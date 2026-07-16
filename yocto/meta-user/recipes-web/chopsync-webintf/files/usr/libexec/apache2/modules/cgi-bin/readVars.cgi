#!/bin/bash

# remember: no blanks before or after = , otherwise labels are interpreted as commands instead of variables

#################################################
#           readback values from hardware
#################################################

statusW=$( devmem 0x80030000 32 )
accelCMD=$( devmem 0x80030014 32 )
# accel CMD is signed 22.0
if [ $(($accelCMD)) -gt 2097151 ]; then
    accelCMD=$(($accelCMD - 4194304))
fi

phERR=$( devmem 0x80030018 32 )
# phase error is signed 24.7 ; scale is 8 ns
if [ $(($phERR)) -gt 8388607 ]; then
    phERR=$(($phERR - 16777216))
fi
#phERR=$(($phERR*8/128))
phERR=$( printf "%d" $phERR | awk '{printf("%+.3f",$1*8/128 )}' )

REFfreq=$( devmem 0x8003001C 32 )
VCOfreq=$( devmem 0x80030020 32 )

Rdiv=$( devmem 0x80030024 32 )
Ndiv=$( devmem 0x80030028 32 )


##############################################################
#      send appropriate HTML back to requesting client
##############################################################


# CAREFUL!! the line with "Content-type and the subsequent blank line ARE NECESSARY, otherwise the page will not load
echo -e "Content-type: text/html"
echo ""

# ----------------------------------------

echo -e "<!DOCTYPE html>"
echo -e "<html>"
echo -e "   <head>"
echo -e "    <link rel=\"stylesheet\" href=\"/LEDstyle.css\">"
echo -e "    <meta http-equiv=\"refresh\" content=\"1\" >"
echo -e "   </head>"
echo -e "   <body>"
echo -e "        "
echo -e "        <!-- readback values -->"
echo -e "        <table>"
echo -e "            <tr>"
echo -e "                <td>Acceleration Command:</td>"

echo -en "                <td align=\"right\">"
printf "%+d" $(($accelCMD))
echo -e "</td>"

echo -e "                <td>pulses</td>"
echo -e "            </tr>"
echo -e ""
echo -e "            <tr>"
echo -e "                <td>Phase Error:</td>"

echo -en "                <td align=\"right\">"
#printf "%d" $(($phERR))
printf "%+.0f" $phERR
#echo $phERR

echo -e "</td>"

echo -e "                <td>ns</td>"
echo -e "            </tr>"
echo -e "            "
echo -e "            <tr>"
echo -e "                <td>REF Frequency:</td>"

echo -en "                <td align=\"right\">"
printf "%d" $(($REFfreq))
echo -e "</td>"

echo -e "                <td>Hz</td>"
echo -e "            </tr>"
echo -e "            "

echo -e "            <tr>"
echo -e "                <td>CHOPPER Frequency:</td>"

echo -en "                <td align=\"right\">"
printf "%d" $(($VCOfreq))
echo -e "</td>"

echo -e "                <td>Hz</td>"
echo -e "            </tr>"

echo -e "            <tr>"
echo -e "                <td> <br> </td> "
echo -e "            </tr>"

echo -e "            <tr>"
echo -en "                <td>REF/"
printf "%d" $(($Rdiv))
echo -e ":</td>"
echo -en "                <td align=\"right\">"
#printf "%.3f" $(($REFfreq/$Rdiv))
printf "%d %d" $REFfreq $Rdiv | awk '{printf("%.3f",$1/$2 )}'
echo -e "</td>"
echo -e "                <td>Hz</td>"
echo -e "            </tr>"

echo -e "            <tr>"
echo -en "                <td>CHOPPER/"
printf "%d" $(($Ndiv))
echo -e ":</td>"
echo -en "                <td align=\"right\">"
#printf "%.3f" $(($VCOfreq/$Ndiv))
printf "%d %d" $VCOfreq $Ndiv | awk '{printf("%.3f",$1/$2 )}'
echo -e "</td>"
echo -e "                <td>Hz</td>"
echo -e "            </tr>"

echo -e "        </table>"
echo -e ""
echo -e "        <br>"
echo -e "        "
echo -e "        <!-- Lock LEDs -->"
echo -e "        <table>"
echo -e "            <tr>"
echo -e "                <td>Frequency Lock</td>"

echo -en "                <td><span class=\""
if ! [  $(($statusW & 0x01)) -eq 0 ]; then
    echo -en "greendot"
else
    echo -en "greydot"
fi
echo -e "\"></span></td>"

echo -e "            </tr>"
echo -e ""
echo -e "            <tr>"
echo -e "                <td>Phase Lock</td>"

echo -en "                <td><span class=\""
if ! [ $(($statusW & 0x02)) -eq 0 ]; then
    echo -en "greendot"
else
    echo -en "greydot"
fi
echo -e "\"></span></td>"

echo -e "            </tr>"

echo -e "            <tr>"
echo -e "                <td>Phase Lock Loss Alarm (sticky)</td>"

echo -en "                <td><span class=\""
if ! [ $(($statusW & 0x020)) -eq 0 ]; then
    echo -en "reddot"
else
    echo -en "greydot"
fi
echo -e "\"></span></td>"

echo -e "            </tr>"
echo -e "        </table>"
echo -e "        <br>"

if ! [ $(($statusW & 0x020)) -eq 0 ]; then
    if ! [ -f "lockloss.txt" ]; then
        # if "lockloss.txt" file does not exist, then it's the first lock loss event: save its date/time
        date >| "lockloss.txt"
    fi
    echo -e "First Lock Loss event occurred on "
    cat "lockloss.txt"
    echo -e "        <br>"
    echo -e "Current time is "
    date
    echo -e "        <br>"
else
    rm "lockloss.txt"
fi

echo -e ""
echo -e "        <br>"
echo -e "        <br>"
echo -e ""
echo -e "   </body>"
echo -e "</html>"



