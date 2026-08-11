#!/bin/bash

# remember: no blanks before or after = , otherwise labels are interpreted as commands instead of variables

function get_parameter ()
    {
    echo "$query" | tr '&' '\n' | grep "^$1=" | head -1 \
    | sed "s/.*=//"
    }


if [ "$REQUEST_METHOD" = POST ]; then
    query=$( head --bytes="$CONTENT_LENGTH")
else
    query="$QUERY_STRING"
fi

Unwr_En=$( get_parameter UnwrEN )
Unwr_Res=$( get_parameter UnwrRES )
Soft_Res=$( get_parameter PHctrlrRES )
Lock_Alarm_Res=$( get_parameter lock_loss_res )
Res_Thr=$( get_parameter UnwrTHR )
Ph_Setpt=$( get_parameter PhSet )
Siggen_Freq=$( get_parameter siggenDFTW )
R_div=$( get_parameter R_div )
N_div=$( get_parameter N_div )
TRIG_ph=$( get_parameter TRIG_ph )
Extra_G=$( get_parameter extraGain )

DEVMEM="/usr/libexec/apache2/modules/cgi-bin/devmem"

#################################################
#           do something on hardware
#################################################

# read current control word before modigying it
ctrlW=$( $DEVMEM 0x80030004 32 )
if [ $Unwr_En = "0" ]; then
    $DEVMEM 0x80030004 32 $(($ctrlW & 0xFE))
elif [ $Unwr_En = "1" ]; then
    $DEVMEM 0x80030004 32 $(($ctrlW | 0x01))
fi

ctrlW=$( $DEVMEM 0x80030004 32 )
if [ $Unwr_Res = "0" ]; then
    $DEVMEM 0x80030004 32 $(($ctrlW & 0xFD))
elif [ $Unwr_Res = "1" ]; then
    $DEVMEM 0x80030004 32 $(($ctrlW | 0x02))
fi

ctrlW=$( $DEVMEM 0x80030004 32 )
AlarmAutoReset="0"
if [ $Soft_Res = "0" ]; then
    $DEVMEM 0x80030004 32 $(($ctrlW & 0xFB))
    # if we are eanbling the controller, force a reset of alarms
    AlarmAutoReset="1"
elif [ $Soft_Res = "1" ]; then
    $DEVMEM 0x80030004 32 $(($ctrlW | 0x04))
fi

ctrlW=$( $DEVMEM 0x80030004 32 )
if [ $Lock_Alarm_Res = "reset" ]; then
    $DEVMEM 0x80030004 32 $(($ctrlW | 0x08))
fi

# reset threshold is forced to a positive value
if [ $Res_Thr != "" ]; then
    $DEVMEM 0x80030008 32 $(($Res_Thr>0?$Res_Thr:-$Res_Thr))
fi

# phase setpoint is signed 17.0; scale is 8 ns per count
# limit to [-10us, +10us]
if [ $(($Ph_Setpt)) -gt 10000 ]; then
    Ph_Setpt=10000
elif [ $(($Ph_Setpt)) -lt -10000 ]; then
    Ph_Setpt=-10000
fi

if [ $Ph_Setpt != "" ]; then
    Ph_Setpt=$(( ($Ph_Setpt/8) & 0x01FFFF ))
    # the previous "bitwise &" takes into account the sign; no need to check again
    #if [ $Ph_Setpt -lt 0 ]; then
    #    Ph_Setpt=$(($Ph_Setpt+131072))
    #fi
    $DEVMEM 0x8003000C 32 $(($Ph_Setpt))
fi

# siggen frequency is signed 32.0; scale is 2199 counts per Hz
if [ $Siggen_Freq != "" ]; then
    Siggen_Freq=$(( ($Siggen_Freq*2199) & 0xFFFFFFFF ))
    $DEVMEM 0x80030010 32 $(($Siggen_Freq))
fi

# R divider on reference (forced to a positive value)
if [ $R_div != "" ]; then
    $DEVMEM 0x80030024 32 $(($R_div>0?$R_div:-$R_div))
fi

# N divider on VCO (forced to a positive value)
if [ $N_div != "" ]; then
    $DEVMEM 0x80030028 32 $(($N_div>0?$N_div:-$N_div))
fi

# TRIG OUT phase, forced to a positive value
# it will be later forced into range [1,R]
if [ $TRIG_ph != "" ]; then
    $DEVMEM 0x80030030 32 $(($TRIG_ph>0?$TRIG_ph:-$TRIG_ph))
fi

# Extra Loop Gain is unsigned 16.12
if [ $Extra_G != "" ]; then
    # need awk for floating point
    Extra_G=$( awk '{printf("%d",$1*$2)}' <<<"  $Extra_G  4096 " )
    Extra_G=$(( ($Extra_G>0?$Extra_G:-$Extra_G) & 0xFFFF ))
    $DEVMEM 0x8003002C 32 $(($Extra_G))
fi



#################################################
#           readback values from hardware
#################################################

ctrlW=$( $DEVMEM 0x80030004 32 )
resTHRreadback=$( $DEVMEM 0x80030008 32 )
# phase setpoint is signed 17.0; scale is 8 ns per count
phSetReadback=$( $DEVMEM 0x8003000C 32 )
if [ $(($phSetReadback)) -gt 65535 ]; then
    phSetReadback=$(($phSetReadback - 131072))
fi
phSetReadback=$(($phSetReadback*8))
# signal generator deltaFrequency; it's signed 32.0; scale is 2199 cnts = 1 Hz
siggenDF=$( $DEVMEM 0x80030010 32 )
if [ $(($siggenDF)) -gt 2147483647 ]; then
    siggenDF=$(($siggenDF - 4294967296))
fi
siggenDF=$(($siggenDF/2199))

Rdiv=$( $DEVMEM 0x80030024 32 )
Ndiv=$( $DEVMEM 0x80030028 32 )
TRIGph=$( $DEVMEM 0x80030030 32 )

# force TRIG OUT phase into range [1,R]
TRIGph=$(($TRIGph>1?$TRIGph:1))
TRIGph=$(($TRIGph<$Rdiv?$TRIGph:$Rdiv))
$DEVMEM 0x80030030 32 $(($TRIGph))

# extra loop gain is unsigned 16.12
extra_Gain=$( $DEVMEM 0x8003002C 32 )
# convert to decimal
extra_Gain=$( printf "%d" $extra_Gain )
# must use awk for floating point
extra_Gain=$( awk '{printf("%.3f",$1/$2)}' <<<"  $extra_Gain  4096 " )


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
echo -e "        <table>"
echo -e "            <tr>"
echo -e "                <td><img src=\"MAX-IV_logo1_rgb-300x104.png\" alt=\"MaxIV Laboratory\"></td>"
echo -e "                <td>"
echo -e "                    <H1>Max IV Chopper Phase Synchronizer</H1>"
#echo -e "                    <H2>Command & Control Panel</H2>"
echo -e "                </td>"
echo -e "            </tr>"
echo -e "        </table>"
echo -e "   </head>"
echo -e "   <body>"

echo -e "This web page is about MaxIV chopper synchronizer;<br>"
echo -e "if you want to control MECOS Active Magnetic Bearing, please use "
echo -e "<a href="/cgi-bin/mecosCtrl.cgi">this web page</a>"
echo -e "<br>"

#debug
#printf "Query: >%s<\n" $query
#echo -e "      <br>"
#echo -e "      <br>"
#printf "Unwrap: >%s<\n" $Unwr_En
#echo -e "      <br>"
#printf "UnwrRes: >%s<\n" $Unwr_Res
#echo -e "      <br>"
#printf "SoftRes: >%s<\n" $Soft_Res
#echo -e "      <br>"
#printf "ResThr: >%s<\n" $Res_Thr
#echo -e "      <br>"
#printf "Phase Setpoint: >%s<\n" $Ph_Setpt
#echo -e "      <br>"
#printf "Siggen Freq: >%s<\n" $Siggen_Freq
#echo -e "      <br>"


echo -e "        <!-- input fields -->"

echo -e "        <table>"
echo -e "            <tr>"
echo -e "                <td colspan=\"2\"> <H3>Synchronizer Control</H3> </td>"
echo -e "            </tr>"

echo -e "            <tr>"
echo -e "                <td>Synchronizer ON/OFF:</td>"
echo -e "                <td>"
echo -e "                    <form action=\"\" method=\"GET\" >"
echo -e "                        <select name=\"PHctrlrRES\" id = \"PHctrlrRES\" onchange=\"javascript:this.form.submit()\">"

echo -en "                            <option value = \"0\""
if [  $(($ctrlW & 0x04)) -eq 0 ]; then
    echo -en " selected=\"selected\""
fi
echo -e ">ON</option>"

echo -en "                            <option value = \"1\""
if ! [  $(($ctrlW & 0x04)) -eq 0 ]; then
    echo -en " selected=\"selected\""
fi
echo -e ">OFF</option>"

echo -e "                        </select>"
echo -e "                    </form>"
echo -e "                </td>"
echo -e "            </tr>"

echo -e ""
echo -e "            <tr>"
echo -e "                <td>Phase Setpoint:</td>"
echo -e "                <td>"
echo -e "                    <form action=\"\" method=\"GET\" >"

echo -en "                        <input type=\"number\" name=\"PhSet\" id=\"PhSet\" value="
#printf "%.3f" $(($phSetReadback))
printf "%d" $(($phSetReadback))
echo -e " min=\"-10000\" max=\"10000\" step=8 onchange=\"javascript:this.form.submit()\">"

echo -e "                        ns"
echo -e "                    </form>"
echo -e "                </td>"
echo -e "            </tr>"
echo -e ""

# lock loss alarm reset button
echo -e "            <tr>"
echo -e "                <td>"
echo -e "                    <form action=\"\" method=\"GET\" id=\"lock_loss_res\">"
echo -e "                        <button id=\"lock_loss_res_btn\" name=\"lock_loss_res\" type=\"submit\" form=\"lock_loss_res\" value=\"reset\">Reset Lock Loss Alarm</button>"
echo -e "                    </form>"
echo -e "                </td>"
echo -e "            </tr>"


echo -e "            <tr>"
echo -e "                <td colspan=\"2\"> <H3>Prescalers</H3> </td>"
echo -e "            </tr>"


echo -e "            <tr>"
echo -e "                <td>REF Frequency Prescaler Factor:</td>"
echo -e "                <td>"
echo -e "                    <form action=\"\" method=\"GET\" >"

echo -en "                        <input type=\"number\" name=\"R_div\" id=\"R_div\" min=\"0\" value="
printf "%d" $(($Rdiv))
echo -e " onchange=\"javascript:this.form.submit()\">"

echo -e ""
echo -e "                    </form>"
echo -e "                </td>"
echo -e "            </tr>"
echo -e ""
echo -e "            <tr>"
echo -e "                <td>CHOPPER Frequency Prescaler Factor:</td>"
echo -e "                <td>"
echo -e "                    <form action=\"\" method=\"GET\" >"

echo -en "                        <input type=\"number\" name=\"N_div\" id=\"N_div\" min=\"0\" value="
printf "%d" $(($Ndiv))
echo -e " onchange=\"javascript:this.form.submit()\">"

echo -e ""
echo -e "                    </form>"
echo -e "                </td>"
echo -e "            </tr>"
echo -e ""
echo -e "            <tr>"
echo -e "                <td>TRIGGER OUT phase delay (in range 1 to" 
printf "%d" $(($Rdiv))
echo -e ") :</td>"
echo -e "                <td>"
echo -e "                    <form action=\"\" method=\"GET\" >"

echo -en "                        <input type=\"number\" name=\"TRIG_ph\" id=\"TRIG_ph\" min=\"1\" max="
printf "%d" $(($Rdiv))
echo -en " value="
printf "%d" $(($TRIGph))
echo -e " onchange=\"javascript:this.form.submit()\">"


echo -e ""
echo -e "                    </form>"
echo -e "                </td>"
echo -e "            </tr>"


echo -e "            <tr>"
echo -e "                <td colspan=\"2\"> <H3>Advanced Synchronizer Configuration</H3> </td>"
echo -e "            </tr>"


echo -e "            <tr>"
echo -e "                <td>Unwrapper:</td>"
echo -e "                <td>"
echo -e "                    <form action=\"\" method=\"GET\" >"
echo -e "                        <select name=\"UnwrEN\" id = \"UnwrEN\" onchange=\"javascript:this.form.submit()\">"

echo -en "                            <option value = \"0\""
if [  $(($ctrlW & 0x01)) -eq 0 ]; then
    echo -en " selected=\"selected\""
fi
echo -e ">DISABLED</option>"

echo -en "                            <option value = \"1\""
if ! [  $(($ctrlW & 0x01)) -eq 0 ]; then
    echo -en " selected=\"selected\""
fi
echo -e ">ENABLED</option>"

echo -e "                        </select>"
echo -e "                    </form>"
echo -e "                </td>"
echo -e "            </tr>"
echo -e ""
echo -e "            <tr>"
echo -e "                <td>Unwrapper Reset:</td>"
echo -e "                <td>"
echo -e "                    <form action=\"\" method=\"GET\" >"
echo -e "                        <select name=\"UnwrRES\" id = \"UnwrRES\" onchange=\"javascript:this.form.submit()\">"

echo -en "                            <option value = \"0\""
if [  $(($ctrlW & 0x02)) -eq 0 ]; then
    echo -en " selected=\"selected\""
fi
echo -e ">DISABLED</option>"

echo -en "                            <option value = \"1\""
if ! [  $(($ctrlW & 0x02)) -eq 0 ]; then
    echo -en " selected=\"selected\""
fi
echo -e ">ENABLED</option>"

echo -e "                        </select>"
echo -e "                    </form>"
echo -e "                </td>"
echo -e "            </tr>"
echo -e ""
echo -e ""
echo -e "            <tr>"
echo -e "                <td>Unwrapper Reset Threshold:</td>"
echo -e "                <td>"
echo -e "                    <form action=\"\" method=\"GET\" >"

echo -en "                        <input type=\"number\" name=\"UnwrTHR\" id=\"UnwrTHR\" min=\"0\" value="
printf "%d" $(($resTHRreadback))
echo -e " onchange=\"javascript:this.form.submit()\">"

echo -e "                        cnts"
echo -e "                    </form>"
echo -e "                </td>"
echo -e "            </tr>"
echo -e ""
echo -e "            <tr>"
echo -e "                <td>Diagnostic Signal Generator Freq: 3'123'437.5 +</td>"
echo -e "                <td>"
echo -e "                    <form action=\"\" method=\"GET\" >"

echo -en "                        <input type=\"number\" name=\"siggenDFTW\" id=\"siggenDFTW\" value="
printf "%d" $(($siggenDF))
echo -e " onchange=\"javascript:this.form.submit()\">"

echo -e "                        Hz"
echo -e "                    </form>"
echo -e "                </td>"
echo -e "            </tr>"
echo -e ""
echo -e "            <tr>"
echo -e "                <td>Control Loop Extra Gain (default=4; hi-perf=6):</td>"
echo -e "                <td>"
echo -e "                    <form action=\"\" method=\"GET\" >"

echo -en "                        <input type=\"number\" name=\"extraGain\" id=\"extraGain\" value="
printf "%s" $extra_Gain
echo -e " step=0.5 onchange=\"javascript:this.form.submit()\">"

echo -e "                    </form>"
echo -e "                </td>"
echo -e "            </tr>"
echo -e ""
echo -e ""
echo -e "        </table>"
echo -e ""
#echo -e "        <br>"
# if an automatic alarm reset is requested, programmatically click the relevant button:
if [ $AlarmAutoReset = "1" ]; then
echo -e "         <script>"
echo -e "         document.getElementById('lock_loss_res_btn').click();"
echo -e "         </script>"
fi

#echo -e "        <br>"
echo -e "        <H3>Synchronizer Readback</H3>"
echo -e ""
echo -e "        <!-- readback values + Lock LEDs-->"
echo -e "        <!-- keep it in a separate frame to enable autoupdate for readback values only -->"
echo -e "        <!-- iframe src=\"readVars.html\" scrolling=no style=\"border:none; height: 220px; width: 600px\" title=\"Readback Values\"></iframe -->"
echo -e "        <iframe src=\"/cgi-bin/readVars.cgi\" scrolling=no style=\"border:none; height: 350px; width: 600px\" title=\"Readback Values\"></iframe>"
echo -e ""
#echo -e "        <br>"

echo -e "   </body>"
echo -e "</html>"







