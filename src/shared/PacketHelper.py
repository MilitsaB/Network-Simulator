from shared.PacketTypes import PacketTypes
from shared.packet import Packet

packet_types = PacketTypes()


class PacketHelper:
    MAX_PAYLOAD_SIZE = 1013

    @staticmethod
    def to_packets(packet_type, max_seq_num, peer_ip_addr, peer_port, payload, server='', max_payload_size=MAX_PAYLOAD_SIZE):
        # first split payload into chunks of max_payload_size
        # to do change synxtax
        payload_chunks = [payload[i:i + max_payload_size] for i in range(0, len(payload.encode()), max_payload_size)]
        # now create packets with each chunk
        packets = []
        for i in range(len(payload_chunks)):
            if i == len(payload_chunks) - 1:
                if server == 'sending':
                    packets.append(
                        Packet(packet_types.FIN_SEND, i % max_seq_num, peer_ip_addr, peer_port,
                               payload_chunks[i].encode()))
                else:
                    packets.append(
                        Packet(packet_types.FIN, i % max_seq_num, peer_ip_addr, peer_port, payload_chunks[i].encode()))
            else:
                packets.append(Packet(packet_type=packet_type,
                                      seq_num=i % max_seq_num,
                                      peer_ip_addr=peer_ip_addr,
                                      peer_port=peer_port,
                                      payload=payload_chunks[i].encode()))
        print('in packet help')
        print(packets)
        return packets

    @staticmethod
    def from_packets(packets):
        payload = b''
        for packet in packets:
            payload += packet.payload
        print()
        return payload.decode()
