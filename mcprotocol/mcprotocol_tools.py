#!/usr/bin/env python
#coding: UTF-8

import socket
from typing import List, Optional

from . import config
from .classes import CpuType,CPUSeries,PacketType, Protocol, EtherFrame, SerialFrameID, MCCommand, SerialFrameID
from .fxdevice import FxDevice, FxDataType, FxDeviceType


def get_route_bytes() -> bytearray:
    rt_bytes = bytearray([])
    if(config.ETHERNET_FRAME == EtherFrame.Ether_4E):
        rt_bytes = bytearray([0x50,0x00,0x00,0x00,0x00,0x00])
    else:
        rt_bytes = bytearray([0x50,0x00])
    rt_bytes.append(config.NETWORK_NUMBER)              # ネットワーク番号
    rt_bytes.append(config.PC_NUMBER)                   # PC番号
    rt_bytes.extend(config.I_O_NUMBER.to_bytes(2, 'little')) # 要求先ユニットI/O番号
    rt_bytes.append(config.UNIT_NUMBER)                 # ユニット局番
    return rt_bytes


def get_command_bytes(command:MCCommand, is_bit_command:bool = False, extention:bool = False) -> bytearray:
    cmd_bytes = bytearray([])
    if config.PROTOCOL == Protocol.Serial and (config.SERIAL_FRAME == SerialFrameID.Serial_1C or config.SERIAL_FRAME == SerialFrameID.Serial_2C):
        #print('1C or 2C')
        pass
    elif not config.PROTOCOL == Protocol.Serial and config.ETHERNET_FRAME == EtherFrame.Ether_1E:
        #print('1E')
        pass
    else:
        #print('3E/4E or 3C/4C')
        if command == MCCommand.Monitor_Get or command == MCCommand.Monitor_Set:
            pass
        else:
            cmd_bytes.extend(command.to_bytes(2,'little'))            
            if is_bit_command:                                  # 但し「ビット単位の電文」の実装をする気は今のところない　20.03.13 
                if config.CPU_SERIES == CPUSeries.iQ_R:
                    cmd_bytes.extend([0x03,0x00])
                else:
                    cmd_bytes.extend([0x01,0x00])
            else:
                if config.CPU_SERIES == CPUSeries.iQ_R:
                    cmd_bytes.extend([0x02,0x00])
                else:
                    cmd_bytes.extend([0x00,0x00])
    return cmd_bytes


def get_device_bytes(fx_device: FxDevice) -> bytearray:
    if config.CPU_SERIES == CPUSeries.iQ_R:
        dev_bytes = bytearray(fx_device.devicenumber.to_bytes(4, 'little'))
        dev_bytes.extend(fx_device.devicetype.to_bytes(2, 'little'))
    else:
        dev_bytes = bytearray(fx_device.devicenumber.to_bytes(3, 'little'))
        dev_bytes.extend(fx_device.devicetype.to_bytes(1, 'little'))
    return dev_bytes



def socket_send(sending_data:bytearray) -> Optional[bytearray]:    
    host = config.DESTINATION_IP    # なぜか一度変数にしないと
    port = config.DESTINATION_PORT  # 通信が拒否される
    recievedData = None

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
            soc.connect((host, port))
            
            if config.MONITOR_SENDING_BYTES:
                print('Sending:', repr(sending_data))
            
            soc.sendall(sending_data)
            recievedData = soc.recv(1024)

            if config.MONITOR_RECEIVED_BYTES:
                print('Received:', repr(recievedData))    
    except TimeoutError:
        print ('Timeout')
        pass
    except Exception as e:
        print ('Exception: %s' % e)
    else:
        pass
    return recievedData


def distinguish_reciedved_data(recieved_data:bytearray):
    if(config.ETHERNET_FRAME == EtherFrame.Ether_4E):
        start = 9
    else:
        start = 7
    data_length = int.from_bytes(recieved_data[start:start+2], 'little')
    ret_code = int.from_bytes(recieved_data[start+2:start+4], 'little')
    data_bytes:bytearray = bytearray([])
    if data_length > 2:
        data_bytes = recieved_data[start+4:]

    return ret_code, data_bytes
