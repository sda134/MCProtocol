#!/usr/bin/env python
#coding: UTF-8

'''
三菱シーケンサで扱うデバイスを扱いやすくする為のモジュールです。\n
fx_dev = FxDevice('D100', FxDataType.Signed16)\n
この様に，文字列とデータ型を指定して下さい。
'''


# このモジュールは単体でも動くように設計する。 20.03.26まだ対応できてない

import struct
from typing import (Optional, Union, Sequence)
from enum import Enum, auto, IntEnum

from .classes import CPUSeries


class FxDeviceType(IntEnum):
    InputSignal = 0x9C,             # 入力 [X]
    OutputSignal = 0x9D,            # 出力 [Y]
    InnerRelay = 0x90,              # 内部リレー [M]
    DataRegister = 0xA8,            # データレジスタ [D]
    FileRegister = 0xAF,            # ファイルレジスタ：ブロック切り替え方式 [R]

    Timer_Contact = 0xC1,           # タイマー接点 [TS]
    Timer_Coil = 0xC0,              # タイマーコイル [TC]
    Timer_Value = 0xC2,             # タイマー現在値 [TN]

    SpecialRelay = 0x91,            # 特殊リレー [SM]
    SpecialRegister = 0xA9,         # 特殊レジスタ [SD]

    # 以下、未実装 20.03.25

    IntegratedTimerContact = 0xC7,  # 積算タイマー接点 [STS]
    IntegratedTimer_Coil = 0xC6,    # 積算タイマーコイル [STC]
    IntegratedTimer_Value = 0xC8,   # 積算タイマー現在値 [STN]

    Counter_Contact = 0xC4,         # カウンタ接点 [CS]
    Counter_Coil = 0xC3,            # カウンタコイル [CC]
    Counter_Value = 0xC5,           # カウンタ現在値 [CN]

    LongCounter_Contact = 0x55,     # ロングカウンタ接点 [LCS]
    LongCounter_Coil = 0x54,        # ロングカウンタコイル [LCC]
    LongCounter_Value = 0x56,       # ロングカウンタ現在値 [LCN]

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
        elif(self.value == FxDeviceType.FileRegister): return 'R'
        elif(self.value == FxDeviceType.Timer_Contact): return 'TS'
        elif(self.value == FxDeviceType.Timer_Coil): return 'TC'
        elif(self.value == FxDeviceType.Timer_Value): return 'TN'
        elif(self.value == FxDeviceType.SpecialRegister): return 'SD'
        elif(self.value == FxDeviceType.SpecialRelay): return 'SM'
        else: return ''


class FxDataType(IntEnum):
    Signed16 = 0,
    Signed32 = 1,
    Float = 3,
    Bit = 4,
    Unsigned16 = 11,
    Unsigned32 = 12,
    # BCD16 = 21,   未だ使った事がないので，実装する気が起きない
    # BCD32 = 22,

    def get_word_length(self):
        if(self.value == FxDataType.Signed16): return 1
        elif(self.value == FxDataType.Signed32): return 2
        elif(self.value == FxDataType.Unsigned16): return 1
        elif(self.value == FxDataType.Unsigned32): return 2
        elif(self.value == FxDataType.Float): return 2
        # elif(self.value == FxDataType.BCD16): return 1
        # elif(self.value == FxDataType.BCD32): return 2
        elif(self.value == FxDataType.Bit): return 1
        else: return None   # None はまずいかも？20.03.18


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
    __device_name_dict = {          # 文字列, 番号システム(16進など)，強制のデータ型
        FxDeviceType.Timer_Contact : ('TS', FxNumberSystem.Decimal, FxDataType.Bit),
        FxDeviceType.Timer_Coil : ('TC', FxNumberSystem.Decimal, FxDataType.Bit),
        FxDeviceType.Timer_Value : ('TN', FxNumberSystem.Decimal, FxDataType.Signed16),

        FxDeviceType.SpecialRegister : ('SD', FxNumberSystem.Decimal, None),
        FxDeviceType.SpecialRelay : ('SM', FxNumberSystem.Decimal, FxDataType.Bit),

        FxDeviceType.InputSignal : ('X', num_sys_xy, FxDataType.Bit),
        FxDeviceType.OutputSignal : ('Y',num_sys_xy, FxDataType.Bit),
        FxDeviceType.InnerRelay : ('M',FxNumberSystem.Decimal, FxDataType.Bit),
        FxDeviceType.DataRegister : ('D', FxNumberSystem.Decimal, None),
        FxDeviceType.FileRegister : ('R', FxNumberSystem.Decimal, None),
    }

    def __init__(self, device_name:str, fx_data_type = FxDataType.Signed16, value = 0): # コンストラクタ
        # 入力値確認
        if not isinstance(device_name, str):
            raise ValueError('device_name must be str') # init で例外は△？ 19.07.15
        
        # 初期値設定の必要な private member
        self.__number_system = FxNumberSystem.Decimal

        # None が標準の private member
        self.__deviceLetter:Optional[str] = None
        self.__index_register: Optional[int] = None
        self.__unit_number: Optional[int] = None
        self.__unit_index: Optional[int] = None
        self.__fx_device_type: Optional[FxDeviceType] = None
        
        # 引数の値を private member に代入
        self.__fx_data_type = fx_data_type
        
        # 大文字に変換
        dev_str_upper = str.upper(device_name)

        try:
            # ￥の有無で処理を変える
            slush_idx = device_name.find('\\')
            if not slush_idx == -1:
                unit_str = device_name[:slush_idx]
                number_str = device_name[slush_idx+1:]
                if unit_str[:1] == 'U':                
                    self.__unit_number = int(unit_str[1:])
                    if number_str[:2] == 'HG':          # 念のため文字数の多い方からやるべき
                        self.__fx_device_type = FxDeviceType.UnitBufferHG
                        self.__device_number = int(number_str[2:])
                    elif number_str[:1] == 'G':                    
                        self.__fx_device_type = FxDeviceType.UnitBuffer
                        self.__device_number = int(number_str[1:])
                    else:
                        inner_fx = FxDevice(number_str)  # 回帰呼び出し　※問題なく実行された 20.03.18
                        self.__fx_device_type = inner_fx.fxdevicetype
                        self.__device_number = inner_fx.devicenumber
                elif unit_str[:1] == 'J':
                    self.__unit_number = int(unit_str[1:])
                    self.__fx_device_type = FxDeviceType.LinqDirect
                    self.devicenumber = int(number_str)
                else:                               # ￥があって，その他の文字列が
                    self.__unit_number = None       # デバイス書式に準じていない，と言う事
                    self.__fx_device_type = None    # self = None みたいな感じでもいいくらい
            else:
                index_str = ''
                # ￥の有無で処理を変える
                for z in ['LZ', 'Z']:
                    index_idx = dev_str_upper.find(z)
                    if not index_idx == -1:
                        dev_str_upper = device_name[:index_idx]
                        z_num_str = device_name[index_idx + len(z):]
                        self.__index_register = int(z_num_str, 10)
                        
                # デバイスレターを長さ順に並び替える
                devList = sorted(self.__device_name_dict.items(), key = lambda x: x[1], reverse = True)
                # 一文字ずつ検索して、発見したら割り当てる
                for dev in devList:
                    if dev_str_upper.startswith(dev[1][0]):   # tuple である点に注意
                        self.__fx_device_type = dev[0]                    
                        self.__number_system = dev[1][1]
                        self.__deviceLetter = dev[1][0]
                        
                        forced_type = dev[1][2]
                        if not forced_type == None:
                            self.__fx_data_type = forced_type

                        numStr = dev_str_upper[len(dev[1][0]):len(dev_str_upper)]                        
                        if self.__number_system == FxNumberSystem.Hexadecimal:
                            self.__device_number = int(numStr,16)
                        elif self.__number_system == FxNumberSystem.Octal:
                            self.__device_number = int(numStr,8)
                        else:
                            self.__device_number = int(numStr, 10)
                                    
        except Exception as e:
            print('Exception: %s' % e)
        
        # データ型の強制変換があるので，value の代入は最後に行う
        if self.__fx_data_type == FxDataType.Float:
            self.__value = float(value)
        else:
            self.__value = int(value)

        
    def __str__(self):              # toString() の様な物。printなどで文字列に変換する場合に呼び出される。
        unit_str = '' if self.__unit_number == None else 'U{0}\\'.format(self.__unit_number)
        type_str = str(self.__fx_device_type)
        num_str = self.__device_number
        idx_str = '' if self.__index_register == None else 'Z{0}'.format(self.__index_register)
        return '{0}{1}{2}{3}'.format(unit_str,type_str,num_str, idx_str)


    def __repr__(self):             # __str__ に似ているが、repr() を使った時の結果
        unit_str = '' if self.__unit_number == None else 'U{0}\\'.format(self.__unit_number)
        type_str = str(self.__fx_device_type)
        num_str = self.__device_number
        val_str = self.__value
        idx_str = '' if self.__index_register == None else 'Z{0}'.format(self.__index_register)
        return '{0}{1}{2}{3} [{4}]'.format(unit_str,type_str,num_str, idx_str, val_str)


    @property                       # プロパティ get
    def fxdevicetype(self) -> FxDeviceType:
        return self.__fx_device_type
    @fxdevicetype.setter              # プロパティ set
    def fxdevicetype(self, arg):    
        self.__fx_device_type = arg

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
    def fxdatatype(self) -> FxDataType:
        return self.__fx_data_type    
    @fxdatatype.setter              # プロパティ set
    def fxdatatype(self, arg):    
        self.__fx_data_type = arg

    @property                       # プロパティ get
    def indexregister(self) -> Optional[int]:
        return self.__index_register
    @indexregister.setter           # プロパティ set
    def indexregister(self, arg):    
        self.__index_register = arg

    @property                       # プロパティ get
    def unitnumber(self) -> Optional[int]:
        return self.__unit_number
    @unitnumber.setter              # プロパティ set
    def unitnumber(self, arg):    
        self.__unit_number = arg


    @property                       # プロパティ get
    def numbersystem(self) -> FxNumberSystem:
        return self.__number_system

    @property                       # プロパティ get
    def is_extended_device(self) -> bool:
        return not self.__unit_number == None or not self.__index_register == None


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
        elif self.__fx_data_type == FxDataType.Bit:
            return int(self.__value).to_bytes(2, 'little',signed=True)
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
        elif self.__fx_data_type == FxDataType.Bit:
            self.__value = int.from_bytes(byte_data[:2],'little', signed=True)  # temporary Bitは16bitと同じにする
        pass


