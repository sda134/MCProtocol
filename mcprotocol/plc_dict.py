'''
シーケンサ毎の Frame判別を行います。
'''

from .classes import EtherFrame, SerialFrameID, CpuType, CPUSeries, UnitControl

EtherFrame = {
    CpuType.FX3UCCPU: EtherFrame.Ether_1E,
    CpuType.FX5UCPU: EtherFrame.Ether_3E, 
    CpuType.Q03UDVCPU: EtherFrame.Ether_3E,
    }

SerialFrame = {
    CpuType.FX3UCCPU: SerialFrameID.Serial_1C,
    CpuType.FX5UCPU: SerialFrameID.Serial_3C, 
    CpuType.Q03UDVCPU: SerialFrameID.Serial_3C,
    }

CPU_Series = {
    CpuType.FX3UCCPU: CPUSeries.F_Series,
    CpuType.FX5UCPU: CPUSeries.iQ_F,
    CpuType.Q03UDVCPU: CPUSeries.Q_Series,
}