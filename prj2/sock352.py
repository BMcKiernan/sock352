
# CS 352 project part 2 
# this is the initial socket library for project 2 
# You wil need to fill in the various methods in this
# library 

# main libraries 
import binascii
import threading
import socket as syssock
import struct
import sys
import time
from random import randint

# encryption libraries 
import nacl.utils
import nacl.secret
import nacl.utils
from nacl.public import PrivateKey, Box

# if you want to debug and print the current stack frame 
from inspect import currentframe, getframeinfo

# these are globals to the sock352 class and
# define the UDP ports all messages are sent
# and received from

# the ports to use for the sock352 messages 
global sock352portTx
global sock352portRx
# the public and private keychains in hex format 
global publicKeysHex
global privateKeysHex

# the public and private keychains in binary format 
global publicKeys
global privateKeys

# the encryption flag 
global ENCRYPT

publicKeysHex = {} 
privateKeysHex = {} 
publicKeys = {} 
privateKeys = {}

# this is 0xEC 
ENCRYPT = 236 

# this is the structure of the sock352 packet 
sock352HdrStructStr = '!BBBBHHLLQQLL'

#Global variables that stroe the sending and receiving ports of the socket
sock352portTx = 0
sock352portRx = 0

#Global variables that stroe the packet header format and packet header length
#to use within the struct in order to pack and unpack
PACKET_HEADER_FORMAT = "1BBBHHLLQQQLL"
PACKET_HEADER_LENGTH = struct.calcsize(PACKET_HEADER_FORMAT)

#Global variables that are responsible for storing the maximum packet size and the
#maximum payload size
MAXIMUM_PACKET_SIZE = 64000
MAXIMIM_PAYLOAD_SIZE = MAXIMUM_PACKET_SIZE - PACKET_HEADER_LENGTH

#Global variables that define all the packet bits
SOCK352_SYN = 0x01
SOCK352_FIN = 0x02
SOCK352_ACK = 0x04
SOCK352_RESET = 0x08
SOCK352_HAS_OPT = 0x10

#String message to print out that a connection has been already established
CONNECTION_ALREADY_ESTABLISHED_MESSAGE = "This socket supports a maximum of one connection\n" \
                                        "And a connection is already established"

def init(UDPportTx,UDPportRx):
    if (UDPportTx is None or UDPportTx == 0):
        UDPportTx = 27182

    if (UDPportRx is None or UDPportRx == 0):
        UDPportRx = 27182

    global sock352portTx
    global sock352portRx
    sock352portTx = int(UDPportTx)
    sock352portRx = int(UDPportRx)

    # create the sockets to send and receive UDP packets on 
    # if the ports are not equal, create two sockets, one for Tx and one for Rx

    
# read the keyfile. The result should be a private key and a keychain of
# public keys
def readKeyChain(filename):
    global publicKeysHex
    global privateKeysHex 
    global publicKeys
    global privateKeys 
    
    if (filename):
        try:
            keyfile_fd = open(filename,"r")
            for line in keyfile_fd:
                words = line.split()
                # check if a comment
                # more than 2 words, and the first word does not have a
                # hash, we may have a valid host/key pair in the keychain
                if ( (len(words) >= 4) and (words[0].find("#") == -1)):
                    host = words[1]
                    port = words[2]
                    keyInHex = words[3]
                    if (words[0] == "private"):
                        privateKeysHex[(host,port)] = keyInHex
                        privateKeys[(host,port)] = nacl.public.PrivateKey(keyInHex, nacl.encoding.HexEncoder)
                    elif (words[0] == "public"):
                        publicKeysHex[(host,port)] = keyInHex
                        publicKeys[(host,port)] = nacl.public.PublicKey(keyInHex, nacl.encoding.HexEncoder)
        except Exception,e:
            print ( "error: opening keychain file: %s %s" % (filename,repr(e)))
    else:
            print ("error: No filename presented")             

    return (publicKeys,privateKeys)

class socket:
    
    def __init__(self):
        #create the socket
        self.socket = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)

        #sets the timeout to be 0.2 second
        self.socket.settimeout(0.2)

        #sets the send address to be None
        self.send_address = None

        #sets the boolean for whether or not the socket is connected
        self.is_connected = False

        #controls whather or not this socket can close
        self.can_close

        #selects a random sequence number between 1 and 1000000 as the first sequence number
        self.sequence_no = randint(1, 1000000)

        #declares the file length, which will set later
        self.file_len = -1

        #declares the retrasnmit boolean which represents whether or not to resend packets and Go-Back_N
        self.retransmit = False

        #the cooresponding lock for the retransmit boolean
        self.retransmit_lock = threading.Lock()

        #declares the last packet that was acked
        self.last_data_packet_acked = None

        #sets the enctyption state to false
        self.encrypt = False

        return 
        
    def bind(self,address):
        # bind is not used in this assignment 
        return

    def connect(self,*args):
        global privateKeys
        global privateKeysHex
        global publicKeys
        global publicKeysHex
        global udpG


        # example code to parse an argument list (use option arguments if you want)
        global sock352portTx
        global ENCRYPT
        if (len(args) >= 1): 
            (host,port) = args[0]
        if (len(args) >= 2):
            if (args[1] == ENCRYPT):
                self.encrypt = True

        #if the connection is encrypted set get the public and private keys
        if (self.encrypt == True):
            self.box = Box(privateKeys[("*"), "*"], publicKeys[host, sock352portRx])
            self.nonce = nacl.util.random(Box.NONCE_SIZE)

        syn_packet =

    def listen(self,backlog):
        # listen is not used in this assignments 
        pass
    

    def accept(self,*args):
        # example code to parse an argument list (use option arguments if you want)
        global ENCRYPT
        if (len(args) >= 1):
            if (args[0] == ENCRYPT):
                self.encryption = True
        # your code goes here 

    def close(self):
        # your code goes here 
        return 

    def send(self,buffer):
        # your code goes here 
        return 

    def recv(self,nbytes):
        # your code goes here
        return 


    def createPacket(self, flags=0x0, sequence_no=0x0, ack_no=0x0, payload_len=0x0):
        return struct.Struct(PACKET_HEADER_FORMAT).pack \
            (
                0x1, #version
                flags, #flags
                0x0, #opt_ptr
                0x0, #protocol
                PACKET_HEADER_LENGTH,   #header_len
                0x0,     #checksum
                0x0,     #source_port
                0x0,     #window
                payload_len     #payload_len
            )

    


