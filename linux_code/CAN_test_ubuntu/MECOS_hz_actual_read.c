//
// test program to read back MECOS chopper actual speed via CAN
//
// code derive from inno-maker USB-CAN interface sample code:
// https://github.com/INNO-MAKER/usb2can/blob/master/For%20Linux%20Raspbian%20Ubuntu/software/c/can_send.c
//
// See also kernel documentation of its standard SocketCAN driver:
// https://www.kernel.org/doc/Documentation/networking/can.txt
//
// latest rev by valerix, aug 5 2024
//

#define CAN_DEBUG

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <linux/can.h>
#include <linux/can/raw.h>
#include <errno.h>
#include <sys/time.h>
// Special address description flags for CAN_ID
#define CAN_EFF_FLAG 0x80000000U
#define CAN_RTR_FLAG 0x40000000U
#define CAN_ERR_FLAG 0x20000000U

#define RX_TIMEOUT_SEC 4


unsigned char find_can(const int port)
  {
  char buf[128]={0};
  sprintf(buf,"/sys/class/net/can%d/can_bittiming/bitrate",port);
  return((access(buf,0)==0));
  }

int main(void)
  {
  int ret;
  int s, nbytes, i, setpoint_hz;
  struct timeval tv,tv2;
  double dt;
  struct sockaddr_can addr;
  struct ifreq ifr;
  struct can_frame frame;
  memset(&frame, 0, sizeof(struct can_frame));
  //if(!find_can(0))
  //  {
  //  printf("Can0 device dose not exist!\n ");
  //  return -1;
  //  }

  // must close can device before set baud rate!
  system("sudo ifconfig can0 down");
  //below mean depend on iprout tools ,not ip tool with busybox
  system("sudo ip link set can0 type can bitrate 1000000");
  //system("sudo echo 1000000 > /sys/class/net/can0/can_bittiming/bitrate");
  system("sudo ifconfig can0 up");

  // create socket
  s = socket(PF_CAN, SOCK_RAW, CAN_RAW);
  if(s < 0)
    {
    perror("Create socket PF_CAN failed!");
    return 1;
    }

  // specify can0 device
  strcpy(ifr.ifr_name, "can0");
  ret = ioctl(s, SIOCGIFINDEX, &ifr);
  if(ret < 0)
    {
    perror("ioctl interface index failed!");
    return 1;
    }

  // set receive timeout
  tv.tv_sec = RX_TIMEOUT_SEC;
  tv.tv_usec = 0;
  setsockopt(s, SOL_SOCKET, SO_RCVTIMEO, (const char*)&tv, sizeof tv);

  // bind the socket to can0
  addr.can_family = AF_CAN;
  addr.can_ifindex = ifr.ifr_ifindex;
  ret = bind(s, (struct sockaddr *)&addr, sizeof(addr));
  if(ret < 0)
    {
    perror("bind failed!");
    return 1;
    }

  // setup receive filter rules
  // receive only Ans_MPDO messages from MECOS AMB
  struct can_filter rfilter[1];
  rfilter[0].can_id = 0x2C0;
  rfilter[0].can_mask = CAN_SFF_MASK;
  setsockopt(s, SOL_CAN_RAW, CAN_RAW_FILTER, &rfilter, sizeof(rfilter));
  //setsockopt(s, SOL_CAN_RAW, CAN_RAW_FILTER, NULL, 0);


  // send request to MECOS using a REQ_MPDO message

  // assembly message data
  frame.can_id = 0x340;
  // payload length in byte (0..8)
  frame.can_dlc = 4;
  frame.data[0] = 0xC0;
  frame.data[1] = 0x01;
  frame.data[2] = 0x20;
  frame.data[3] = 0x00;

#ifdef CAN_DEBUG
  printf("Sending request to MECOS via a REQ_MPDO message\n");
  if(!(frame.can_id&CAN_EFF_FLAG))
    printf("Transmit standard frame\n");
  else
    printf("Transmit extended frame\n");
  printf("can_id  = 0x%X\n", frame.can_id);
  printf("can_dlc (payload length) = %d bytes\n", frame.can_dlc);
  for(i = 0; i < frame.can_dlc; i++)
    printf("data[%d] = 0x%02X\n", i, frame.data[i]);
#endif

  // send message out
  nbytes = write(s, &frame, sizeof(frame)); 
  if(nbytes != sizeof(frame))
    {
    perror("Send frame incomplete\r\n");
    system("sudo ifconfig can0 down");
    return 1;
    }

  // now wait for MECOS response via an Ans_MPDO message
  // note that also the CB100 may be on the bus, making different
  // requests to MECOS AMB, so there may be stray Ans_MPDO on the bus
  // keep looking for the right one until we time out
  dt=0;
  gettimeofday(&tv, NULL);
  while(dt<RX_TIMEOUT_SEC)
    {
    errno=0;
    // note that read has a timeout previously set via setsockopt
    nbytes = read(s, &frame, sizeof(frame));
    if((errno==EAGAIN)||(errno==EWOULDBLOCK))
      {
      perror("Timed out");
      break;
      }
    if(nbytes > 0)
      {
#ifdef CAN_DEBUG
      if(!(frame.can_id&CAN_EFF_FLAG))
        printf("Received standard frame\n");
      else
        printf("Received extended frame\n");
      printf("can_id = 0x%X\r\ncan_dlc = %d \r\n", frame.can_id&0x1FFFFFFF, frame.can_dlc);
      for(i = 0; i < frame.can_dlc; i++)
        printf("data[%d] = %02X\r\n", i, frame.data[i]);
#endif
      if( ((frame.can_id&0x1FFFFFFF) == 0x2C0) &&
          (frame.can_dlc >= 6) &&
          (frame.data[0] == 0x40) &&
          (frame.data[1] == 0x01) &&
          (frame.data[2] == 0x20) &&
          (frame.data[3] == 0x00)
        )
        {
        // we received the correct message; now decode speed value
        setpoint_hz=(unsigned int)(frame.data[4])+(unsigned int)(frame.data[5])*256;
        printf("MECOS actual speed: %d Hz\n", setpoint_hz);
        break;
        }      
      }
    
    gettimeofday(&tv2, NULL);
    dt= (tv2.tv_sec+tv2.tv_usec/1.e6) - (tv.tv_sec+tv.tv_usec/1.e6);
    }

  if(dt>=RX_TIMEOUT_SEC)
    {
    perror("Timed out");
    }

  // close the socket and can0
  close(s);
  system("sudo ifconfig can0 down");
  return 0;
  }
