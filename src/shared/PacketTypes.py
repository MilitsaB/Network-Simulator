class PacketTypes:
    @property
    def DATA(self):
        return 0
    @property
    def ACK(self):
        return 1
    @property
    def NAK(self):
        return 2
    @property
    def SYN(self):
        return 3
    @property
    def SYNACK(self):
        return 4
    @property
    def FIN(self):
        return 5
    @property
    def FINACK(self):
        return 6
    @property
    def FIN_RECEIVE(self):
        return 7

    @property
    def FIN_SEND(self):
        return 8

    @staticmethod
    def to_string(packet_type):
        if packet_type == 0:
            return "DATA"
        elif packet_type == 1:
            return "ACK"
        elif packet_type == 2:
            return "NAK"
        elif packet_type == 3:
            return "SYN"
        elif packet_type == 4:
            return "SYNACK"
        elif packet_type == 5:
            return "FIN"
        elif packet_type == 6:
            return "FINACK"
        elif packet_type == 7:
            return "FIN_RECEIVE"
        elif packet_type == 8:
            return "FIN_SEND"
        else:
            return "UNKNOWN"

