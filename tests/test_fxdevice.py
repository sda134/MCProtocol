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
fx_d = FxDevice('D100', FxDataType.Signed16)
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

print('[D dev]\trepr:%s\tis_extended:%s' % (repr(fx_d), fx_d.is_extended_device))
print('[M dev]\trepr:%s\tis_extended:%s' % (repr(fx_m), fx_m.is_extended_device))
print('[index]\trepr:%s\tis_extended:%s' % (repr(fx_index), fx_index.is_extended_device))
print('[unit]\trepr:%s\tis_extended:%s' % (repr(fx_unit), fx_unit.is_extended_device))
print('[rcpu]\trepr:%s\tis_extended:%s' % (repr(fx_rcpu), fx_rcpu.is_extended_device))
