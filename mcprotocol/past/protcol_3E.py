#!/usr/bin/env python
#coding: UTF-8



class Protcol_3E:
    def __init__(self):             # コンストラクタ
        pass

    def __del__(self):              #デストラクタ
        pass

    # メソッド
    def GetDevice(self, startDevice, deviceCount, readData):
        sendingData = bytearray([
            0x50,0x00,                # 要求電文を示す(2byte)
            0x00,                     # ネットワーク番号
            0xFF,                     # PC番号
            0xFF,0x03,                # 要求先ユニットI/O番号
            0x00,                     # 要求先ユニット局番号

            0x0C,0x00,                # 要求データ長さ(2byte)
            0x10,0x00,                # 監視タイマ(2byte)

            0x01,0x4,                 # 読み込み
            0x0,0x0,                  # サブコマンド？
            0x64,0x00,0x00,           # デバイス番号(3byte)
            0xA8,                     # デバイスコード(1byte) ※データレジスタ
            0x01,0x00])               # デバイス数

    def SetDevice(self, startDevice, deviceCount, writeData):
        pass



