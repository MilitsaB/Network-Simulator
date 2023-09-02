from shared.PacketTypes import PacketTypes
from shared.PacketHelper import PacketHelper

packet_types = PacketTypes()
class ReceiveWindow:
    def __init__(self, udpHelper):
        self.udpHelper = udpHelper
        self.packets = []
        self.payloadReady = False

    def clear(self):
        self.packets.clear()
        self.payloadReady = False

    def add_packet(self, packet):
        self.packets.append(packet)
        self.packets.sort(key=lambda x: x.seq_num)
        self.check_for_payload()


    def check_for_payload(self):
        if len(self.packets) == 0:
            return
        if self.packets[0].seq_num != 0:
            return
        for i in range(len(self.packets) - 1):
            if self.packets[i+1].seq_num - self.packets[i].seq_num != 1:
                return
        if self.packets[-1].packet_type == packet_types.FIN:
            print("Payload ready")
            self.payloadReady = True
        return

