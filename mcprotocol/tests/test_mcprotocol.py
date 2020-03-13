import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import mcprotocol
from mcprotocol.classes import CpuType, Protocol
from mcprotocol.fxdevice import FxDataType

import unittest

# この様に設定する
mcprotocol.config.DESTINATION_IP = '192.168.1.15'
mcprotocol.config.DESTINATION_PORT = 6001
mcprotocol.config.PROTOCOL = Protocol.TCP_IP

# CPU 毎に通信プロトコルが異なるので、
# クラス生成時に CPU情報を入れる事でプロトコル判断を行う
mc_proc = mcprotocol.MCProtocol(cpu_type= CpuType.FX5UCPU)

# 今のままだと bytearray が返る
mc_proc.get_device('D100', FxDataType.Signed16)

print('hoge')
