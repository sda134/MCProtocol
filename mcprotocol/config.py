#!/usr/bin/env python
#coding: UTF-8
 
'''
通信に必要な設定を行います。\n
ソースを直接書き換えて初期値を変更しても良いし、\n
mcprotocol.config.DESTINATION_IP = '192.168.1.1' \n
などと変更しても良い。
'''

from .classes import PacketType, Protocol, SerialFrameID, EtherFrame, SerialFormat, CPUSeries

DESTINATION_IP = '192.168.1.1'
DESTINATION_PORT = 5001
PACKET_TYPE = PacketType.Binary

PROTOCOL = Protocol.TCP_IP

SERIAL_FORMAT = SerialFormat.Format_4   # 形式
ETHERNET_FRAME = EtherFrame.Ether_1E    # 
SERIAL_FRAME = SerialFrameID.Serial_1C  # 
CPU_SERIES = CPUSeries.iQ_R

NETWORK_NUMBER= 0x00
PC_NUMBER= 0xFF                         # 255
I_O_NUMBER = 1023                       # 0x03, 0xFF となる(int16)
UNIT_NUMBER =0x00                       # ユニット番号

MONITOR_TIMER = 10                      # 監視タイマ