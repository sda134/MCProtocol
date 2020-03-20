## MCProtocol
三菱PLCとの通信（開発途中）

## Demo
    import mcprotocol
    from mcprotocol.classes import CpuType, Protocol
    from mcprotocol.fxdevice import FxDevice, FxDataType

    # この様に設定する
    mcprotocol.config.DESTINATION_IP = '192.168.3.250'
    mcprotocol.config.DESTINATION_PORT = 6001
    mcprotocol.config.PROTOCOL = Protocol.TCP_IP

    # CPU 毎に通信プロトコルが異なるので、
    # クラス生成時に CPU情報を入れる事でプロトコル判断を行う
    mc_proc = mcprotocol.MCProtocol(cpu_type= CpuType.FX5UCPU)

    # 単一デバイスの読み書き
    ret_wr = mc_proc.set_device('D100', 123, FxDataType.Signed16)    
    ret_rd = mc_proc.get_device('D100', FxDataType.Signed16)
    print (ret_rd)
    # > [123]

    # ユニットデバイスの読み込み
    unit_buff_rd = mc_proc.get_device('U1\\G70', FxDataType.Signed16)