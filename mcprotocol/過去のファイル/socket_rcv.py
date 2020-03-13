#!/usr/bin/env python
#coding: UTF-8

import socket

host = ''
port = 6012

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind((host,port))
soc.listen(1)
conn, addr = soc.accept()

print('Connected by', addr)
while True:
	data = conn.recv(1024)
	print('Recieved Data', repr(data))
	if not data: break
	conn.sendall(data)
