#!/usr/bin/env python
#coding: UTF-8

import socket
from . import config
from .fxdevice import FxDevice
from .classes import EtherFrame, CPUSeries

def _get_route_bytes() -> bytearray:
    if(config.ETHERNET_FRAME == EtherFrame.Ether_4E):
        rt_bytes = bytearray([0x50,0x00,0x00,0x00,0x00,0x00])
    else:
        rt_bytes = bytearray([0x50,0x00])    
    rt_bytes.append(config.NETWORK_NUMBER)              # ネットワーク番号
    rt_bytes.append(config.PC_NUMBER)                   # PC番号
    rt_bytes.extend(config.I_O_NUMBER.to_bytes(2, 'little')) # 要求先ユニットI/O番号
    rt_bytes.append(config.UNIT_NUMBER)                 # ユニット局番
    return rt_bytes


def _get_device_bytes(device_name: str) -> bytearray:
    fxdev = FxDevice(device_name)
    if config.CPU_SERIES == CPUSeries.iQ_R:
        dev_bytes = bytearray(fxdev.DeviceNumber.to_bytes(4, 'little'))
        dev_bytes.extend(fxdev.DeviceType.to_bytes(2, 'little'))
    else:
        dev_bytes = bytearray(fxdev.DeviceNumber.to_bytes(3, 'little'))
        dev_bytes.extend(fxdev.DeviceType.to_bytes(1, 'little'))
    return dev_bytes


def get_device(device_name: str) -> bytearray:
    rt_bytes = _get_route_bytes()                       # 要求データ（特にデータ長さが必要）
    rqst_bytes = bytearray(config.MONITOR_TIMER.to_bytes(2, 'little'))    # 監視タイマ(2byte)
    rqst_bytes.extend([0x01,0x4,0x0,0x0])               # コマンド：読み込み＋サブコマンド    
    rqst_bytes.extend(_get_device_bytes(device_name))   # デバイス番号
    rqst_bytes.extend([0x01, 0x00])                     # デバイス数

    sendingData = rt_bytes                              # アクセス経路まで
    sendingData.extend(len(rqst_bytes).to_bytes(2, 'little'))  # 要求データ長さ(2byte)
    sendingData.extend(rqst_bytes)                      # 要求データ

    # なぜか一度変数にしないと通信が拒否される
    host = config.DESTINATION_IP
    port = config.DESTINATION_PORT

    # 戻り値になる変数
    recievedData = None

    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect((host, port))
        print('Sending:', repr(sendingData))
        soc.sendall(sendingData)
        recievedData = soc.recv(1024)
        print('Received:', repr(recievedData))        
    except TimeoutError:
        print ('Timeout')
        pass
    except Exception as e:
        print ('Exception: %s' % e)
    else:
        pass
    
    return recievedData

