#!/usr/bin/env python
#coding: UTF-8

from typing import (Optional, Union, List, Dict)

from mcprotocol import config, tools
from mcprotocol.classes import EtherFrame, CPUSeries, MCCommand
from mcprotocol.fxdevice import FxDevice, FxDataType, FxDeviceType


def get_device_list(start_device: str, device_count: int, fx_datatype: FxDataType = FxDataType.Signed16 )-> Union[None,int, List[Union[int,float]]]:    # MCProtocol的にはこっちがメインメソッドらしい
    rqst_bytes = bytearray(config.MONITOR_TIMER.to_bytes(2, 'little'))  # 監視タイマ(2byte)
    fx_dev = FxDevice(start_device)                                     # 先頭デバイスを文字列から扱いやすい形に変換

    rqst_bytes.extend(tools.Eth.get_command_bytes(              # コマンドを示すデータバイト
        MCCommand.Read_List,
        extention= fx_dev.is_extended_device))
    rqst_bytes.extend(tools.Eth.get_device_bytes(fx_dev))       # 開始デバイスを示すバイト列

    word_length = fx_datatype.get_word_length() * device_count  # デバイス点数(2byte) 
    rqst_bytes.extend(word_length.to_bytes(2, 'little'))        # 三菱の仕様から察するに，ここでの「デバイス」はint16の事　本来ならばword数と言うべき。

    sd_data = tools.Eth.get_route_bytes()                       # アクセス経路まで
    sd_data.extend(len(rqst_bytes).to_bytes(2, 'little'))       # 要求データ長さ(2byte)
    sd_data.extend(rqst_bytes)                                  # 要求データ

    recievedData = tools.socket_send(sd_data)                   # ソケットで送信

    if recievedData == None: return None                        # 通信失敗
            
    distinguished = tools.distinguish_reciedved_data(recievedData)   # データ判別
    ret_code = distinguished[0]

    if not ret_code ==0: return ret_code                        # エラーコードだった場合は処理を中止

    count = 0                                                   # デバイスリストに値を格納していく
    data_bytes = distinguished[1]
    value_list = []

    for c in range(device_count):                               # ※ここではループ変数 c は使わない。→もっといい方法ないか？
        dev = FxDevice(start_device, fx_datatype)               # デバイス名（特に番号）は割とどうでも良いために ループ内すべてstart_deviceを使っている。
        byte_length = fx_datatype.get_word_length() * 2         # バイト数
        dev.set_value_from_bytes(data_bytes[count:count+byte_length])   # bytes から値を代入
        value_list.append(dev.value)
        count += byte_length

    return value_list

def set_device_list(start_device: str, value_list: List[Union[int, float]], fx_datatype: FxDataType = FxDataType.Signed16 )-> None:
    rqst_bytes = bytearray(config.MONITOR_TIMER.to_bytes(2, 'little'))  # 監視タイマ(2byte)
    
    fx_dev = FxDevice(start_device)                                     # 先頭デバイスを文字列から扱いやすい形に変換
    rqst_bytes.extend(tools.Eth.get_command_bytes(                      # コマンドを示すデータバイト
        MCCommand.Write_List,
        extention= fx_dev.is_extended_device))
    rqst_bytes.extend(tools.Eth.get_device_bytes(fx_dev))               # 先頭デバイス番号＋デバイスコードを示すバイト列

    word_length = fx_datatype.get_word_length() * len(value_list)       # デバイス点数(1byte)   ※本来ならばword数と言うべき
    rqst_bytes.extend(word_length.to_bytes(2, 'little'))                # （三菱の仕様から察するに，ここでの「デバイス」はint16の事）

    for val in value_list:                                              # 具体的な書き込みデータ　※注意！ここでは生成されるFxDevice のfx_devicetype とvalue だけが重要で、
        dev = FxDevice(start_device, fx_datatype, val)                  # デバイス名（特に番号）は割とどうでも良いために ループ内すべてstart_deviceを使っている。
        rqst_bytes.extend(dev.value_to_bytes())

    sd_data = tools.Eth.get_route_bytes()                               # アクセス経路まで
    sd_data.extend(len(rqst_bytes).to_bytes(2, 'little'))               # 要求データ長さ(2byte)
    sd_data.extend(rqst_bytes)                                          # 要求データ

    recievedData = tools.socket_send(sd_data)                           # ソケットで送信

    distinguished = tools.distinguish_reciedved_data(recievedData)      # データ判別
    ret_code = distinguished[0]
    return ret_code                                                     # set_device の場合は戻り値変換がないので，そのままの値を返しても良い。

def get_device_random(device_list: List[FxDevice]):
    rqst_bytes = bytearray(                         #
        config.MONITOR_TIMER.to_bytes(2, 'little')) # 監視タイマ(2byte)

    if config.CPU_SERIES == CPUSeries.iQ_R:         # Random 読みはbit 版がないらしい
        rqst_bytes.extend([0x03,0x04,0x02,0x00])    # ワード，iQ-R   モニタ条件を指定　は無視 20.03.16
    else:
        rqst_bytes.extend([0x03,0x04,0x00,0x00])    # ワード，Q/L
    
    # single word とdouble word を分ける    ※良いgroupbyが見つからなかった
    single_list: List[FxDevice] =[]
    double_list: List[FxDevice] =[]
    for dev in device_list:
        if dev.fxdatatype.get_word_length() == 1: single_list.append(dev)
        elif dev.fxdatatype.get_word_length() == 2: double_list.append(dev)

    rqst_bytes.extend(len(single_list).to_bytes(1, 'little'))   # single wordデータ長さ(1byte)
    rqst_bytes.extend(len(double_list).to_bytes(1, 'little'))   # double wordデータ長さ(1byte)

    for dev in single_list:
        rqst_bytes.extend(tools.Eth.get_device_bytes(dev))    # デバイス名＋デバイスコード：single word
        pass

    for dev in double_list:
        rqst_bytes.extend(tools.Eth.get_device_bytes(dev))    # デバイス名＋デバイスコードdouble word
        pass

    sd_data = tools.Eth.get_route_bytes()            # アクセス経路まで
    sd_data.extend(len(rqst_bytes).to_bytes(2, 'little'))   # 要求データ長さ(2byte)
    sd_data.extend(rqst_bytes)                              # 要求データ

    recievedData = tools.socket_send(sd_data)    # ソケットで送信

    if recievedData == None:                                # 通信失敗
        return None
    
    distinguished = tools.distinguish_reciedved_data(recievedData)   # データ判別

    ret_code = distinguished[0]
    if not ret_code ==0: return ret_code

    count = 0                                               # デバイスリストに値を格納していく
    data_bytes = distinguished[1]

    for dev in single_list:
        byte_length = dev.fxdatatype.get_word_length() * 2
        dev.set_value_from_bytes(data_bytes[count:count+byte_length])
        count += byte_length

    for dev in double_list:
        byte_length = dev.fxdatatype.get_word_length() * 2
        dev.set_value_from_bytes(data_bytes[count:count+byte_length])
        count += byte_length

    return 0

def set_device_random(device_list: List[FxDevice]):
    rqst_bytes = bytearray(                         #
        config.MONITOR_TIMER.to_bytes(2, 'little')) # 監視タイマ(2byte)
        
    rqst_bytes.extend(tools.Eth.get_command_bytes(MCCommand.Write_Random))  # コマンドを示すデータバイト
        
    # single word とdouble word を分ける    ※良いgroupbyが見つからなかった
    single_list:List[FxDevice] =[]
    double_list:List[FxDevice] =[]
    for dev in device_list:
        if dev.fxdatatype.get_word_length() == 1: single_list.append(dev)
        elif dev.fxdatatype.get_word_length() == 2: double_list.append(dev)

    rqst_bytes.extend(len(single_list).to_bytes(1, 'little'))   # singleデータ長さ(1byte)
    rqst_bytes.extend(len(double_list).to_bytes(1, 'little'))   # doubleデータ長さ(1byte)

    for dev in single_list:
        rqst_bytes.extend(tools.Eth.get_device_bytes(dev))    # デバイス名＋デバイスコード
        rqst_bytes.extend(dev.value_to_bytes())
        pass

    for dev in double_list:
        rqst_bytes.extend(tools.Eth.get_device_bytes(dev))
        rqst_bytes.extend(dev.value_to_bytes())
        pass

    sd_data = tools.Eth.get_route_bytes()            # アクセス経路まで
    sd_data.extend(len(rqst_bytes).to_bytes(2, 'little'))   # 要求データ長さ(2byte)
    sd_data.extend(rqst_bytes)                              # 要求データ

    recievedData = tools.socket_send(sd_data)    # ソケットで送信

    if recievedData == None:                                # 通信失敗
        return None
    
    distinguished = tools.distinguish_reciedved_data(recievedData)   # データ判別
    ret_code = distinguished[0]
    return ret_code


def buffer_test():                  # 20.03.20 不要だが、20.03.30 くらいまで残しておく
    data = bytearray([
        0x00,0x00,                  # デバイス修飾間接指定 (デバイス用の Zインデックス の事)[20.03.19 これを忘れていた]
        0x46,0x00,0x00,             # デバイス番号 3byte = 46(dec) = 0x70(hex)
        0xAB,                       # デバイスコード 1byte
        0x00,0x00,                  # 拡張指定修飾　拡張番号に付くインデックス番号 2byte
        0x01,0x00,                  # 拡張指定　ユニット番号やリンク先番号 2byte
        0xF8,                       # 1byte

        0x01, 0x00                  # デバイス点数(2byte)
    ])
    pass


