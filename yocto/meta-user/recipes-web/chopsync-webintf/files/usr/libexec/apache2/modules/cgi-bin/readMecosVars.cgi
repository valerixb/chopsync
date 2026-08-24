#!/usr/bin/python

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 8888))

print('Content-type:text/html\r\n\r\n')
print('<!DOCTYPE html>')
print('<html>')
print('<head>')
print('  <link rel="stylesheet" href="/LEDstyle.css">')
print('  <meta http-equiv="refresh" content="1" >')
print('</head>')
print('<body>')

print('<table>')

#------------------------ actual speed -----------------------------------------
s.sendall(b"MECOS:HZ_ACTUAL?\n") 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
if(tok[0]=="OK:"):
  v_act=tok[1] + " Hz"
else:
  v_act='&ltERR&gt'
  #v_act=ans
print('  <tr>')
print('    <td>Actual Speed:</td>')
print(f'    <td>{v_act}</td>')
print('  </tr>')
#------------------------- Ext Ctrl Enabled ----------------------------------------
s.sendall(b"MECOS:STABLE?\n") 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
print('  <tr>')
print('    <td>Ext CTRL Enabled</td>')
if(tok[0]=="OK:"):
  if(tok[1].strip()=="OFF"):
    print('      <td><span class="reddot"></span></td>')
  else:
    print('      <td><span class="greendot"></span></td>')
else:
  print('      <td><span class="greydot"></span></td>')
print('  </tr>')
#------------------------- Fault ----------------------------------------
s.sendall(b"MECOS:FAULT?\n") 
ans=(s.recv(1024)).decode("utf-8")
tok=ans.split(" ",2)
print('  <tr>')
print('    <td>Fault</td>')
if(tok[0]=="OK:"):
  if(tok[1].strip()=="OFF"):
    print('      <td><span class="greendot"></span></td>')
  else:
    print('      <td><span class="reddot"></span></td>')
else:
  print('      <td><span class="greydot"></span></td>')
print('  </tr>')


print('</table>')


print('</body>')
print('</html>')

s.close

