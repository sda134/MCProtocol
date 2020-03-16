import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
import struct

import mcprotocol
from mcprotocol.classes import CpuType, Protocol
from mcprotocol.fxdevice import FxDevice, FxDataType

# この様に設定する
mcprotocol.config.DESTINATION_IP = '192.168.1.15'
mcprotocol.config.DESTINATION_PORT = 6001
mcprotocol.config.PROTOCOL = Protocol.TCP_IP

# CPU 毎に通信プロトコルが異なるので、
# クラス生成時に CPU情報を入れる事でプロトコル判断を行う
mc_proc = mcprotocol.MCProtocol(cpu_type= CpuType.FX5UCPU)

# 単一デバイスの読み書き
#test1_singledev_16 = mc_proc.get_device('D100', FxDataType.Signed16)
#test1_singledev_32 = mc_proc.get_device('D100', FxDataType.Signed32)
#test1_singledev_fl = mc_proc.get_device('D100', FxDataType.Float)



# ランダムデバイスの読み書き
#dev_list = [
#    FxDevice('D100', FxDataType.Unsigned32, 100),
#    FxDevice('D104', FxDataType.Unsigned32, 20),
#    FxDevice('D108', FxDataType.Float, 2),
#]
#test2_randomdev_wr = mc_proc.set_device_random(dev_list)


dev_list = [
    FxDevice('D100', FxDataType.Signed16, 0),
    FxDevice('D104', FxDataType.Unsigned32, 0),
    FxDevice('D108', FxDataType.Float, 0),
]

test2_randomdev_rd = mc_proc.get_device_random(dev_list)

for dev in dev_list:
    print(repr(dev))
