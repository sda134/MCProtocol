#!/usr/bin/env python
#coding: UTF-8

import time
import serial
import binascii

with serial.Serial(
    port='/dev/ttyS0',
    baudrate= 9600,
    bytesize= serial.SEVENBITS,         # SEVENBITS =7; EIGHTBITS =8
    stopbits= serial.STOPBITS_ONE,
    parity= serial.PARITY_NONE) as ser: # なぜか PARITY_NONE 以外指定できない 19.07.10

    while True:
        line= ser.readline()      # = read_until(b'\x0A') と同じ
        rcvData= line.rstrip()    # 空白と改行コードの削除
        print(repr(rcvData))
    
    '''
        rcvData= ser.read()         # 引数なし 1文字づつ
        rcvData= ser.read(10)       # 引数あり 指定バイト数になった時にバッファから取り出し
    '''
    
