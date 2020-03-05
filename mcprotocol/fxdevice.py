#!/usr/bin/env python
#coding: UTF-8

# .NET 版から必要部分だけを抜粋
# このモジュールは単体でも動くように設計する。 

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

class FxNumberSystem(IntEnum):
    Decimal = 1,
    Hexadecimal = 2,
    Octal = 3

# モジュール変数
CPU_SERIES = CPUSeries.iQ_F


# デバイス番号の番号システム
num_sys_xy = FxNumberSystem.Decimal 
if CPUSeries == CPUSeries.iQ_R or CPUSeries == CPUSeries.iQ_F or  CPUSeries == CPUSeries.Q_Series:
    num_sys_xy = FxNumberSystem.Hexadecimal 
elif CPUSeries == CPUSeries.F_Series or CPUSeries == CPUSeries.iQ_F:
    num_sys_xy = FxNumberSystem.Octal 


# FxDevice.TryPerce で使う dict     変換アルゴリズムの為、文字数の多い順にする
_deviceNameDict = {
    FxDeviceType.Timer_Contact : ('TS', FxNumberSystem.Decimal),
    FxDeviceType.Timer_Coil : ('TC', FxNumberSystem.Decimal),
    FxDeviceType.Timer_Value : ('TN', FxNumberSystem.Decimal),

    FxDeviceType.InputSignal : ('X', num_sys_xy),
    FxDeviceType.OutputSignal : ('Y',num_sys_xy),
    FxDeviceType.InnerRelay : ('M',FxNumberSystem.Decimal),
    FxDeviceType.DataRegister : ('D', FxNumberSystem.Decimal),
}


class FxDevice:
    def __init__(self, device_name='D0'): # コンストラクタ
        self.DeviceNumber =-1

        if not isinstance(device_name, str):
            raise ValueError('deviceName must be str') # init で例外は△？ 19.07.15
        try:
            # 大文字に変換
            upper_name = str.upper(device_name)

            # デバイスレターを長さ順に並び替える
            devList = sorted(_deviceNameDict.items(), key = lambda x: x[1], reverse = True)

            # 一文字ずつ検索して、発見したら割り当てる
            for dev in devList:
                if upper_name.startswith(dev[1][0]):   # なぜか tuple になっている 19.07.15                    
                    str_encording = dev[1][1]
                    numberStr = device_name[len(dev[1][0]):len(device_name)]
                    self.__deviceLetter = dev[1][0]
                    self.__deviceType = dev[0]                    
                    if str_encording == FxNumberSystem.Hexadecimal:
                        self.DeviceNumber = int(numberStr,16)
                    elif str_encording == FxNumberSystem.Octal:
                        self.DeviceNumber = int(numberStr,8)
                    else:
                        self.DeviceNumber = int(numberStr, 10)
                else:
                    pass
        
        except Exception as e:
            print('Exception: %s' % e)

        if self.DeviceNumber== -1:
            self.DeviceNumber = None
            self.__deviceType = None

    @property                       # プロパティ get
    def DeviceType(self) -> FxDeviceType:
        return self.__deviceType
        
# これは別の場所に置く
class FxDataType(IntEnum):
    Signed16 = 0,
    Signed32 = 1,
    Float = 3,
    Bit = 4,
    Unsigned16 = 11,
    Unsigned32 = 12,
    BCD16 = 21,
    BCD32 = 22,

