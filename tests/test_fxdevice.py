import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest

import mcprotocol
from mcprotocol.classes import CpuType
from mcprotocol.fxdevice import FxDevice, FxDataType


# CPU 毎に通信プロトコルが異なるので、
# クラス生成時に CPU情報を入れる事でプロトコル判断を行う


# 通常使用のテスト
fx_d = FxDevice('D100', fx_data_type= FxDataType.Float)
fx_m = FxDevice('M100', fx_data_type= FxDataType.Float)     # initでFloat を指定してもBitになる事を確認

# byte変換のテスト
#fx_byte = FxDevice('D102')
#fx_byte.fxdatatype = FxDataType.Float   # 後でデータ型を変える
#for b in fx_byte.value_to_bytes():
#    print(int(b))


# 様々な特殊デバイス変換
fx_index = FxDevice('D100Z1')
fx_unit = FxDevice('U1\\G6016')
fx_rcpu = FxDevice('U1\\D100')

print(repr(fx_index))
print(repr(fx_unit))
print(repr(fx_rcpu))
