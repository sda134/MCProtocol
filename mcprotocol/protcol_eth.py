#!/usr/bin/env python
#coding: UTF-8

import socket
from typing import (Optional, Union, List, Dict)

from itertools import groupby

from . import config, mcprotocol_tools
from .fxdevice import FxDevice, FxDataType
from .classes import EtherFrame, CPUSeries



def get_device_list(start_device:str, device_count:int, fx_datatype: FxDataType = FxDataType.Signed16 )-> Union[None,int, List[Union[int,float]]]:    # MCProtocol的にはこっちがメインメソッドらしい
    rqst_bytes = bytearray(                         #
        config.MONITOR_TIMER.to_bytes(2, 'little')) # 監視タイマ(2byte)
    is_all_bit = False                              # 全てビットなら，「ビット単位での電文」を利用する
    if is_all_bit:                                  # 但し「ビット単位の電文」の実装をする気は今のところない　20.03.13 
        if config.CPU_SERIES == CPUSeries.iQ_R:
            rqst_bytes.extend([0x01,0x04,0x03,0x00])   # ビット，iQ-R　(コマンド2byte, サブコマンド2byte)
        else:
            rqst_bytes.extend([0x01,0x04,0x01,0x00])   # ビット，Q/L
    else:
        if config.CPU_SERIES == CPUSeries.iQ_R:
            rqst_bytes.extend([0x01,0x04,0x02,0x00])   # ワード，iQ-R
        else:
            rqst_bytes.extend([0x01,0x04,0x00,0x00])   # ワード，Q/L

    fx_dev = FxDevice(start_device)                                     # 開始デバイス
    rqst_bytes.extend(mcprotocol_tools.get_device_bytes(fx_dev)) 

    word_length = fx_datatype.get_word_length() * device_count          # デバイス点数(2byte) 
    rqst_bytes.extend(word_length.to_bytes(2, 'little'))                # 三菱の仕様から察するに，ここでの「デバイス」はint16の事　本来ならばword数と言うべき。

    sd_data = mcprotocol_tools.get_route_bytes()            # アクセス経路まで
    sd_data.extend(len(rqst_bytes).to_bytes(2, 'little'))   # 要求データ長さ(2byte)
    sd_data.extend(rqst_bytes)                              # 要求データ

    recievedData = mcprotocol_tools.socket_send(sd_data)    # ソケットで送信

    if recievedData == None:                                # 通信失敗
        return None
    
    distinguished = mcprotocol_tools.distinguish_reciedved_data(recievedData)   # データ判別
    ret_code = distinguished[0]

    if not ret_code ==0: return ret_code

    count = 0                                               # デバイスリストに値を格納していく
    data_bytes = distinguished[1]
    value_list = []

    for c in range(device_count):
        dev = FxDevice(start_device, fx_datatype)              # デバイス名（特に番号）は割とどうでも良いために ループ内すべてstart_deviceを使っている。
        byte_length = fx_datatype.get_word_length() * 2        # バイト数
        dev.set_value_from_bytes(data_bytes[count:count+byte_length])   # bytes から値を代入
        value_list.append(dev.value)
        count += byte_length

    return value_list


def set_device_list(start_device:str, value_list: List[Union[int, float]], fx_datatype: FxDataType = FxDataType.Signed16 )-> None:
    rqst_bytes = bytearray(                         #
        config.MONITOR_TIMER.to_bytes(2, 'little')) # 監視タイマ(2byte)

    is_all_bit = False                              # 全てビットなら，「ビット単位での電文」を利用する
    if is_all_bit:                                  # 但し「ビット単位の電文」の実装をする気は今のところない　20.03.13 
        if config.CPU_SERIES == CPUSeries.iQ_R:
            rqst_bytes.extend([0x01,0x14,0x03,0x00])   # ビット，iQ-R
        else:
            rqst_bytes.extend([0x01,0x14,0x01,0x00])   # ビット，Q/L
    else:
        if config.CPU_SERIES == CPUSeries.iQ_R:
            rqst_bytes.extend([0x01,0x14,0x02,0x00])   # ワード，iQ-R
        else:
            rqst_bytes.extend([0x01,0x14,0x00,0x00])   # ワード，Q/L
    
    fx_dev = FxDevice(start_device)                                 # 開始デバイス
    rqst_bytes.extend(mcprotocol_tools.get_device_bytes(fx_dev))    # 先頭デバイス番号＋デバイスコード

    word_length = fx_datatype.get_word_length() * len(value_list)   # デバイス点数(1byte) 
    rqst_bytes.extend(word_length.to_bytes(2, 'little'))            # 三菱の仕様から察するに，ここでの「デバイス」はint16の事　本来ならばword数と言うべき。

    for val in value_list:                                          # 具体的な書き込みデータ　※注意！ここでは生成されるFxDevice のfx_devicetype とvalue だけが重要で、
        dev = FxDevice(start_device, fx_datatype, val)              # デバイス名（特に番号）は割とどうでも良いために ループ内すべてstart_deviceを使っている。
        rqst_bytes.extend(dev.value_to_bytes())

    sd_data = mcprotocol_tools.get_route_bytes()            # アクセス経路まで
    sd_data.extend(len(rqst_bytes).to_bytes(2, 'little'))   # 要求データ長さ(2byte)
    sd_data.extend(rqst_bytes)                              # 要求データ

    recievedData = mcprotocol_tools.socket_send(sd_data)    # ソケットで送信

    distinguished = mcprotocol_tools.distinguish_reciedved_data(recievedData) # データ判別
    ret_code = distinguished[0]
    return ret_code


def get_device_random(device_list:List[FxDevice]):
    rqst_bytes = bytearray(                         #
        config.MONITOR_TIMER.to_bytes(2, 'little')) # 監視タイマ(2byte)
    if config.CPU_SERIES == CPUSeries.iQ_R:
        rqst_bytes.extend([0x03,0x04,0x02,0x00])   # ワード，iQ-R   モニタ条件を指定　は無視 20.03.16
    else:
        rqst_bytes.extend([0x03,0x04,0x00,0x00])   # ワード，Q/L
    
    # single word とdouble word を分ける    ※良いgroupbyが見つからなかった
    single_list:List[FxDevice] =[]
    double_list:List[FxDevice] =[]
    for dev in device_list:
        if dev.fxdatatype.get_word_length() == 1: single_list.append(dev)
        elif dev.fxdatatype.get_word_length() == 2: double_list.append(dev)

    rqst_bytes.extend(len(single_list).to_bytes(1, 'little'))   # single wordデータ長さ(1byte)
    rqst_bytes.extend(len(double_list).to_bytes(1, 'little'))   # double wordデータ長さ(1byte)

    for dev in single_list:
        rqst_bytes.extend(mcprotocol_tools.get_device_bytes(dev))    # デバイス名＋デバイスコード：single word
        pass

    for dev in double_list:
        rqst_bytes.extend(mcprotocol_tools.get_device_bytes(dev))    # デバイス名＋デバイスコードdouble word
        pass

    sd_data = mcprotocol_tools.get_route_bytes()            # アクセス経路まで
    sd_data.extend(len(rqst_bytes).to_bytes(2, 'little'))   # 要求データ長さ(2byte)
    sd_data.extend(rqst_bytes)                              # 要求データ

    recievedData = mcprotocol_tools.socket_send(sd_data)    # ソケットで送信

    if recievedData == None:                                # 通信失敗
        return None
    
    distinguished = mcprotocol_tools.distinguish_reciedved_data(recievedData)   # データ判別

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


def set_device_random(device_list:List[FxDevice]):
    rqst_bytes = bytearray(                         #
        config.MONITOR_TIMER.to_bytes(2, 'little')) # 監視タイマ(2byte)
    is_all_bit = False                              # 全てビットなら，「ビット単位での電文」を利用する
    if is_all_bit:                                  # 但し「ビット単位の電文」の実装をする気は今のところない　20.03.13 
        if config.CPU_SERIES == CPUSeries.iQ_R:
            rqst_bytes.extend([0x02,0x14,0x03,0x00])   # ビット，iQ-R
        else:
            rqst_bytes.extend([0x02,0x14,0x01,0x00])   # ビット，Q/L
    else:
        if config.CPU_SERIES == CPUSeries.iQ_R:
            rqst_bytes.extend([0x02,0x14,0x02,0x00])   # ワード，iQ-R
        else:
            rqst_bytes.extend([0x02,0x14,0x00,0x00])   # ワード，Q/L
    
    # single word とdouble word を分ける    ※良いgroupbyが見つからなかった
    single_list:List[FxDevice] =[]
    double_list:List[FxDevice] =[]
    for dev in device_list:
        if dev.fxdatatype.get_word_length() == 1: single_list.append(dev)
        elif dev.fxdatatype.get_word_length() == 2: double_list.append(dev)

    rqst_bytes.extend(len(single_list).to_bytes(1, 'little'))   # singleデータ長さ(1byte)
    rqst_bytes.extend(len(double_list).to_bytes(1, 'little'))   # doubleデータ長さ(1byte)

    for dev in single_list:
        rqst_bytes.extend(mcprotocol_tools.get_device_bytes(dev))    # デバイス名＋デバイスコード
        rqst_bytes.extend(dev.value_to_bytes())
        pass

    for dev in double_list:
        rqst_bytes.extend(mcprotocol_tools.get_device_bytes(dev))
        rqst_bytes.extend(dev.value_to_bytes())
        pass

    sd_data = mcprotocol_tools.get_route_bytes()                                 # アクセス経路まで
    sd_data.extend(len(rqst_bytes).to_bytes(2, 'little'))   # 要求データ長さ(2byte)
    sd_data.extend(rqst_bytes)                              # 要求データ

    recievedData = mcprotocol_tools.socket_send(sd_data)    # ソケットで送信

    if recievedData == None:                                # 通信失敗
        return None
    
    distinguished = mcprotocol_tools.distinguish_reciedved_data(recievedData)   # データ判別
    ret_code = distinguished[0]
    return ret_code


def get_unit_buffuer():
    rqst_bytes = bytearray(                         #
        config.MONITOR_TIMER.to_bytes(2, 'little')) # 監視タイマ(2byte)
    if config.CPU_SERIES == CPUSeries.iQ_R:
        rqst_bytes.extend([0x00,0x00])   # ビット，iQ-R　(コマンド2byte)
    else:
        rqst_bytes.extend([0x00,0x00])   # ビット，Q/L

