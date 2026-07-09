#!/usr/bin/python

import socket
import os
import urllib.parse
import time

#seconds to wait after issuing a CAN command to MECOS
CANSLEEP=2

# get the query string of the GET form. 
# It is passed to cgi scripts as the environment
# variable QUERY_STRING
query_string = os.environ['QUERY_STRING']
# convert the query string to a dictionary
arguments = urllib.parse.parse_qs(query_string)


# open a connection to chopsync SCPI server on localhost
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 8888))

print('Content-type:text/html\r\n\r\n')
print('<!DOCTYPE html>')
print('<html>')
print('<head>')
#print('<title>Test Python CGI script</title>')
print('</head>')
print('<body>')
print('<h2>MECOS Active Magnetic Bearing control</h2>')

print('This web page is about MECOS Active Magnetic Bearing and chopper motor driver;<br>')
print('if you want to control MaxIV chopper synchronizer, please use ')
print('<a href="/">this web page</a>')
print('<br><br>')

# check the fields of the GET form query string and act accordingly
for name in arguments.keys():
#    # the value is always a list, watch out for that
#    print(str(name) + ' = ' + str(arguments[name]))
#    print('<br>')
    #------------ new speed setpoint -------------
    if name=='setp':
      v_setp=arguments[name][0]
      cmd_s='MECOS:HZ_SETPOINT '+str(v_setp)+'\n'
 #     print(cmd_s)
      s.sendall(cmd_s.encode('ascii')) 
      ans=(s.recv(1024)).decode('utf-8')
      tok=ans.split(" ",2)
      if tok[0].strip()=='ERR:':
        print('Error commanding the new speed setpoint')
#      print(f'new commanded speed set point is {v_setp} Hz')
      time.sleep(CANSLEEP)
    #------------ rotation on/off -------------
    elif name=='rot':
      if arguments[name][0].strip()=='0':
        rot_st='OFF'
      else:
        rot_st='ON'
      cmd_s='MECOS:ROTATION '+rot_st+'\n'
 #     print(cmd_s)
      s.sendall(cmd_s.encode('ascii')) 
      ans=(s.recv(1024)).decode('utf-8')
      tok=ans.split(" ",2)
      if tok[0].strip()=='ERR:':
        print('Error commanding the new rotation state')
#      print(f'new rotation state is {rot_st}')
      time.sleep(CANSLEEP)
    #------------ lift up/down -------------
    elif name=='lift':
      if arguments[name][0].strip()=='0':
        lift_st='OFF'
      else:
        lift_st='ON'
      cmd_s='MECOS:LIFTUP '+lift_st+'\n'
 #     print(cmd_s)
      s.sendall(cmd_s.encode('ascii')) 
      ans=(s.recv(1024)).decode('utf-8')
      tok=ans.split(" ",2)
      if tok[0].strip()=='ERR:':
        print('Error commanding the new levitation state')
      time.sleep(CANSLEEP)
    #------------ reset MECOS faults -------------
    elif name=='mecos_fault_reset':
      if arguments[name][0].strip()=='reset':
        cmd_s='MECOS:FAULT_RESET\n'
 #       print(cmd_s)
        s.sendall(cmd_s.encode('ascii')) 
        ans=(s.recv(1024)).decode('utf-8')
        tok=ans.split(" ",2)
        if tok[0].strip()=='ERR:':
          print('Error resetting MECOS fault register')
        time.sleep(CANSLEEP)
# just ignore unknown parameters
#    else:
#      print('unknown parameter')
    

print('<table>')

#------------------------ desired speed -----------------------------------------
s.sendall(b"MECOS:HZ_SETPOINT?\n") 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
print('  <tr>')
print('    <td>Desired Speed:</td>')
print('    <td>')
if(tok[0].strip()=="OK:"):
  print('      <form action="" method="GET" >')
  print(f'        <input type="number" name="setp" id="setp" value={tok[1]} min="0" max="1000" step=1 onchange="javascript:this.form.submit()"> Hz')
  print('        </select>')
  print('      </form>')
else:
  print('    &ltERR&gt')
print('    </td>')
print('  </tr>')
#------------------------- rotation ----------------------------------------
s.sendall(b"MECOS:ROTATION?\n") 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
print('  <tr>')
print('    <td>Rotation:</td>')
print('    <td>')
if(tok[0].strip()=="OK:"):
  print('      <form action="" method="GET" >')
  print('        <select name="rot" id = "rot" onchange="javascript:this.form.submit()">')
  if(tok[1].strip()=="OFF"):
    print('          <option value = "0" selected="selected">OFF</option>')
    print('          <option value = "1">ON</option>')
  else:
    print('          <option value = "0">OFF</option>')
    print('          <option value = "1" selected="selected">ON</option>')
  print('        </select>')
  print('      </form>')
else:
  print('    &ltERR&gt')
print('    </td>')
print('  </tr>')
#------------------------- levitation ----------------------------------------
s.sendall(b"MECOS:LIFTUP?\n") 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
print('  <tr>')
print('    <td>Levitation:</td>')
print('    <td>')
if(tok[0].strip()=="OK:"):
  print('      <form action="" method="GET" >')
  print('        <select name="lift" id = "lift" onchange="javascript:this.form.submit()">')
  if(tok[1].strip()=="OFF"):
    print('          <option value = "0" selected="selected">OFF</option>')
    print('          <option value = "1">ON</option>')
  else:
    print('          <option value = "0">OFF</option>')
    print('          <option value = "1" selected="selected">ON</option>')
  print('        </select>')
  print('      </form>')
else:
  print('    &ltERR&gt')
print('    </td>')
print('  </tr>')

print('</table>')

print('<form action="" method="GET" id="mecos_fault_reset">')
print('  <button id="mecos_fault_reset_btn" name="mecos_fault_reset" type="submit" form="mecos_fault_reset" value="reset">Reset MECOS faults</button>')
print('</form>')


#<iframe src="/cgi-bin/readMecosVars.cgi" scrolling=no style="border:none; height: 350px; width: 600px" title="Readback Values"></iframe>
print('<iframe src="/cgi-bin/readMecosVars.cgi" scrolling=no style="border:none"></iframe>')

print('</body>')
print('</html>')

s.close

