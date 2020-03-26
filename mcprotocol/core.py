#!/usr/bin/env python
#coding: UTF-8
 
# ここは出来る限り見通しをよくする　c++の ヘッダーのような形をとる
# 各module のメソッドからはbytes で受け取って、signed16,32 などへの変換はここで行う
from typing import (List, Optional, Union)

from .classes import CpuType, PacketType, Protocol, EtherFrame, SerialFrameID
from .fxdevice import FxDataType, FxDevice
from . import config, plc_dict, protcol_eth, protcol_1E



class MCProtocol():
    def __init__(self, cpu_type):
        __cpu_type = cpu_type
        config.ETHERNET_FRAME = plc_dict.EtherFrame[cpu_type]
        config.SERIAL_FRAME = plc_dict.SerialFrame[cpu_type]
        config.CPU_SERIES = plc_dict.CPU_Series[cpu_type]        

    def __del__(self):
        pass
    

    def get_device(self, device_name:str, fx_data_type:FxDataType)-> Union[None, int, float]:
        '''
        単一デバイスの書き込み\n
        （実際には get_device_list のラッパーメソッドです。）
        '''
        ret = self.get_device_list(device_name, 1, fx_data_type)    # 単一の時とlistで引数の順番が異なる
        if ret == None: return None
        else: return ret

        
    def set_device(self, device_name:str, value:Union[int,float], fx_data_type:FxDataType)-> None:
        '''
        単一デバイスの書き込み\n
        （実際には set_device_list のラッパーメソッドです。）
        '''
        return self.set_device_list(device_name, [value], fx_data_type)


    def get_device_list(self, start_device:str, device_count:int, fx_data_type: FxDataType = FxDataType.Signed16 )-> List[Union[int,float]]:
        '''
        連続デバイスの読み込み\n
        start_device\t:先頭デバイス\n
        fx_data_type\t:データ型（※PLC からの取得バイトはすべてこの型に変換されます。）
        '''
        if(config.PROTOCOL == Protocol.Serial):
            pass
        else:
            if(config.ETHERNET_FRAME == EtherFrame.Ether_1E):
                pass
            else:
                return protcol_eth.get_device_list(start_device, device_count, fx_data_type)


    def set_device_list(self, start_device:str, value_list: List[Union[int, float]], fx_data_type: FxDataType = FxDataType.Signed16 )-> Union[int,float]:
        '''
        連続デバイスの書き込み\n
        start_device\t:先頭デバイス\n
        value_list\t:
        '''
        if(config.PROTOCOL == Protocol.Serial):
            pass
        else:
            if(config.EtherFrame == EtherFrame.Ether_1E):
                pass
            else:
                return protcol_eth.set_device_list(start_device, value_list, fx_data_type)


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
