#!/usr/bin/env python
#coding: UTF-8

# .NET 版から必要部分だけを抜粋
# このモジュールは単体でも動くように設計する。 

import struct
from typing import (Optional, Union, Sequence)
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

    # 以下、未実装 20.03.17
    SpecialRelay = 0x91,    # 特殊リレー [SM]
    SpecialRegister = 0xA9, # 特殊レジスタ [SD]

    IntegratedTimerContact = 0xC7,  # 積算タイマー接点 [STS]
    IntegratedTimer_Coil = 0xC6,    # 積算タイマーコイル [STC]
    IntegratedTimer_Value = 0xC8,   # 積算タイマー現在値 [STN]

    Counter_Contact = 0xC4,         # カウンタ接点 [CS]
    Counter_Coil = 0xC3,            # カウンタコイル [CC]
    Counter_Value = 0xC5,           # カウンタ現在値 [CN]

    LongCounter_Contact = 0x55,     # ロングカウンタ接点 [LCS]
    LongCounter_Coil = 0x54,        # ロングカウンタコイル [LCC]
    LongCounter_Value = 0x56,       # ロングカウンタ現在値 [LCN]

    FileRegister = 0xAF,            # ファイルレジスタ：ブロック切り替え方式 [R]
    FileRegister_ZR = 0xB0,         # ファイルレジスタ：連番アクセス方式 [ZR]  なぜ２つある？ 18.01.16
    RefreshDataRegister = 0x2C,     # リフレッシュデータレジスタ [RD]

    LinqDirect = 0x4A,              # リンクダイレクトデバイス [Jn\]

    UnitBuffer = 0xAB,              # バッファ [Un\G*]
    #RCPUBuffer = 0xAB,             # バッファ [Un\**]  RCPUのバッファメモリらしいが、良く分からない 20.03.17
    # ⇒ デバイスコードは通常のものを使う。RCPUBufferかどうかは unit_number がNone かどうかで判断する
    UnitBufferHG = 0x2E,            # バッファ [Un\HG*] iQRで用いる、ユニットバッファの定周期通信エリアの事らしいが良く分からない。20.03.17

    def __str__(self):
        if(self.value == FxDeviceType.InputSignal): return 'Y'
        elif(self.value == FxDeviceType.OutputSignal): return 'X'
        elif(self.value == FxDeviceType.InnerRelay): return 'M'
        elif(self.value == FxDeviceType.DataRegister): return 'D'
        elif(self.value == FxDeviceType.Timer_Contact): return 'TS'
        elif(self.value == FxDeviceType.Timer_Coil): return 'TC'
        elif(self.value == FxDeviceType.Timer_Value): return 'TN'


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
        self.__unit_number:Optional[int] = None
        self.__fx_data_type = FxDataType.Signed16
        self.__value: Union[int, float] = 0
        self.__number_system = FxNumberSystem.Decimal
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
                if upper_name.startswith(dev[1][0]):   # tuple である点に注意
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
        return '{0}{1}'.format(str(self.__device_type), self.__device_number)


    def __repr__(self):             # __str__ に似ているが、repr() を使った時の結果
        return '{0}{1} [{2}]'.format(
            str(self.__device_type), self.__device_number, str(self.value)
            )


    @property                       # プロパティ get
    def devicetype(self) -> FxDeviceType:
        return self.__device_type
    @devicetype.setter              # プロパティ set
    def devicetype(self, arg):    
        self.__device_type = arg


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


    @property                       # プロパティ get
    def unitnumber(self) -> FxDataType:
        return self.__unit_number
    @unitnumber.setter              # プロパティ set
    def unitnumber(self, arg):    
        self.__unit_number = arg



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
            self.__value = int.from_bytes(byte_data[:2],'little', signed=False)
        elif self.__fx_data_type == FxDataType.Unsigned32:
            self.__value = int.from_bytes(byte_data[:4],'little', signed=False)
        elif self.__fx_data_type == FxDataType.Float:
            array = bytearray(byte_data)    # バイト数が足りないと怒られるので
            while len(array) < 4:           # 4byteを確保
                array.append(0x00)
            byte_data = bytes(array)        # 多くても怒られる →つまりbyte 数が4 の倍数である必用がある
            self.__value = float(struct.unpack('f', byte_data[:4])[0])
        pass




class UnitDevice(FxDevice):
    def __init__(self, device_name:str):
        idx = device_name.find('\\')
        if not idx == -1:
            unit_str = device_name[:idx]
            number_str = device_name[idx+1:]
            if unit_str[:1] == 'U':                
                self.unitnumber = int(unit_str[1:])
                if number_str[:1] == 'G':                    
                    self.devicetype = FxDeviceType.UnitBuffer
                    self.devicenumber = int(number_str[1:])
                    print('hoge')
                elif number_str[:2] == 'HG':
                    self.devicetype = FxDeviceType.UnitBufferHG
                    self.devicenumber = int(number_str[2:])
                else:
                    fx = super().__init__(number_str)
                    self.devicetype = fx.devicetype
                    self.devicenumber = fx.devicenumber
            elif unit_str[:1] == 'J':
                self.unitnumber = int(unit_str[1:])
                self.devicetype = FxDeviceType.LinqDirect
                self.devicenumber = int(number_str)
                print('hoge')
            else:                               # ￥があって，その他の文字列が
                self.__unit_number = None       # デバイス書式に準じていない，と言う事
                self.__fx_device_type = None    # self = None みたいな感じでもいいくらい
                print('hoge')


