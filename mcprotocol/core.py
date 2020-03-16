#!/usr/bin/env python
#coding: UTF-8
 
# ここは出来る限り見通しをよくする　c++の ヘッダーのような形をとる
# 各module のメソッドからはbytes で受け取って、signed16,32 などへの変換はここで行う
from typing import (List, Optional)

from .classes import CpuType, PacketType, Protocol, EtherFrame, SerialFrameID
from .fxdevice import FxDataType, FxDevice
from . import config, plc_dict, protcol_eth, protcol_1E
import socket

__byte_len_dic = {
    FxDataType.Signed16: 1,
    FxDataType.Signed32: 2, 
    FxDataType.Unsigned16: 1,
    FxDataType.Unsigned32: 2,
    FxDataType.Float: 2,
    FxDataType.Bit: 1,
    }

def _bytes_to_value(byte_data:bytes, data_type:FxDataType):
    if data_type == FxDataType.Signed16:
        return int.from_bytes(byte_data, 'little')
    else:
        pass
    return None

class MCProtocol():
    def __init__(self, cpu_type):
        __cpu_type = cpu_type
        config.ETHERNET_FRAME = plc_dict.EtherFrame[cpu_type]
        config.SERIAL_FRAME = plc_dict.SerialFrame[cpu_type]
        config.CPU_SERIES = plc_dict.CPU_Series[cpu_type]

    def __del__(self):
        pass
    
    def get_device(self, device_name:str, fx_data_type:FxDataType)-> Optional[FxDevice]:
        pass

    def get_device_list(self, start_device:str,device_list:List[FxDevice]):
        '''
        連続デバイスの読み込み
        device_list は値とデータ型のみが有効で、デバイス名は無視されます。
        '''
        pass


    def set_device_list(self, start_device:str,device_list:List[FxDevice]):
        '''
        連続デバイスの読み込み
        device_list は値とデータ型のみが有効で、デバイス名は無視されます。
        '''
        pass


    def get_device_random(self,device_list:List[FxDevice]):
        '''
        複数デバイスの読み込み
        '''
        if(config.PROTOCOL == Protocol.Serial):
            pass
        else:
            if(config.EtherFrame == EtherFrame.Ether_1E):
                pass
            else:
                return protcol_eth.get_device_random(device_list)

    def set_device_random(self, device_list:List[FxDevice]) :
        '''
        複数デバイスの書き込み
        '''
        if(config.PROTOCOL == Protocol.Serial):
            pass
        else:
            if(config.EtherFrame == EtherFrame.Ether_1E):
                pass
            else:
                return protcol_eth.set_device_random(device_list)
                
    def read_buffer(self, start_address, byte_array):
        pass

    def write_buffer(self, start_address, byte_array):
        pass
