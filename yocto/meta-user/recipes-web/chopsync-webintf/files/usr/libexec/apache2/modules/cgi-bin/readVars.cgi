#!/usr/bin/python

import socket
#import select
import os
#import urllib.parse
#import time
from datetime import datetime
#import numpy as np
#import matplotlib.pyplot as plt
#import io
#import base64
#import fnmatch

# constants
ERR_STRING='&ltERR&gt'
LOL_FNAME="lockloss.txt"

# defaults


# --------------------  open html page right away, so we can print errors on it -----------------------

print('Content-type:text/html\r\n\r\n')
print('<!DOCTYPE html>')
print('<html>')
print('<head>')
print('  <link rel="stylesheet" href="/LEDstyle.css">')
print('  <meta http-equiv="refresh" content="1">')
print('</head>')
print('<body>')



# --------- open a connection to r5ctrlr SCPI server ----------

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 8888))
#s.connect(("192.168.0.17", 8888))


# ------------------  get current config  --------------------

# -------- acceleration command
qstr='MECOS_CMD?\n'
s.sendall(bytes(qstr,encoding='ascii')) 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
if(tok[0].strip()=="OK:"):
  MECOS_cmd=tok[1].strip()
else:
  MECOS_cmd=ERR_STRING

# -------- phase error
qstr='PHERR?\n'
s.sendall(bytes(qstr,encoding='ascii')) 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
if(tok[0].strip()=="OK:"):
  pherr=tok[1].strip()
else:
  pherr=ERR_STRING

# -------- bunch marker frequency
qstr='BUNCHFREQ?\n'
s.sendall(bytes(qstr,encoding='ascii')) 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
if(tok[0].strip()=="OK:"):
  bunch_freq=tok[1].strip()
else:
  bunch_freq=ERR_STRING

# -------- chopper frequency
qstr='CHOPFREQ?\n'
s.sendall(bytes(qstr,encoding='ascii')) 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
if(tok[0].strip()=="OK:"):
  chop_freq=tok[1].strip()
else:
  chop_freq=ERR_STRING

# -------- bunch marker prescaler
qstr='BUNCHMARKER_PRESCALER?\n'
s.sendall(bytes(qstr,encoding='ascii')) 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
if(tok[0].strip()=="OK:"):
  R_div=tok[1].strip()
else:
  R_div=ERR_STRING

# -------- chopper prescaler
qstr='CHOPPER_PRESCALER?\n'
s.sendall(bytes(qstr,encoding='ascii')) 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
if(tok[0].strip()=="OK:"):
  N_div=tok[1].strip()
else:
  N_div=ERR_STRING

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

# -------- frequency lock
qstr='FLOCK?\n'
s.sendall(bytes(qstr,encoding='ascii')) 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
if(tok[0].strip()=="OK:"):
  if(tok[1].strip())=="ON":
    freq_lock=True
  else:
    freq_lock=False
else:
  # use default in case of error, but issue a message
  print('<br>Error querying frequency lock<br>')
  freq_lock=False

# -------- phase lock
qstr='PHLOCK?\n'
s.sendall(bytes(qstr,encoding='ascii')) 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
if(tok[0].strip()=="OK:"):
  if(tok[1].strip())=="ON":
    phase_lock=True
  else:
    phase_lock=False
else:
  # use default in case of error, but issue a message
  print('<br>Error querying phase lock<br>')
  phase_lock=False

# -------- sticky loss of lock alarm
qstr='STICKYLOL?\n'
s.sendall(bytes(qstr,encoding='ascii')) 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
if(tok[0].strip()=="OK:"):
  if(tok[1].strip())=="ON":
    sticky_LOL=True
  else:
    sticky_LOL=False
else:
  # use default in case of error, but issue a message
  print('<br>Error querying sticky loss of lock alarm<br>')
  sticky_LOL=False


# --------------------  now display body of html page  -----------------------

print('<table>')

print('  <tr>')
print('    <td>Acceleration Command:</td>')
print('    <td align="right">'+MECOS_cmd+'</td>')
print('    <td>pulses</td>')
print('  </tr>')

if pherr!=ERR_STRING:
  pherr_str="{:+d}".format(round(float(pherr)))
else:
  pherr_str=pherr
  
print('  <tr>')
print('    <td>Phase Error:</td>')
print('    <td align="right">'+pherr_str+'</td>')
print('    <td>ns</td>')
print('  </tr>')

print('  <tr>')
print('    <td>Bunch Marker Freq:</td>')
print('    <td align="right">'+bunch_freq+'</td>')
print('    <td>Hz</td>')
print('  </tr>')

print('  <tr>')
print('    <td>Chopper Freq:</td>')
print('    <td align="right">'+chop_freq+'</td>')
print('    <td>Hz</td>')
print('  </tr>')

print('  <tr>')
print('    <td> <br> </td>')
print('  </tr>')

# -------- scaled frequencies

if ((bunch_freq!=ERR_STRING) and (R_div!=ERR_STRING)):
  r=int(R_div)
  if r!=0:
    scaled_bunch="{:.3f}".format(float(bunch_freq)/float(R_div))
  else:
    scaled_bunch=ERR_STRING
else:
  scaled_bunch=ERR_STRING

print('  <tr>')
print('    <td>Bunch Marker Freq/'+R_div+':</td>')
print('    <td align="right">'+scaled_bunch+'</td>')
print('    <td>Hz</td>')
print('  </tr>')

if ((chop_freq!=ERR_STRING) and (N_div!=ERR_STRING)):
  n=int(N_div)
  if n!=0:
    scaled_chop="{:.3f}".format(float(chop_freq)/float(N_div))
  else:
    scaled_chop=ERR_STRING
else:
  scaled_chop=ERR_STRING

print('  <tr>')
print('    <td>Chopper Freq/'+N_div+':</td>')
print('    <td align="right">'+scaled_chop+'</td>')
print('    <td>Hz</td>')
print('  </tr>')

print('  <tr>')
print('    <td> <br> </td>')
print('  </tr>')

print('</table>')


# -------- Lock LEDs

print('<table>')

print('  <tr>')
print('    <td>Frequency Lock</td>')
print('    <td><span class="',end='')
if freq_lock:
  print('greendot',end='')
else:
  print('greydot',end='')
print('"></span></td>')
print('  </tr>')

print('  <tr>')
print('    <td>Phase Lock</td>')
print('    <td><span class="',end='')
if phase_lock:
  print('greendot',end='')
else:
  print('greydot',end='')
print('"></span></td>')
print('  </tr>')

print('  <tr>')
print('    <td>Phase Lock Loss Alarm (sticky)</td>')
print('    <td><span class="',end='')
if sticky_LOL:
  print('reddot',end='')
else:
  print('greydot',end='')
print('"></span></td>')
print('  </tr>')

print('</table>')
print('<br>')

# -------- print time of first loss of lock event
if sticky_LOL:
  if os.path.exists(LOL_FNAME):
    print('First Lock Loss event occurred on ')
    with open(LOL_FNAME, "r") as f:
      print(f.read())
    print('<br>')
    print('Current time is '+str(datetime.now()))
    print('<br>')
  else:
    with open(LOL_FNAME, "w") as f:
      f.write(str(datetime.now()))
else:
  if os.path.exists(LOL_FNAME):
    os.remove(LOL_FNAME)

print('<br>')
print('<br>')

print('</body>')
print('</html>')






