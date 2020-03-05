#!/usr/bin/env python
#coding: UTF-8

import socket

#clr.AddReference("System")
#clr .AddReference("Mtec.UtilityLibrary.Mitsubishi.MCProtocol")

class MCProtcol:
    """三菱シーケンサと通信をする為のクラスです。"""


    # private member
    _pcNumber = 0xFF       # PC番号

    _watchTimer = 0x10     # 監視タイマー
       
    def GetDevice(self, deviceType):

        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        target = '192.168.1.11'
        port = 5015
        sendingData = bytearray([
            SubHeader_1E.ReadWord , # サブヘッダ 1byte
            self._pcNumber,         # PC番号 1byte
            self._watchTimer,0,     # ACPU 監視タイマ 2byte
            100,0, 0, 0,        # 先頭デバイス番号 4byte
            0x20,0x44,          # デバイスコード 2byte
            1,                  # デバイス点数
            0                   # 固定値
            ])
        
        # 接続
        soc.connect((target, port))   
   
        # データ送信
        count = soc.send(sendingData)

        return soc.recv(256)

        # Unicode文字を数値にして返す
        #return [int(b) for b in soc.recv(256)]




from enum import Enum, auto, IntEnum

class SubHeader_1E(IntEnum):
    ReadBit = 0x00,
    ReadWord = 0x01,
    WriteBit = 0x02,
    WriteWord = 0x03,
    BitRandomTest = 0x04,
    WordRandomTest = 0x05,
    BitMonitor = 0x08,
    WordMonitor = 0x09,

    Remote_Run = 0x13,
    Remote_Stop = 0x14,
    GetPCName = 0x15,
    ResponseTest = 0x16,        # 折り返しテスト


    RegisterRead = 0x17,
    RegisterWrite = 0x18,
    RegisterRandomTest = 0x19,
    RegisterMonitorRegister = 0x1A,
    RegisterMonitor = 0x1B,
    RegisterWriteDirect = 0x3B,
    RegisterReadDirect = 0x3C,
    UnitRead = 0x0E,
    UnitWrite = 0x0F



class DeviceType(Enum):
    InputSignal = 0x9C, #入力 [X]
    OutputSignal = 0x9D,#出力 [Y]
    InnerRelay = 0x90,  #内部リレー [M]
    DataRegister = 0xA8,#データレジスタ [D]


    #ワードデバイスの型
class DeviceFormat(Enum):
    Signed16 = auto(),
    Signed32 = auto(),
    Unsigned16 = auto(),
    Unsigned32 = auto(),
    Float = auto()


class DeviceFieldFormat():
    def __init__(self):   # コンストラクタ
        self.__comment = ''
        self.__deviceName = ''
        self.__deviceFormatType = ''
        self.__value = ''


    @property                       # プロパティ get
    def Comment(self):
        return self.__comment
    @Comment.setter                 # プロパティ set
    def name(self, arg):    
        self.__comment = arg

    @property                       # プロパティ get
    def DeviceName(self):
        return self.__deviceName
    @DeviceName.setter              # プロパティ set
    def name(self, arg):    
        self.__deviceName = arg

    @property                       # プロパティ get
    def DeviceFormatType(self):
        return self.__deviceFormatType
    @DeviceFormatType.setter        # プロパティ set
    def name(self, arg):    
        self.__deviceFormatType = arg

    @property                       # プロパティ get
    def Value(self):
        return self.__value
    @Value.setter                   # プロパティ set
    def name(self, arg):    
        self.__value = arg



