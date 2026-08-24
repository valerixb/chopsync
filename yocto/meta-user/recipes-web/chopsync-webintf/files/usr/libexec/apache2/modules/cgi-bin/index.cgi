#!/usr/bin/python

import socket
#import select
import os
import urllib.parse
#import time
#from datetime import datetime
#import numpy as np
#import matplotlib.pyplot as plt
#import io
#import base64
#import fnmatch

# constants


# defaults

# --------------------  open html page right away, so we can print errors on it -----------------------

print('Content-type:text/html\r\n\r\n')
print('<!DOCTYPE html>')
print('<html>')
print('<head>')
print('')
print('  <table>')
print('    <tr>')
print('      <td> <a href="/cgi-bin/index.cgi"> <img src="/MAX-IV_logo1_rgb-300x104.png" alt="MaxIV Laboratory"> </a> </td>')
print('      <td>')
print('      <H1>Max IV Chopper Phase Synchronizer</H1>')
print('      <H2>Command & Control Panel</H2>')
print('      </td>')
print('    </tr>')
print('  </table>')
print('</head>')
print('<body>')

print('This web page is about MaxIV chopper synchronizer;<br>')
print('if you want to control MECOS Active Magnetic Bearing, please use ')
print('<a href="/cgi-bin/mecosCtrl.cgi">this web page</a>')
print('<br>')


# --------- open a connection to r5ctrlr SCPI server ----------

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 8888))
#s.connect(("192.168.0.17", 8888))




# ------------------  do the changes requested by the GET form query string  --------------------

# the query string of the GET form
# is passed to cgi scripts as the environment
# variable QUERY_STRING
query_string = os.environ['QUERY_STRING']
#query_string = ''
# convert the query string to a dictionary
arguments = urllib.parse.parse_qs(query_string)

# ---------  check the fields of the GET form query string ----
# ---------            and act accordingly                 ----

for name in arguments.keys():
  
  # -------- sync ON/OFF
  if name=='sync_on':
    if int(arguments[name][0])==1:
      cmd_s='SYNCHRONIZER ON\n'
      sync_ONOFF=True
    else:
      cmd_s='SYNCHRONIZER OFF\n'
      sync_ONOFF=False
    s.sendall(cmd_s.encode('ascii')) 
    ans=(s.recv(1024)).decode('utf-8')
    tok=ans.split(" ",2)
    if tok[0].strip()=='ERR:':
      print('<br>Error commanding the global ON/OFF state<br>')

  # -------- phase setpoint (may be negative)
  elif name=='PhSet':
    phsetpoint=int(arguments[name][0])
    cmd_s='PHSETPOINT_NS '+str(phsetpoint)+'\n'
    s.sendall(cmd_s.encode('ascii')) 
    ans=(s.recv(1024)).decode('utf-8')
    tok=ans.split(" ",2)
    if tok[0].strip()=='ERR:':
      print('<br>Error commanding the phase setpoint<br>')
    
  # -------- sticky lock loss alarm reset
  elif name=='lock_loss_res':
    if arguments[name][0]=="reset":
      cmd_s='STICKYLOL OFF\n'
      s.sendall(cmd_s.encode('ascii')) 
      ans=(s.recv(1024)).decode('utf-8')
      tok=ans.split(" ",2)
      if tok[0].strip()=='ERR:':
        print('<br>Error resetting sticky lock of loss flag<br>')

  # -------- bunch marker prescaler
  elif name=='R_div':
    R_div=int(arguments[name][0])
    R_div=max(1,abs(R_div))
    cmd_s='BUNCHMARKER_PRESCALER '+str(R_div)+'\n'
    s.sendall(cmd_s.encode('ascii')) 
    ans=(s.recv(1024)).decode('utf-8')
    tok=ans.split(" ",2)
    if tok[0].strip()=='ERR:':
      print('<br>Error commanding the bunch marker prescaler<br>')

  # -------- chopper prescaler
  elif name=='N_div':
    N_div=int(arguments[name][0])
    N_div=max(1,abs(N_div))
    cmd_s='CHOPPER_PRESCALER '+str(N_div)+'\n'
    s.sendall(cmd_s.encode('ascii')) 
    ans=(s.recv(1024)).decode('utf-8')
    tok=ans.split(" ",2)
    if tok[0].strip()=='ERR:':
      print('<br>Error commanding the chopper prescaler<br>')

  # -------- TRIG OUT phase
  elif name=='TRIG_ph':
    TRIG_ph=int(arguments[name][0])
    TRIG_ph=max(1,abs(TRIG_ph))
    cmd_s='TRIGOUT_PH '+str(TRIG_ph)+'\n'
    s.sendall(cmd_s.encode('ascii')) 
    ans=(s.recv(1024)).decode('utf-8')
    tok=ans.split(" ",2)
    if tok[0].strip()=='ERR:':
      print('<br>Error commanding the TRIG OUT phase<br>')

  # -------- unwrapper ON/OFF
  elif name=='UnwrEN':
    if int(arguments[name][0])==1:
      cmd_s='UNWRAPPER ON\n'
      Unwr_EN=True
    else:
      cmd_s='UNWRAPPER OFF\n'
      Unwr_EN=False
    s.sendall(cmd_s.encode('ascii')) 
    ans=(s.recv(1024)).decode('utf-8')
    tok=ans.split(" ",2)
    if tok[0].strip()=='ERR:':
      print('<br>Error commanding the unwrapper state<br>')

  # -------- unwrapper reset ON/OFF
  elif name=='UnwrRES':
    if int(arguments[name][0])==1:
      cmd_s='UNW_RES ON\n'
      Unwr_RES=True
    else:
      cmd_s='UNW_RES OFF\n'
      Unwr_RES=False
    s.sendall(cmd_s.encode('ascii')) 
    ans=(s.recv(1024)).decode('utf-8')
    tok=ans.split(" ",2)
    if tok[0].strip()=='ERR:':
      print('<br>Error commanding the unwrapper reset state<br>')

  # -------- unwrapper threshold
  elif name=='UnwrTHR':
    Res_Thr=int(arguments[name][0])
    Res_Thr=abs(Res_Thr)
    cmd_s='UNW_THR '+str(Res_Thr)+'\n'
    s.sendall(cmd_s.encode('ascii')) 
    ans=(s.recv(1024)).decode('utf-8')
    tok=ans.split(" ",2)
    if tok[0].strip()=='ERR:':
      print('<br>Error commanding the unwrapper reset threshold<br>')

  # -------- SIGGEN deltaFTW
  elif name=='siggenDFTW':
    Siggen_DF=float(arguments[name][0])
    cmd_s='SIGGEN_DF_HZ '+str(Siggen_DF)+'\n'
    s.sendall(cmd_s.encode('ascii')) 
    ans=(s.recv(1024)).decode('utf-8')
    tok=ans.split(" ",2)
    if tok[0].strip()=='ERR:':
      print('<br>Error commanding signal generator deltaFTW<br>')

  # -------- extra Gain
  elif name=='extraGain':
    extraG=float(arguments[name][0])
    cmd_s='GAIN '+str(extraG)+'\n'
    s.sendall(cmd_s.encode('ascii')) 
    ans=(s.recv(1024)).decode('utf-8')
    tok=ans.split(" ",2)
    if tok[0].strip()=='ERR:':
      print('<br>Error commanding extra gain<br>')




  
# ------------------  get current config  --------------------

# -------- sync ON/OFF
qstr='SYNCHRONIZER?\n'
s.sendall(bytes(qstr,encoding='ascii')) 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
if(tok[0].strip()=="OK:"):
  if(tok[1].strip())=="ON":
    sync_ONOFF=True
  else:
    sync_ONOFF=False
else:
  # use default in case of error, but issue a message
  print('<br>Error querying the global ON/OFF state<br>')
  sync_ONOFF=False

# -------- phase setpoint (may be negative)
qstr='PHSETPOINT_NS?\n'
s.sendall(bytes(qstr,encoding='ascii')) 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
if(tok[0].strip()=="OK:"):
  phsetpoint=int(tok[1].strip())
else:
  # use default in case of error, but issue a message
  print('<br>Error querying the phase setpoint<br>')
  phsetpoint=128

# -------- bunch marker prescaler
qstr='BUNCHMARKER_PRESCALER?\n'
s.sendall(bytes(qstr,encoding='ascii')) 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
if(tok[0].strip()=="OK:"):
  R_div=int(tok[1].strip())
else:
  # use default in case of error, but issue a message
  print('<br>Error querying the bunch marker prescaler<br>')
  R_div=33

# -------- chopper prescaler
qstr='CHOPPER_PRESCALER?\n'
s.sendall(bytes(qstr,encoding='ascii')) 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
if(tok[0].strip()=="OK:"):
  N_div=int(tok[1].strip())
else:
  # use default in case of error, but issue a message
  print('<br>Error querying the chopper prescaler<br>')
  N_div=1

# -------- TRIG OUT phase
qstr='TRIGOUT_ph?\n'
s.sendall(bytes(qstr,encoding='ascii')) 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
if(tok[0].strip()=="OK:"):
  TRIG_ph=int(tok[1].strip())
else:
  # use default in case of error, but issue a message
  print('<br>Error querying the TRIG OUT phase<br>')
  TRIG_ph=1

# -------- unwrapper ON/OFF
qstr='UNWRAPPER?\n'
s.sendall(bytes(qstr,encoding='ascii')) 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
if(tok[0].strip()=="OK:"):
  if(tok[1].strip())=="ON":
    Unwr_EN=True
  else:
    Unwr_EN=False
else:
  # use default in case of error, but issue a message
  print('<br>Error querying unwrapper state<br>')
  Unwr_EN=True

# -------- unwrapper reset ON/OFF
qstr='UNW_RES?\n'
s.sendall(bytes(qstr,encoding='ascii')) 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
if(tok[0].strip()=="OK:"):
  if(tok[1].strip())=="ON":
    Unwr_RES=True
  else:
    Unwr_RES=False
else:
  # use default in case of error, but issue a message
  print('<br>Error querying unwrapper reset state<br>')
  Unwr_RES=True

# -------- unwrapper threshold
qstr='UNW_THR?\n'
s.sendall(bytes(qstr,encoding='ascii')) 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
if(tok[0].strip()=="OK:"):
  Res_Thr=int(tok[1].strip())
else:
  # use default in case of error, but issue a message
  print('<br>Error querying the unwrapper reset threshold<br>')
  Res_Thr=10

# -------- SIGGEN deltaFTW
qstr='SIGGEN_DF_HZ?\n'
s.sendall(bytes(qstr,encoding='ascii')) 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
if(tok[0].strip()=="OK:"):
  Siggen_DF=float(tok[1].strip())
else:
  # use default in case of error, but issue a message
  print('<br>Error querying the signal generator deltaFTW<br>')
  Siggen_DF=0.0

# -------- extra Gain
qstr='GAIN?\n'
s.sendall(bytes(qstr,encoding='ascii')) 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
if(tok[0].strip()=="OK:"):
  extraG=float(tok[1].strip())
else:
  # use default in case of error, but issue a message
  print('<br>Error querying the extra Gain<br>')
  extraG=6.0





# --------------------  now display body of html page  -----------------------

print('  <table>')

# -------- Synchronizer Control

print('    <tr>')
print('      <td colspan=\"2\"> <H3>Synchronizer Control</H3> </td>')
print('    </tr>')

print('    <tr>')
print('      <td>Synchronizer ON/OFF:</td>')
print('      <td>')
print('        <form action="" method="GET" >')
print('          <select name="sync_on" id = "sync_on" onchange="javascript:this.form.submit()">')
print('            <option value = "0"')
if not sync_ONOFF:
  print(' selected="selected"')
print('>OFF</option>')
print('            <option value = "1"')
if sync_ONOFF:
  print(' selected="selected"')
print('>ON</option>')

print('          </select>')
print('        </form>')
print('      </td>')
print('    </tr>')

print('')

print('    <tr>')
print('      <td>Phase Setpoint:</td>')
print('      <td>')
print('        <form action="" method="GET" >')
print(f'          <input type="number" name="PhSet" id="PhSet" value="{phsetpoint}" min="-10000" max="10000" step=8 onchange="javascript:this.form.submit()">')
print('           ns')
print('        </form>')
print('      </td>')
print('    </tr>')

print('')

# lock loss alarm reset button
print('    <tr>')
print('      <td>')
print('        <form action="" method="GET" id="lock_loss_res">')
print('          <button id="lock_loss_res_btn" name="lock_loss_res" type="submit" form="lock_loss_res" value="reset">Reset Lock Loss Alarm</button>')
print('        </form>')
print('      </td>')
print('    </tr>')


# -------- Prescalers

print('    <tr>')
print('      <td colspan=\"2\"> <H3>Prescalers</H3> </td>')
print('    </tr>')

print('')

print('    <tr>')
print('      <td>Bunch Marker prescaler:</td>')
print('      <td>')
print('        <form action="" method="GET" >')
print(f'          <input type="number" name="R_div" id="R_div" value="{R_div}" min="1" onchange="javascript:this.form.submit()">')
print('        </form>')
print('      </td>')
print('    </tr>')

print('')

print('    <tr>')
print('      <td>Chopper prescaler:</td>')
print('      <td>')
print('        <form action="" method="GET" >')
print(f'          <input type="number" name="N_div" id="N_div" value="{N_div}" min="1" onchange="javascript:this.form.submit()">')
print('        </form>')
print('      </td>')
print('    </tr>')

print('')

print('    <tr>')
print(f'      <td>TRIGGER OUT phase delay (in range 1 to {R_div}):</td>')
print('      <td>')
print('        <form action="" method="GET" >')
print(f'          <input type="number" name="TRIG_ph" id="TRIG_ph" value="{TRIG_ph}" min="1" max="{R_div}" onchange="javascript:this.form.submit()">')
print('        </form>')
print('      </td>')
print('    </tr>')

print('')

# -------- Advanced Setup

print('    <tr>')
print('      <td colspan=\"2\"> <H3>Advanced Synchronizer Configuration</H3> </td>')
print('    </tr>')

print('')

print('    <tr>')
print('      <td>Unwrapper:</td>')
print('      <td>')
print('        <form action="" method="GET" >')
print('          <select name="UnwrEN" id = "UnwrEN" onchange="javascript:this.form.submit()">')
print('            <option value = "0"')
if not Unwr_EN:
  print(' selected="selected"')
print('>DISABLED</option>')
print('            <option value = "1"')
if Unwr_EN:
  print(' selected="selected"')
print('>ENABLED</option>')

print('          </select>')
print('        </form>')
print('      </td>')
print('    </tr>')

print('')

print('    <tr>')
print('      <td>Unwrapper Reset:</td>')
print('      <td>')
print('        <form action="" method="GET" >')
print('          <select name="UnwrRES" id = "UnwrRES" onchange="javascript:this.form.submit()">')
print('            <option value = "0"')
if not Unwr_RES:
  print(' selected="selected"')
print('>DISABLED</option>')
print('            <option value = "1"')
if Unwr_RES:
  print(' selected="selected"')
print('>ENABLED</option>')

print('          </select>')
print('        </form>')
print('      </td>')
print('    </tr>')

print('')

print('    <tr>')
print('      <td>Unwrapper Reset Threshold:</td>')
print('      <td>')
print('        <form action="" method="GET" >')
print(f'          <input type="number" name="UnwrTHR" id="UnwrTHR" value="{Res_Thr}" min="0" onchange="javascript:this.form.submit()">')
print('           cnts')
print('        </form>')
print('      </td>')
print('    </tr>')

print('')

print('    <tr>')
print("      <td>Diagnostic Signal Generator Freq: 3'123'437.5 +</td>")
print('      <td>')
print('        <form action="" method="GET" >')
print(f'          <input type="number" name="siggenDFTW" id="siggenDFTW" value="{Siggen_DF}" onchange="javascript:this.form.submit()">')
print('           Hz')
print('        </form>')
print('      </td>')
print('    </tr>')

print('')

print('    <tr>')
print("      <td>Control Loop Extra Gain (default=4; hi-perf=6):</td>")
print('      <td>')
print('        <form action="" method="GET" >')
print(f'          <input type="number" name="extraGain" id="extraGain" value="{extraG}" onchange="javascript:this.form.submit()">')
print('        </form>')
print('      </td>')
print('    </tr>')

print('')

print('  </table>')

# -------- readback page

print('  <H3>Synchronizer Readback</H3>')
print('')
print('  <!-- readback values + Lock LEDs-->')
print('  <!-- keep it in a separate frame to enable autoupdate for readback values only -->')
print('  <!-- iframe src="readVars.html" scrolling=no style="border:none; height: 220px; width: 600px" title="Readback Values"></iframe -->')
print('  <iframe src="/cgi-bin/readVars.cgi" scrolling=no style="border:none; height: 350px; width: 600px" title="Readback Values"></iframe>')
print('')


print('</body>')
print('</html>')


