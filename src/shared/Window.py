from shared.PacketTypes import PacketTypes

packet_types = PacketTypes()

max_sequence_number = 10
window_size = int(max_sequence_number / 2)


class SendingWindow:
    def __init__(self, data):
        self.packets = data
        self.packets_current_index = 0
        self.current_sequence_number = 0
        self.window = self.set_window(0, window_size)
        self.is_done = False

    def get_packets_data(self, sequence_number=None):
        if sequence_number is None:
            return [packet for packet in self.window]
        elif self.is_valid_sequence(sequence_number):
            for packet in self.window:
                if packet.seq_num == sequence_number:
                    return packet
        return None

    def set_window(self, window_start, window_end):
        return self.packets[window_start: min(len(self.packets), window_end)]

    def move_window(self, ack_seq):
        if self.is_valid_sequence(ack_seq):
            to_slide = ((ack_seq - self.current_sequence_number + 1) % max_sequence_number)
            packets_done = range(self.current_sequence_number, (self.current_sequence_number + to_slide) % max_sequence_number)

            next_sequence_number = (self.current_sequence_number + to_slide) % max_sequence_number
            self.current_sequence_number = next_sequence_number
            self.window = self.set_window(self.packets_current_index, self.packets_current_index + to_slide + 1)

            self.packets_current_index = self.packets_current_index + to_slide
            if self.packets_current_index == len(self.packets):
                self.is_done = True

            return [*packets_done]
        else:
            return []

    def is_valid_sequence(self, sequence_number):
        for num in range(self.current_sequence_number,
                         min(len(self.packets), self.current_sequence_number + window_size)):
            if sequence_number == (num % max_sequence_number):
                return True
        return False


class ReceivingWindow:
    def __init__(self, ):
        self.buffer = []
        self.buffer_is_done = False
        self.current_sequence_number = 0
        self.window = self.set_window(0, max_sequence_number)
        self.is_done = False

    def set_window(self, window_start, window_end):
        return dict.fromkeys([sequence_number for sequence_number in range(window_start, window_end)])

    def add_packet(self, packet):
        print('inserting packet ', packet.seq_num)
        if self.is_valid_sequence(packet.seq_num):
            self.window[packet.seq_num] = packet

        current_packet_index = next((packet for packet in self.window if
                                     (self.window[packet] is not None and self.window[
                                         packet].seq_num == self.current_sequence_number)), None)
        if current_packet_index is not None:
            current_packet = self.window[current_packet_index]
            self.buffer.append(current_packet.payload.decode('utf-8'))

            self.window[self.current_sequence_number] = None
            self.current_sequence_number = (self.current_sequence_number + 1) % max_sequence_number

            if current_packet.packet_type == packet_types.FIN_SEND:
                self.buffer_is_done = True
                return (self.current_sequence_number - 1) % max_sequence_number, packet_types.FIN_RECEIVE,

            return (self.current_sequence_number - 1) % max_sequence_number, packet_types.ACK

        else:
            return self.current_sequence_number, packet_types.NAK

    def is_valid_sequence(self, sequence_number):
        for num in range(self.current_sequence_number, self.current_sequence_number + window_size):
            if sequence_number == (num % max_sequence_number):
                return True
        return False
