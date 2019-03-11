import binascii
import socket as syssock
import struct
import sys
import thread
import random
import time

receiver = -1
transmitter = -1
header_len = struct.calcsize('!BBBBHHLLQQLL')
sock352PktHdrFmt = '!BBBBHHLLQQLL'  # Fmt for Version 1
acknowledge_no = None
sequence_no = None
fin_received = False
error = False
other_address = None
last_acked = 0
data_to_return = ''
finished = False
FRAGMENT_SIZE = 60000

SYN = 0x01  # Connection initiation
DATA = 0x03  # Packet specifying data payload_len
FIN = 0x02  # Connection end
ACK = 0x04  # Acknowledgement
RESET = 0x08  # Reset connection
HAS_OPT = 0xA0  # Option field is valid


# these functions are global to the class and
# define the UDP ports all messages are sent
# and received from

def init(UDPportTx, UDPportRx):  # initialize your UDP socket here
    global receiver, transmitter
    if int(UDPportRx) == 0:
        receiver = 27182
    else:
        receiver = int(UDPportRx)
    if UDPportTx == '':
        sys.exit('Both ports need to be initialized for this implementation as it uses two sockets!')
    else:
        transmitter = int(UDPportTx)


class socket:
    tSocket = None
    rSocket = None

    def __init__(self):
        global tSocket, rSocket
        tSocket = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)
        rSocket = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)
        rSocket.bind(('', receiver))
        print('Sockets for sending and receiving have been initialized')
        return

    def bind(self, address):
        return

    def connect(self, address):
        global sequence_no, acknowledge_no, other_address
        print('Connecting. . .')
        other_address = (address[0], transmitter)
        sequence_no = random.randint(1, 255)
        s_header = self.__create_header(SYN, sequence_no, 0, 0)
        tSocket.sendto(s_header, other_address)
        packet = rSocket.recv(header_len)
        r_header = struct.unpack(sock352PktHdrFmt, packet)
        if SYN == r_header[1] and sequence_no == r_header[9]:
            acknowledge_no = r_header[8]
        else:
            sys.exit('Error while attempting to connect either SYN flag missing or no ack_no wasn\'t right')
        tSocket.connect(other_address)
        print('Successfully connected')
        return

    def listen(self, backlog):
        return

    def accept(self):
        global sequence_no, acknowledge_no, other_address
        print('Accepting connections . . .')
        r_packet, address = rSocket.recvfrom(header_len)
        other_address = (address[0], transmitter)
        r_header = struct.unpack(sock352PktHdrFmt, r_packet)
        if SYN == r_header[1]:
            acknowledge_no = r_header[8]
            sequence_no = random.randint(1, 250)  # must fit in byte and be able be incremented several times
            s_header = self.__create_header(SYN, sequence_no, acknowledge_no, 0)
            tSocket.sendto(s_header, other_address)  # ack their seq_no with SYN for connection
            client_socket = self
        else:
            sys.exit('Error while attempting to accept SYN flag missing')
        print('Successfully accepted connection')
        return client_socket, other_address

    def close(self):
        global rSocket
        print("Closing . . .")
        rSocket.close()

    def send(self, buffer):
        print("Starting send . . .")
        global last_acked, finished
        last_acked = 0
        remainder = 0
        fragments = 0
        size = len(buffer)
        finished = False
        packets = list()
        bytes_sent = 0
        go_back_i = False
        fragment = 0
        i = 0
        start = 0
        if size > FRAGMENT_SIZE:
            fragments = len(buffer) / FRAGMENT_SIZE
            remainder = len(buffer) % FRAGMENT_SIZE
            size = FRAGMENT_SIZE

        while i <= fragments or go_back_i:
            total_sent = 0
            print(i)

            if go_back_i:
                i = last_acked + 1
                print("Had to go back n")
                size = len(packets[i])
                go_back_i = False

            elif fragments > 0:

                if i == fragments and remainder > 0:
                    # if len(buffer) % FRAGMENT_SIZE > 0 and all full fragments have been sent
                    size = remainder
                    fragment = buffer[bytes_sent:]

                elif i == fragments and remainder == 0:
                    # if there FRAGMENT_SIZE divided len(buffer) perfectly and there's no remainder
                    break

                else:
                    fragment = buffer[bytes_sent:bytes_sent + FRAGMENT_SIZE]  # get next FRAGMENT_SIZE
            else:
                # if return_data is smaller than one FRAGMENT_SIZE
                fragment = buffer[:]

            # checks if ith packet occurs at the end so not to add packets twice if go_back_i
            if i == len(packets):
                header = self.__create_header(DATA, i, 0, size)
                packets.append(header+fragment)
                # print('Inside if  i==len(packets)    i:  ' + str(i) + ' len(packets): ' + str(len(packets[i])))

            while total_sent < len(packets[i]):
                sent = tSocket.sendto((packets[i])[total_sent:], other_address)
                if sent == 0:
                    raise RuntimeError("socket broken")
                else:
                    print('Total sent bytes: ' + str(sent))
                    total_sent += sent

            bytes_sent += total_sent - header_len

            if start:

                if last_acked == i - 1 or last_acked == i:
                    start = time.time()
                elif last_acked > i:
                    i = last_acked
                elif last_acked < i - 1 and time.time() - start >= 0.002:  # timeout never occurs so need other condition
                    go_back_i = True
                else:
                    print('\n\n In else, time is: ' + str(time.time() - start) + ' i: ' + str(i) + ' last_acked: ' + str(last_acked))

            else:
                start = time.time()
                thread.start_new_thread(self.__receive, ())

            i += 1

        finished = True
        return bytes_sent

    def __receive(self):
        print("Started receiving ack packets for send . . .")
        global last_acked
        while not finished:
            r_header = rSocket.recv(header_len)
            header = struct.unpack(sock352PktHdrFmt, r_header)
            last_acked = header[9]
        return

    def recv(self, nbytes):
        print('Receiving nbytes: ' + str(nbytes))
        i = 0
        fragments = 0
        remainder = 0
        return_data = ""
        if nbytes > FRAGMENT_SIZE:
            fragments = nbytes / FRAGMENT_SIZE
            remainder = nbytes % FRAGMENT_SIZE
        print('Fragments: ' + str(fragments))
        if fragments == 0:
            # fragments is 0 because nbytes wasn't great enough to be divded by FRAGMENT_SIZE
            fragment = rSocket.recv(nbytes+header_len)
            packet, msg = fragment[:header_len], fragment[header_len:]
            print('Header length: ' + str(header_len))
            print('Len of packet: ' + str(len(packet)))
            packet = struct.unpack(sock352PktHdrFmt, packet)  # don't need the packet there's only one being sent
            # Don't send ack_packet because send finishes too fast
            return_data = msg
        while i < fragments:
            fragment = ''
            size = FRAGMENT_SIZE + header_len

            while size > 0:
                print('Size: ' + str(size) + ' i: ' + str(i) + ' fragments: ' + str(fragments))
                if size >= FRAGMENT_SIZE+header_len:
                    fragment = rSocket.recv(FRAGMENT_SIZE+header_len)
                else:
                    fragment = rSocket.recv(size)
                size -= len(fragment)
            packet, msg = fragment[:header_len], fragment[header_len:]
            packet = struct.unpack(sock352PktHdrFmt, packet)
            if i == packet[8]:
                return_data += msg  # The data after all the header fields
                ack_packet = self.__create_header(ACK, 0, i, 0)
                tSocket.sendto(ack_packet, other_address)
                i += 1
            else:
                continue
        if remainder > 0:
            fragment = ''
            size = remainder + header_len
            while size > 0:
                if size >= remainder+header_len:
                    fragment = rSocket.recv(header_len+remainder)
                else:
                    fragment = rSocket.recv(size)
                size -= len(fragment)
            packet, msg = fragment[:header_len], fragment[header_len:]
            packet = struct.unpack(sock352PktHdrFmt, packet)
            if i == packet[8]:
                return_data += msg
                ack_packet = self.__create_header(ACK, 0, i, 0)
                tSocket.sendto(ack_packet, other_address)
        return return_data

    def __create_header(self, flags, seq_no, ack_no, payload_len):
        # print('Flag: ' + str(flags) + ' Seq_no: ' + str(seq_no) + ' Ack_no: ' + str(ack_no) + ' payload_len: ' + str(payload_len))
        packet_header = struct.Struct(sock352PktHdrFmt)
        return packet_header.pack(0x1, flags, 0x0, 0x0, header_len, 0x0, 0x0, 0x0, seq_no, ack_no, 0x0, payload_len)
