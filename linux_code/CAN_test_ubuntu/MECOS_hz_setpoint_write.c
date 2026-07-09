//
// test program to change MECOS chopper speed setpoint via CAN
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
// Special address description flags for CAN_ID
#define CAN_EFF_FLAG 0x80000000U
#define CAN_RTR_FLAG 0x40000000U
#define CAN_ERR_FLAG 0x20000000U

unsigned char find_can(const int port)
  {
  char buf[128]={0};
  sprintf(buf,"/sys/class/net/can%d/can_bittiming/bitrate",port);
  return((access(buf,0)==0));
  }

int main(int argc, char** argv)
  {
  int ret;
  int s, nbytes, setpoint_hz;
  struct sockaddr_can addr;
  struct ifreq ifr;
  struct can_frame frame;
  memset(&frame, 0, sizeof(struct can_frame));
  //if(!find_can(0))
  //  {
  //  printf("Can0 device dose not exist!\n ");
  //  return -1;
  //  }

  // get desired chopper speed in Hz
  if(argc<2)
    {
    perror("Please rerun command spcifying desired speed in Hz");
    return 1;
    }
  else
    {
    if(sscanf(argv[1],"%d",&setpoint_hz)<1)
      {
      perror("Invalid speed setpoint (Hz)");
      return 1;
      }
    }

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

  // bind the socket to can0
  addr.can_family = AF_CAN;
  addr.can_ifindex = ifr.ifr_ifindex;
  ret = bind(s, (struct sockaddr *)&addr, sizeof(addr));
  if(ret < 0)
    {
    perror("bind failed!");
    return 1;
    }

  // disable filtering rules: this program only sends a message, without receiving anything
  setsockopt(s, SOL_CAN_RAW, CAN_RAW_FILTER, NULL, 0);

  // assembly message data
  frame.can_id = 0x1C0;
  // payload length in byte (0..8)
  frame.can_dlc = 8;
  frame.data[0] = 0xC0;
  frame.data[1] = 0x00;
  frame.data[2] = 0x20;
  frame.data[3] = 0x00;
  frame.data[4] = (setpoint_hz & 0x00FF);
  frame.data[5] = ((setpoint_hz>>8) & 0x00FF);
  frame.data[6] = 0x00;
  frame.data[7] = 0x00;

#ifdef CAN_DEBUG
  printf("Required setpoint: %d Hz\n",setpoint_hz);
  if(!(frame.can_id&CAN_EFF_FLAG))
    printf("Transmit standard frame\n");
  else
    printf("Transmit extended frame\n");
  printf("can_id  = 0x%X\n", frame.can_id);
  printf("can_dlc (payload length) = %d bytes\n", frame.can_dlc);
  int i = 0;
  for(i = 0; i < frame.can_dlc; i++)
    printf("data[%d] = 0x%02X\n", i, frame.data[i]);
#endif

  // send message out
  nbytes = write(s, &frame, sizeof(frame)); 
  if(nbytes != sizeof(frame))
    {
    printf("Send  frame incompletely!\r\n");
    system("sudo ifconfig can0 down");
    }

  // close the socket and can0
  close(s);
  system("sudo ifconfig can0 down");
  return 0;
  }
