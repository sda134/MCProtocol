#!/usr/bin/env python
#coding: UTF-8

# .NET 版から必要部分だけを抜粋
# このモジュールは単体でも動くように設計する。 

import struct
from typing import (Optional, Sequence)
from enum import Enum, auto, IntEnum

from .classes import CPUSeries


class FxDeviceType(IntEnum):
    InputSignal = 0x9C,    # 入力 [X]
    OutputSignal = 0x9D,   # 出力 [Y]
    InnerRelay = 0x90,     # 内部リレー [M]
    DataRegister = 0xA8,   # データレジスタ [D]

    Timer_Contact = 0xC1,  # タイマー接点 [TS]
    Timer_Coil = 0xC0,     # タイマーコイル [TC]
    Timer_Value = 0xC2,    # タイマー現在値 [TN]


class FxDataType(IntEnum):
    Signed16 = 0,
    Signed32 = 1,
    Float = 3,
    Bit = 4,
    Unsigned16 = 11,
    Unsigned32 = 12,
    BCD16 = 21,
    BCD32 = 22,

    def get_word_length(self):
        if(self.value == FxDataType.Signed16): return 1
        elif(self.value == FxDataType.Signed32): return 2
        elif(self.value == FxDataType.Unsigned16): return 1
        elif(self.value == FxDataType.Unsigned32): return 2
        elif(self.value == FxDataType.Float): return 2
        elif(self.value == FxDataType.BCD16): return 1
        elif(self.value == FxDataType.BCD32): return 2
        elif(self.value == FxDataType.Bit): return 1
        else: return None


class FxNumberSystem(IntEnum):
    Decimal = 1,
    Hexadecimal = 2,
    Octal = 3


# モジュール変数
_CPU_SERIES = CPUSeries.iQ_F


# デバイス番号の番号システム
num_sys_xy = FxNumberSystem.Decimal 
if CPUSeries == CPUSeries.iQ_R or CPUSeries == CPUSeries.iQ_F or  CPUSeries == CPUSeries.Q_Series:
    num_sys_xy = FxNumberSystem.Hexadecimal 
elif CPUSeries == CPUSeries.F_Series or CPUSeries == CPUSeries.iQ_F:
    num_sys_xy = FxNumberSystem.Octal 



class FxDevice:
    __number_system : FxNumberSystem

    # FxDevice.TryPerce で使う dict     変換アルゴリズムの為、文字数の多い順にする
    __device_name_dict = {
        FxDeviceType.Timer_Contact : ('TS', FxNumberSystem.Decimal),
        FxDeviceType.Timer_Coil : ('TC', FxNumberSystem.Decimal),
        FxDeviceType.Timer_Value : ('TN', FxNumberSystem.Decimal),

        FxDeviceType.InputSignal : ('X', num_sys_xy),
        FxDeviceType.OutputSignal : ('Y',num_sys_xy),
        FxDeviceType.InnerRelay : ('M',FxNumberSystem.Decimal),
        FxDeviceType.DataRegister : ('D', FxNumberSystem.Decimal),
    }

    def __init__(self, device_name:str, fx_data_type = FxDataType.Signed16, value = 0): # コンストラクタ
        self.__device_number =-1
        self.__fx_data_type = fx_data_type

        if self.__fx_data_type == FxDataType.Float:
            self.__value = float(value)
        else:
            self.__value = int(value)

        if not isinstance(device_name, str):
            raise ValueError('deviceName must be str') # init で例外は△？ 19.07.15
        try:
            # 大文字に変換
            upper_name = str.upper(device_name)

            # デバイスレターを長さ順に並び替える
            devList = sorted(self.__device_name_dict.items(), key = lambda x: x[1], reverse = True)

            # 一文字ずつ検索して、発見したら割り当てる
            for dev in devList:
                if upper_name.startswith(dev[1][0]):   # なぜか tuple になっている 19.07.15                    
                    self.__number_system = dev[1][1]
                    numStr = device_name[len(dev[1][0]):len(device_name)]
                    self.__deviceLetter = dev[1][0]
                    self.__device_type = dev[0]                    
                    if self.__number_system == FxNumberSystem.Hexadecimal:
                        self.__device_number = int(numStr,16)
                    elif self.__number_system == FxNumberSystem.Octal:
                        self.__device_number = int(numStr,8)
                    else:
                        self.__device_number = int(numStr, 10)
                else:
                    pass
        
        except Exception as e:
            print('Exception: %s' % e)

        if self.__device_number== -1:
            self.__device_type = None

    def __str__(self):              # toString() の様な物。printなどで文字列に変換する場合に呼び出される。
        return '<str>' + '{0}{1}'.format(self.__device_type, self.__device_number)

    def __repr__(self):             # __str__ に似ているが、repr() を使った時の結果
        return '<repr>' + self.value


    @property                       # プロパティ get
    def devicetype(self) -> FxDeviceType:
        return self.__device_type

    @property                       # プロパティ get
    def numbersystem(self) -> FxNumberSystem:
        return self.__number_system


    @property                       # プロパティ get
    def fxdatatype(self) -> FxDataType:
        return self.__fx_data_type
    @fxdatatype.setter              # プロパティ set
    def fxdatatype(self, arg):    
        self.__fx_data_type = arg


    @property                       # プロパティ get
    def devicenumber(self) -> int:
        return self.__device_number
    @devicenumber.setter            # プロパティ set
    def devicenumber(self, arg:int):  
        self.__device_number = arg


    @property                       # プロパティ get
    def value(self):
        return self.__value
    @value.setter                   # プロパティ set
    def value(self, arg): 
        if self.__fx_data_type == FxDataType.Float:
            self.__value = float(arg)
        else:
            self.__value = int(arg)

    def value_to_bytes(self)-> bytes:
        if self.__fx_data_type == FxDataType.Signed16:
            return int(self.__value).to_bytes(2, 'little',signed=True)
        elif self.__fx_data_type == FxDataType.Signed32:
            return int(self.__value).to_bytes(4, 'little',signed=True)
        elif self.__fx_data_type == FxDataType.Unsigned16:
            return int(self.__value).to_bytes(2, 'little',signed=False)
        elif self.__fx_data_type == FxDataType.Unsigned32:
            return int(self.__value).to_bytes(4, 'little',signed=False)
        elif self.__fx_data_type == FxDataType.Float:
            return struct.pack('<f', float(self.__value))
        pass

    def set_value_from_bytes(self, byte_data: Sequence[int]):
        if self.__fx_data_type == FxDataType.Signed16:
            self.__value = int.from_bytes(byte_data[:2],'little', signed=True)
        elif self.__fx_data_type == FxDataType.Signed32:
            self.__value = int.from_bytes(byte_data[:4],'little', signed=True)
        elif self.__fx_data_type == FxDataType.Unsigned16:
            self.__value = int.from_bytes(byte_data[:2],'little', signed=True)
        elif self.__fx_data_type == FxDataType.Unsigned32:
            self.__value = int.from_bytes(byte_data[:4],'little', signed=True)
        elif self.__fx_data_type == FxDataType.Float:
            array = bytearray(byte_data)    # バイト数が足りないと怒られるので
            while len(array) < 4:           # 4byteを確保
                array.append(0x00)
            byte_data = bytes(array)        # 多くても怒られる →つまりbyte 数が4 の倍数である必用がある
            self.__value = struct.unpack('f', byte_data[:4])[0]
        pass

        