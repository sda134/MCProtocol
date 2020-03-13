#!/usr/bin/env python
#coding: UTF-8

from time import sleep
import serial
import RPi.GPIO as GPIO

# 送信のために pin18 をon する
GPIO.setmode(GPIO.BCM)      # BCM番号での指定（使用前に指定が必要）
GPIO.setup(18,GPIO.OUT)     # pin18 を出力ピンにする(毎回設定が必要らしい)
GPIO.output(18,GPIO.HIGH) 

# 送信データ（適当に作った）
#data = bytearray([0x55,0x61,0x55,0x61]) # 0110 0001  0101 0101
#data = bytearray([0x2A,0x61,0x2A,0x61]) # 0010 1010 0110 0001
#data = bytearray([0xA5,0x69,0xA5,0x69]) # 1010 0101 0110 1001
data = bytearray([0x2A,0xAA,0x2A,0xAA]) # 0010 1010 1010 1010

#待ち時間計
baudrate = 9600.0                    # ≒ bps 早すぎるとエラーになるみたい
waitSec = 1.0 / baudrate * len(data) # 実際にはstopbit などが影響するが、無視して計算する
print("待ち時間 %f" % (waitSec))
waitSec += 0.010                     # 保険のために 10msec 加算しておく



# シリアル通信のインスタンス
ser = serial.Serial(
    port='/dev/ttyS0',
    baudrate= 9600,
    bytesize= serial.EIGHTBITS,       # SEVENBITS =7; EIGHTBITS =8
    stopbits= serial.STOPBITS_ONE,
    parity= serial.PARITY_NONE)       # なぜかNONE以外指定できない 19.07.10

ser.write(data)                      # 送信

sleep(waitSec)              # RTS 信号を消すのを少し待機する
GPIO.output(18,GPIO.LOW)    # RTS のOFF

ser.close()

