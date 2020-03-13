#!/usr/bin/env python
#coding: UTF-8

import socket
from . import config
from .classes import EtherFrame

'''
1E は電文の形式が全く異なるので、別モジュールを作成して対応する
'''


def get_device_list():
    pass