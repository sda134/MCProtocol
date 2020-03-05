#!/usr/bin/env python
#coding: UTF-8
 
# ここは見通しをよくする　c++の ヘッダーのような形をとる
from .classes import CpuType, PacketType, Protocol, EtherFrame, SerialFrameID
from . import config, plc_dict, protcol_eth, protcol_1E
import socket

class MCProtocol():
    def __init__(self, cpu_type):
        __cpu_type = cpu_type
        config.ETHERNET_FRAME = plc_dict.EtherFrame[cpu_type]
        config.SERIAL_FRAME = plc_dict.SerialFrame[cpu_type]
        config.CPU_SERIES = plc_dict.CPU_Series[cpu_type]

    def __del__(self):
        pass
    
    def get_device(self, device_name):
        if(config.PROTOCOL == Protocol.Serial):
            return 0
        else:
            if(config.EtherFrame == EtherFrame.Ether_1E):
                return protcol_1E.get_device(device_name)
            else:
                return protcol_eth.get_device(device_name)
        
    def set_device(self, device_name, value) :
        pass

    def get_device_random(self):
        pass

    def set_device_random(self, device_blocks) :
        pass

    def read_buffer(self, start_address, byte_array):
        pass

    def write_buffer(self, start_address, byte_array):
        pass
