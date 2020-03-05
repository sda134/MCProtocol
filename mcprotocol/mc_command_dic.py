'''
通信先の PLC 毎の設定を記述します
'''

from .classes import CommunicationFrame, CpuType, UnitControl




UnitControlCommand ={
    UnitControl.RemoteRun : bytearray([0x10,0x10,0x00,0x00,]),
    UnitControl.RemoteStop : bytearray([0x02,0x10,0x00,0x00]),
    UnitControl.RemotePause : bytearray([0x03,0x10,0x00,0x00]),
    UnitControl.RemoteLatchClear : bytearray([0x05,0x10,0x00,0x00]),
    UnitControl.RemoteReset : bytearray([0x05,0x10,0x00,0x00]),
    UnitControl.CPU_Name : bytearray([0x01,0x01,0x00,0x00]),
}