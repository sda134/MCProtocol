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

PROTOCOL: Protocol = Protocol.TCP_IP

SERIAL_FORMAT:SerialFormat = SerialFormat.Format_4   # 形式
ETHERNET_FRAME:EtherFrame = EtherFrame.Ether_1E    # 
SERIAL_FRAME:SerialFrameID = SerialFrameID.Serial_1C  # 
CPU_SERIES:CPUSeries = CPUSeries.iQ_R

NETWORK_NUMBER= 0x00
PC_NUMBER= 0xFF                         # 255
I_O_NUMBER = 1023                       # 0x03, 0xFF となる(int16)
UNIT_NUMBER =0x00                       # ユニット番号

MONITOR_TIMER = 0x01                    # 監視タイマ

MONITOR_SENDING_BYTES = False           # 送信バイトをprint する
MONITOR_RECEIVED_BYTES = False          # 送信バイトをprint する
