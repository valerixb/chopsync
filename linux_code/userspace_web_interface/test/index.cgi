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
Res_Thr=$( get_parameter UnwrTHR )
Ph_Setpt=$( get_parameter PhSet )
Siggen_Freq=$( get_parameter siggenDFTW )
R_div=$( get_parameter R_div )
N_div=$( get_parameter N_div )



#################################################
#           do something on hardware
#################################################

# read current control word first
ctrlW=$( devmem 0xA0000004 32 )

if [ $Unwr_En = "0" ]; then
    devmem 0xA0000004 32 $(($ctrlW & 0xFE))
elif [ $Unwr_En = "1" ]; then
    devmem 0xA0000004 32 $(($ctrlW | 0x01))
fi

if [ $Unwr_Res = "0" ]; then
    devmem 0xA0000004 32 $(($ctrlW & 0xFD))
elif [ $Unwr_Res = "1" ]; then
    devmem 0xA0000004 32 $(($ctrlW | 0x02))
fi

if [ $Soft_Res = "0" ]; then
    devmem 0xA0000004 32 $(($ctrlW & 0xFB))
elif [ $Soft_Res = "1" ]; then
    devmem 0xA0000004 32 $(($ctrlW | 0x04))
fi

# reset threshold is forced to a positive value
if [ $Res_Thr != "" ]; then
    devmem 0xA0000008 32 $(($Res_Thr>0?$Res_Thr:-$Res_Thr))
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
    devmem 0xA000000C 32 $(($Ph_Setpt))
fi

# siggen frequency is signed 32.0; scale is 2199 counts per Hz
if [ $Siggen_Freq != "" ]; then
    Siggen_Freq=$(( ($Siggen_Freq*2199) & 0xFFFFFFFF ))
    devmem 0xA0000010 32 $(($Siggen_Freq))
fi

# R divider on reference (forced to a positive value)
if [ $R_div != "" ]; then
    devmem 0xA0000024 32 $(($R_div>0?$R_div:-$R_div))
fi

# N divider on VCO (forced to a positive value)
if [ $N_div != "" ]; then
    devmem 0xA0000028 32 $(($N_div>0?$N_div:-$N_div))
fi



#################################################
#           readback values from hardware
#################################################

ctrlW=$( devmem 0xA0000004 32 )
resTHRreadback=$( devmem 0xA0000008 32 )
# phase setpoint is signed 17.0; scale is 8 ns per count
phSetReadback=$( devmem 0xA000000C 32 )
if [ $(($phSetReadback)) -gt 65535 ]; then
    phSetReadback=$(($phSetReadback - 131072))
fi
phSetReadback=$(($phSetReadback*8))
# signal generator deltaFrequency; it's signed 32.0; scale is 2199 cnts = 1 Hz
siggenDF=$( devmem 0xA0000010 32 )
if [ $(($siggenDF)) -gt 2147483647 ]; then
    siggenDF=$(($siggenDF - 4294967296))
fi
siggenDF=$(($siggenDF/2199))

Rdiv=$( devmem 0xA0000024 32 )
Ndiv=$( devmem 0xA0000028 32 )


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
echo -e "                    <H1>FlexPES Chopper Phase Synchronizer</H1>"
#echo -e "                    <H2>Command & Control Panel</H2>"
echo -e "                </td>"
echo -e "            </tr>"
echo -e "        </table>"
echo -e "   </head>"
echo -e "   <body>"

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
echo -e ""
echo -e "        </table>"
echo -e ""
#echo -e "        <br>"
#echo -e "        <br>"
echo -e "        <H3>Synchronizer Readback</H3>"
echo -e ""
echo -e "        <!-- readback values + Lock LEDs-->"
echo -e "        <!-- keep it in a separate frame to enable autoupdate for readback values only -->"
echo -e "        <!-- iframe src=\"readVars.html\" scrolling=no style=\"border:none; height: 220px; width: 600px\" title=\"Readback Values\"></iframe -->"
echo -e "        <iframe src=\"/cgi-bin/readVars.cgi\" scrolling=no style=\"border:none; height: 250px; width: 600px\" title=\"Readback Values\"></iframe>"
echo -e ""
#echo -e "        <br>"

echo -e "   </body>"
echo -e "</html>"







