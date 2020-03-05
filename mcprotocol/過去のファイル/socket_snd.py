#!/usr/bin/env python
#coding: UTF-8

import socket

host = '10.4.1.112'
port = 6002
sndData = bytearray([0x30,0x30,0x30,0x30])

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.connect((host,port))
soc.sendall(sndData)
rcvData = soc.recv(1024)
print('Received', repr(rcvData))

