#!/usr/bin/env python
#coding: UTF-8

from enum import Enum, auto, IntEnum

class DeviceFormatType(IntEnum):
    Signed16 = 0,
    Signed32 = 1,
    Float = 3,
    Bit = 4,
    Unsigned16 = 11,
    Unsigned32 = 12,
    BCD16 = 21,
    BCD32 = 22,


class DeviceFieldFormat:    
    def __init__(self):             # コンストラクタ
        self.DeviceName ="D0"       # これでもメンバが生成される
        self.__fxDeviceType = DeviceFormatType.Signed16

    def __del__(self):              #デストラクタ
        pass

    @property                       # プロパティ get
    def FxDeviceType(self):
        return self.__fxDeviceType

    @FxDeviceType.setter            # プロパティ set
    def FxDeviceType(self, arg: FxDeviceType):    
        self.__fxDeviceType = arg