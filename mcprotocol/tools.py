#!/usr/bin/env python
#coding: UTF-8

import socket
from typing import List, Optional

from . import config
from .classes import CpuType,CPUSeries,PacketType, Protocol, EtherFrame, SerialFrameID, MCCommand, SerialFrameID
from .fxdevice import FxDevice, FxDataType, FxDeviceType

class Eth():
    @staticmethod
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

    @staticmethod
    def get_command_bytes(command:MCCommand, is_bit_command:bool = False, extention:bool = False) -> bytearray:
        #「ビット単位の電文」の実装をする気は今のところない　20.03.13 
        cmd_bytes = bytearray([])
        if command == MCCommand.Monitor_Get or command == MCCommand.Monitor_Set:
            pass        # ちょっと違うらしいし，この機能を使う気がしないので保留 20.03.20
        else:
            cmd_bytes.extend(command.to_bytes(2,'little'))
            if extention:
                if is_bit_command and not command == MCCommand.Read_Random:     # ランダム読みにはbitコマンドがないらしい
                    if config.CPU_SERIES == CPUSeries.iQ_R:
                        cmd_bytes.extend([0x83,0x00])
                    else:
                        cmd_bytes.extend([0x81,0x00])
                else:
                    if config.CPU_SERIES == CPUSeries.iQ_R:
                        cmd_bytes.extend([0x82,0x00])
                    else:
                        cmd_bytes.extend([0x80,0x00])
            else:           
                if is_bit_command and not command == MCCommand.Read_Random:
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

    @staticmethod
    def get_device_bytes(fx_device: FxDevice) -> bytearray:
        dev_bytes = bytearray([])
        if fx_device.is_extended_device:        
            if fx_device.indexregister == None:
                dev_bytes.extend(b'\x00\x00')
            else:
                dev_bytes.extend(fx_device.indexregister.to_bytes(2,'little'))
            
            if config.CPU_SERIES == CPUSeries.iQ_R:
                dev_bytes.extend(fx_device.devicenumber.to_bytes(4, 'little'))
                dev_bytes.extend(fx_device.fxdevicetype.to_bytes(2, 'little'))
            else:
                dev_bytes.extend(fx_device.devicenumber.to_bytes(3, 'little'))
                dev_bytes.extend(fx_device.fxdevicetype.to_bytes(1, 'little'))
            
            dev_bytes.extend(b'\x00\x00')      # 拡張指定番号：ユニット番号のインデックス。多分使う事はない。20.03.19
            dev_bytes.extend(fx_device.unitnumber.to_bytes(2, 'little'))

            if fx_device.unitnumber == None:
                dev_bytes.append(0x00)
            elif fx_device.fxdevicetype == FxDeviceType.LinqDirect:
                dev_bytes.append(0xF9)
            elif fx_device.fxdevicetype == FxDeviceType.UnitBuffer:
                dev_bytes.append(0xF8)
            else:
                dev_bytes.append(0xFA)
        else:
            if config.CPU_SERIES == CPUSeries.iQ_R:
                dev_bytes.extend(fx_device.devicenumber.to_bytes(4, 'little'))
                dev_bytes.extend(fx_device.fxdevicetype.to_bytes(2, 'little'))
            else:
                dev_bytes.extend(fx_device.devicenumber.to_bytes(3, 'little'))
                dev_bytes.extend(fx_device.fxdevicetype.to_bytes(1, 'little'))
        
        return dev_bytes



def socket_send(sending_data:bytearray) -> Optional[bytearray]:    
    host = config.DESTINATION_IP    # なぜか一度変数にしないと
    port = config.DESTINATION_PORT  # 通信が拒否される
    recievedData = None

    try:
        if config.PROTOCOL == Protocol.UDP_IP:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as soc:
                soc.connect((host, port))
                
                if config.MONITOR_SENDING_BYTES:
                    print('Sending(UDP):', repr(sending_data))
                
                soc.sendall(sending_data)
                print('sent')
                recievedData = soc.recv(1024)
        elif config.PROTOCOL == Protocol.TCP_IP:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
                soc.connect((host, port))
                
                if config.MONITOR_SENDING_BYTES:
                    print('Sending(TCP):', repr(sending_data))
                
                soc.sendall(sending_data)
                recievedData = soc.recv(1024)
    except TimeoutError:
        print ('Timeout')
        pass
    except Exception as e:
        print ('Exception: %s' % e)
    else:
        pass
    return recievedData


def distinguish_reciedved_data(recieved_data:bytearray):
    if recieved_data == None:return None
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
