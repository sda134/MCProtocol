#!/usr/bin/env python
#coding: UTF-8
 
from . import config
from .classes import CpuType,CPUSeries,PacketType, Protocol, EtherFrame, SerialFrameID
from .fxdevice import FxDevice, FxDataType
from typing import List, Optional

def get_device_bytes(fx_device: FxDevice) -> bytearray:
    if config.CPU_SERIES == CPUSeries.iQ_R:
        dev_bytes = bytearray(fx_device.devicenumber.to_bytes(4, 'little'))
        dev_bytes.extend(fx_device.devicetype.to_bytes(2, 'little'))
    else:
        dev_bytes = bytearray(fx_device.devicenumber.to_bytes(3, 'little'))
        dev_bytes.extend(fx_device.devicetype.to_bytes(1, 'little'))
    return dev_bytes