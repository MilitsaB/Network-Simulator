import socket
import sys
import random
from threading import Timer

from shared.PacketTypes import PacketTypes
from shared.Window import SendingWindow
from shared.ReceiveWindow import ReceiveWindow
from shared.packet import Packet
from shared.PacketHelper import PacketHelper
from shared.Window import ReceivingWindow

packet_types = PacketTypes()
max_sequence_number = 10


class UDPHelper:
    # Helper class for UDP communication
    def __init__(self, timeout, conn, peer_ip_addr, peer_port, router_addr, router_port):
        self.conn = conn
        self.peer_ip_addr = peer_ip_addr
        self.peer_port = peer_port
        self.router_addr = router_addr
        self.router_port = router_port
        self.timeoutCount = 30
        self.timeout = timeout
        self.clocks_stopped = False
        self.receive_window = ReceiveWindow(self)

    def initiate_handshake(self, peer_ip_addr, peer_port):
        # send SYN packet
        initial_seq_num = 0

        syn_packet = Packet(packet_types.SYN, initial_seq_num, peer_ip_addr, peer_port, '')
        received_synack = False
        timeoutIterations = 0
        while not received_synack:
            try:
                self.conn.sendto(syn_packet.to_bytes(), (self.router_addr, self.router_port))
                self.conn.settimeout(2)
                synack_packet, sender = self.conn.recvfrom(1024)
                synack_packet = Packet.from_bytes(synack_packet)
                if synack_packet.packet_type == packet_types.SYNACK:
                    received_synack = True
                    print("Received SYNACK packet")
                    next_seq_num = synack_packet.seq_num + 1
                    print("Sending ACK to SYNACK packet")
                    ack_packet = Packet(packet_types.ACK, next_seq_num, peer_ip_addr, peer_port, 'handshake'.encode())
                    self.conn.sendto(ack_packet.to_bytes(), (self.router_addr, self.router_port))
                    print("Sent ACK to SYNACK packet")

            except socket.timeout:
                timeoutIterations += 1
                if timeoutIterations > self.timeoutCount:
                    print("Timeout exceeded")
                    sys.exit()
                print("No response after 1s, resending SYN packet")
                continue

    def receive_handshake(self, packet, sender):
        initial_seq_num = random.randint(0, 2 ** 32)
        if packet.packet_type == packet_types.SYN:
            print("Received SYN packet")
            synack_packet = Packet(packet_types.SYNACK, initial_seq_num, packet.peer_ip_addr, packet.peer_port, '')
            print("Sending SYNACK packet")
            self.conn.sendto(synack_packet.to_bytes(), sender)
            print("Sent SYNACK packet")
        if packet.packet_type == packet_types.ACK:
            print("Received ACK packet, handshake is_done")
            return True
        return False

    def send_data(self, packet_array):
        # send packets packet
        for packet in packet_array:
            self.conn.sendto(packet.to_bytes(), (self.router_addr, self.router_port))
            print("Sent packets packet")

    def send(self, packet_array):
        packets = PacketHelper.to_packets(packet_types.DATA, 10, self.peer_ip_addr, self.peer_port,
                                          packet_array, 'sending')
        sender_window = SendingWindow(packets)
        window_frames_clock = {}

        self.send_window_data(sender_window, window_frames_clock)
        no_reply = False
        timeout_count = 0

        while not sender_window.is_done or no_reply:
            try:
                response, sender = self.conn.recvfrom(1024)
                packet = Packet.from_bytes(response)
                print('Received ' + packet_types.to_string(packet.packet_type) + str(packet.seq_num))

                if packet.packet_type == packet_types.ACK:
                    packets_ack = sender_window.move_window(packet.seq_num)
                    self.stop_clock(window_frames_clock, packets_ack)
                    self.send_window_data(sender_window, window_frames_clock)

                elif packet.packet_type == packet_types.NAK:
                    sender_window.move_window((packet.seq_num - 1) % max_sequence_number)
                    self.send_packet(sender_window.get_packets_data(packet.seq_num))
                    if packet.seq_num in window_frames_clock:
                        self.set_packet_clock([window_frames_clock[packet.seq_num]])

                elif packet.packet_type == packet_types.FIN_RECEIVE:
                    sender_window.is_done = True
                    print("All packets have been sent")
                    break
            except socket.timeout:
                if not no_reply:
                    timeout_count += 1
                    print("Timeout, resending:")
                    self.send_window_data(sender_window, window_frames_clock)
                    if timeout_count > self.timeoutCount:
                        no_reply = True
                        break
                    else:
                        continue
        self.clocks_stopped = True
        if no_reply:
            return False
        return True

    def send_packet(self, packet):
        print(packet)
        if packet is not None and self.conn is not None:
            print('Sending ' + packet_types.to_string(packet.packet_type) + '#' + str(packet.seq_num))
            print(packet)
            self.conn.sendto(packet.to_bytes(), (self.router_addr, self.router_port))

    def receive_data(self, packet):
        # receive packets packet
        print("Received packets packet *****COUNT")
        if packet.packet_type == packet_types.DATA:

            # send ACK packet
            ack_packet = Packet(packet_types.ACK, packet.seq_num, packet.peer_ip_addr, packet.peer_port, '')
            self.conn.sendto(ack_packet.to_bytes(), (self.router_addr, self.router_port))
            print("Adding to receive window")
            self.receive_window.add_packet(packet)
            print("Sent ACK packet")
        elif packet.packet_type == packet_types.FIN:
            print("Received FIN packet")
            self.receive_window.add_packet(packet)
            # send ACK packet
            ack_packet = Packet(packet_types.FIN, packet.seq_num, packet.peer_ip_addr, packet.peer_port, '')
            self.conn.sendto(ack_packet.to_bytes(), (self.router_addr, self.router_port))
            print("Sent ACK packet")

    def receive_response(self):
        rec_window = ReceivingWindow()
        timeout_count = 0
        while not rec_window.buffer_is_done:
            try:
                response, sender = self.conn.recvfrom(1024)
                packet = Packet.from_bytes(response)
                if packet.packet_type in [packet_types.DATA]:
                    self.handle_rec_packet(packet, rec_window)
                if packet.packet_type in [packet_types.FIN_SEND]:
                    self.handle_rec_packet(packet, rec_window, packet_types.FIN_RECEIVE)
            except socket.timeout:
                timeout_count += 1
                print("Timeout, resending:")
                if timeout_count > self.timeoutCount:
                    print("No response. Exiting...")
                    sys.exit()
                else:
                    continue
        print("Packets have been received, buffer extracted")
        return rec_window.buffer

    def handle_rec_packet(self, packet, rec_window, final_packet_type=None):
        print('Receiving' + packet_types.to_string(packet.packet_type) + '#' + str(packet.seq_num))
        seq_num, packet_type = rec_window.add_packet(packet)
        if final_packet_type is not None:
            packet_type = packet_type

        packet_to_send = Packet(
            packet_type=packet_type,
            seq_num=seq_num,
            peer_ip_addr=packet.peer_ip_addr,
            peer_port=packet.peer_port,
            payload=''
        )
        self.send_packet(packet_to_send)

    def send_window_data(self, window, window_frames_clock):
        for packet in window.get_packets_data():
            if packet is not None:
                window_frames_clock[packet.seq_num] = {"packet": packet, "ack": False}
                self.set_packet_clock([window_frames_clock[packet.seq_num]])
                self.send_packet(packet)

    def set_packet_clock(self, packet_status):
        Timer(self.timeout, self.manage_clock, packet_status).start()

    def manage_clock(self, packet_status):
        if not self.clocks_stopped and not packet_status['ack']:
            self.send_packet(packet_status['packet'])

    def stop_clock(self, window_frames_clock, packets_done):
        for packet in packets_done:
            if packet in window_frames_clock:
                window_frames_clock[packet]['ack'] = True

