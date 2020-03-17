import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest

import mcprotocol
from mcprotocol.classes import CpuType
from mcprotocol.fxdevice import FxDevice, FxDataType, UnitDevice


# CPU 毎に通信プロトコルが異なるので、
# クラス生成時に CPU情報を入れる事でプロトコル判断を行う


# 通常使用のテスト
fx1 = FxDevice('D100', fx_data_type= FxDataType.Float)
fx1.value = 3.14159
byte_data1 = fx1.value_to_bytes()
for b in byte_data1:
    print(int(b))

# byte変換のテスト
fx2 = FxDevice('D102')
fx2.fxdatatype = FxDataType.Float   # 後でデータ型を変える

fx2.set_value_from_bytes([0x01,0x02,0x03,0x04,0x05])    # byte数不足
fx2.set_value_from_bytes([0x01,0x02,0x03])              # byte数過多
byte_data2 = fx2.value_to_bytes()
print('hoge')


test_str = '1'
test = int(test_str)
unit1 = UnitDevice('U1\\D6016')