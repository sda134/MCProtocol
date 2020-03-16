#!/usr/bin/env python
#coding: UTF-8

import socket
from typing import Optional, List, Dict

from itertools import groupby

from . import config, device_dict
from .fxdevice import FxDevice, FxDataType
from .classes import EtherFrame, CPUSeries


# アクセス経路  ※動的な変化に対応できない見直しの余地あり。
if(config.ETHERNET_FRAME == EtherFrame.Ether_4E):
    __route_bytes = bytearray([0x50,0x00,0x00,0x00,0x00,0x00])
else:
    __route_bytes = bytearray([0x50,0x00])

__route_bytes.append(config.NETWORK_NUMBER)              # ネットワーク番号
__route_bytes.append(config.PC_NUMBER)                   # PC番号
__route_bytes.extend(config.I_O_NUMBER.to_bytes(2, 'little')) # 要求先ユニットI/O番号
__route_bytes.append(config.UNIT_NUMBER)                 # ユニット局番


# このあたりの _で始まるメソッドは置き場所を変える。さもないと，使用側から丸見えでスッキリしない

def _distinguish_reciedved_data(recieved_data:bytearray):
    if(config.ETHERNET_FRAME == EtherFrame.Ether_4E):
        start = 9
    else:
        start = 7
    data_length = int.from_bytes(recieved_data[start:start+2], 'little')
    ret_code = int.from_bytes(recieved_data[start+2:start+4], 'little')
    data_bytes:bytearray = bytearray([])
    if data_length > 2:
        data_bytes = recieved_data[start+4:]

    return ret_code, data_bytes



        
# メソッドの中身がえらく長くなってしまったので、再度考え直す事
def get_device_list(device_list:List[FxDevice]):    # MCProtocol的にはこっちがメインメソッドらしい
    rqst_bytes = bytearray(                         #
        config.MONITOR_TIMER.to_bytes(2, 'little')) # 監視タイマ(2byte)
    is_all_bit = False                              # 全てビットなら，「ビット単位での電文」を利用する
    if is_all_bit:                                  # 但し「ビット単位の電文」の実装をする気は今のところない　20.03.13 
        if config.CPU_SERIES == CPUSeries.iQ_R:
            rqst_bytes.extend([0x01,0x04,0x03,0x00])   # ビット，iQ-R
        else:
            rqst_bytes.extend([0x01,0x04,0x01,0x00])   # ビット，Q/L
    else:
        if config.CPU_SERIES == CPUSeries.iQ_R:
            rqst_bytes.extend([0x01,0x04,0x02,0x00])   # ワード，iQ-R
        else:
            rqst_bytes.extend([0x01,0x04,0x00,0x00])   # ワード，Q/L
    
    dev_length = 0
    for fx_dev in device_list:
        rqst_bytes.extend(device_dict.get_device_bytes(fx_dev)) # 対象デバイス：番号＋コード
        dev_length += fx_dev.fxdatatype.get_word_length()

    rqst_bytes.extend(dev_length.to_bytes(2, 'little'))   # デバイス数

    # ここから送信データの作成
    sd_data = __route_bytes                                 # アクセス経路まで
    sd_data.extend(len(rqst_bytes).to_bytes(2, 'little'))   # 要求データ長さ(2byte)
    sd_data.extend(rqst_bytes)                              # 要求データ

    recievedData = __send_socket_data(sd_data)               # ソケットで送信
    if recievedData == None:                                # 通信失敗
        return None
    
    distinguished = _distinguish_reciedved_data(recievedData)   # データ判別
    ret_code = distinguished[0]
    if not ret_code == 0:                                   # 通信は成功したが、エラー電文が返ってきた
        return ret_code

    count = 0                                               # デバイスリストに値を格納していく
    data_bytes = distinguished[1]
    for dev in device_list:
        byte_length = dev.fxdatatype.get_word_length() * 2
        dev.set_value_from_bytes(data_bytes[count:count+byte_length])
        count += byte_length
    return ret_code



def set_device_list(start_device:str, device_list:List[FxDevice]):
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
    pass


# もう不要 03.20 くらいに削除
def set_device_random_test():
    sd_data = bytearray([
        0x50,0x00,                # 要求電文を示す(2byte)
        0x00,                     # ネットワーク番号
        0xFF,                     # PC番号
        0xFF,0x03,                # 要求先ユニットI/O番号
        0x00,                     # 要求先ユニット局番号

        0x20,0x00,          # 要求データ長さ(2byte)
        0x10,0x00,          # 監視タイマ(2byte)

        0x02, 0x14,         # コマンド
        0x00, 0x00,         # サブコマンド
        0x04, 0x00,         # デバイス点数
        0x00, 0x00,0x00,    # デバイス番号 single １点目
        0xA8,               # デバイスコード single １点目
        0x50, 0x05,
        0x01, 0x00,0x00,    # デバイス番号 single １点目
        0xA8,               # デバイスコード single １点目
        0x75, 0x05,
        0x64, 0x00,0x00,    # デバイス番号 single １点目
        0x90,               # デバイスコード single １点目
        0x40, 0x05,
        0x20, 0x00,0x00,    # デバイス番号 single １点目
        0x9C,               # デバイスコード single １点目
        0x83, 0x05,
    ])

    recievedData = __send_socket_data(sd_data)               # ソケットで送信


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
        rqst_bytes.extend(device_dict.get_device_bytes(dev))    # デバイス名＋デバイスコード：single word
        pass

    for dev in double_list:
        rqst_bytes.extend(device_dict.get_device_bytes(dev))    # デバイス名＋デバイスコードdouble word
        pass

    sd_data = __route_bytes                                 # アクセス経路まで
    sd_data.extend(len(rqst_bytes).to_bytes(2, 'little'))   # 要求データ長さ(2byte)
    sd_data.extend(rqst_bytes)                              # 要求データ

    recievedData = __send_socket_data(sd_data)               # ソケットで送信

    if recievedData == None:                                # 通信失敗
        return None
    
    distinguished = _distinguish_reciedved_data(recievedData)   # データ判別

    count = 0                                               # デバイスリストに値を格納していく
    data_bytes = distinguished[1]

    for dev in single_list:
        byte_length = dev.fxdatatype.get_word_length() * 2
        dev.set_value_from_bytes(data_bytes[count:count+byte_length])
        count += byte_length
        pass

    for dev in double_list:
        byte_length = dev.fxdatatype.get_word_length() * 2
        dev.set_value_from_bytes(data_bytes[count:count+byte_length])
        count += byte_length
        pass


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
        rqst_bytes.extend(device_dict.get_device_bytes(dev))    # デバイス名＋デバイスコード
        rqst_bytes.extend(dev.value_to_bytes())
        pass

    for dev in double_list:
        rqst_bytes.extend(device_dict.get_device_bytes(dev))
        rqst_bytes.extend(dev.value_to_bytes())
        pass

    sd_data = __route_bytes                                 # アクセス経路まで
    sd_data.extend(len(rqst_bytes).to_bytes(2, 'little'))   # 要求データ長さ(2byte)
    sd_data.extend(rqst_bytes)                              # 要求データ

    recievedData = __send_socket_data(sd_data)               # ソケットで送信

    if recievedData == None:                                # 通信失敗
        return None
    
    distinguished = _distinguish_reciedved_data(recievedData)   # データ判別
    ret_code = distinguished[0]
    return ret_code


def __send_socket_data(sending_data:bytearray) -> Optional[bytearray]:    
    host = config.DESTINATION_IP    # なぜか一度変数にしないと
    port = config.DESTINATION_PORT  # 通信が拒否される
    recievedData = None

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
            soc.connect((host, port))
            print('Sending:', repr(sending_data))
            soc.sendall(sending_data)
            recievedData = soc.recv(1024)
            print('Received:', repr(recievedData))    
    except TimeoutError:
        print ('Timeout')
        pass
    except Exception as e:
        print ('Exception: %s' % e)
    else:
        pass
    return recievedData


