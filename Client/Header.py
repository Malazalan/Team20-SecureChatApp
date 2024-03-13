from enum import Enum


HEADER_LENGTH = 16

class Message_Type(Enum):
    METADATA = 0
    TEXT = 1
    FILE = 2


def bytes_to_header(header_bytes):
    return Header(header_bytes[0], int.from_bytes(header_bytes[1:], "little"))
class Header:
    def __init__(self, message_type, number_of_packets):
        self.type = message_type
        self.number_of_packets = number_of_packets

    def get_header_bytes(self):
        byte_header = (self.type).value.to_bytes(1, byteorder='little') + self.number_of_packets.to_bytes((HEADER_LENGTH - 1), byteorder='little')
        return byte_header
