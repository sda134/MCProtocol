import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
import struct

import mcprotocol
import mcprotocol.mcprotocol_tools as tools
from mcprotocol.classes import MCCommand, Protocol, EtherFrame, SerialFrameID, CPUSeries

#mcprotocol.config.PROTOCOL = Protocol.Serial
#mcprotocol.config.PROTOCOL = Protocol.UDP_IP
mcprotocol.config.PROTOCOL = Protocol.TCP_IP
mcprotocol.config.ETHERNET_FRAME = EtherFrame.Ether_3E
mcprotocol.config.SERIAL_FRAME = SerialFrameID.Serial_1C
mcprotocol.config.CPU_SERIES = CPUSeries.iQ_F

cmd_bytes_rd_list = tools.get_command_bytes(MCCommand.Read_List)
cmd_bytes_wr_list = tools.get_command_bytes(MCCommand.Write_List)
cmd_bytes_rd_random = tools.get_command_bytes(MCCommand.Read_Random)
cmd_bytes_wr_random = tools.get_command_bytes(MCCommand.Write_Random)

print('hoge')