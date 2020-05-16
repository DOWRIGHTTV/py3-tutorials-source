#!/usr/bin/env python3

# if anyone is worndering, the undescores are here to prevent namespace conflictions.
import os as _os
import sys as _sys
import time as _time
import socket as _socket

from struct import Struct as _Struct
from ipaddress import IPv4Address as _IPv4Address

# assigning variables to direct function references.
_fast_time = _time.time
_write_err = _sys.stdout.write

tcp_header_unpack = _Struct('!2H2LB').unpack_from
udp_header_unpack = _Struct('!4H').unpack_from


class RawPacket:
    '''tcp/ip packet represented in class form. packet fields can be accessed via their corresponding attribute.'''

    def __init__(self, data):
        self.timestamp = _fast_time()
        self.protocol  = 0

        self._name = self.__class__.__name__

        self._dlen = len(data)

        # parsing ethernet header here because it is more efficient
        self.dst_mac = data[:6].hex()
        self.src_mac = data[6:12].hex()
        self._data   = data[14:]

    # NOTE: this is very slow to have to print and should only be used for testing or learning. Generally you wouldnt need
    # to print a string representation of the class instance anyways.
    def __str__(self):
        return '\n'.join([
            f'{"="*32}',
            f'{" "*8}PACKET',
            f'{"="*32}',
            f'{" "*8}ETHERNET',
            f'{"-"*32}',
            f'src mac: {self.src_mac}',
            f'dst mac: {self.dst_mac}',
            f'{"-"*32}',
            f'{" "*8}IP',
            f'{"-"*32}',
            f'header length: {self.header_len}',
            f'protocol: {self.protocol}',
            f'src ip: {self.src_ip}',
            f'dst ip: {self.dst_ip}',
            f'{"-"*32}',
            f'{" "*8}PROTOCOL',
            f'{"-"*32}',
            f'src port: {self.src_port}',
            f'dst port: {self.dst_port}',
            f'{"-"*32}',
            f'{" "*8}PAYLOAD',
            f'{"-"*32}',
            f'{self.payload}'
        ])

    def parse(self):
        '''index tcp/ip packet layers 3 & 4 for use as instance objects.'''

        self._ip()
        if (self.protocol == 6):
            self._tcp()

        elif (self.protocol == 17):
            self._udp()

        else:
            _write_err('non tcp/udp packet!\n')

    def _ip(self):
        data = self._data

        self.src_ip = _IPv4Address(data[12:16])
        self.dst_ip = _IPv4Address(data[16:20])

        self.header_len = (data[0] & 15) * 4
        self.protocol  = data[9]
        self.ip_header = data[:self.header_len]

        # removing ip header from data
        self._data = data[self.header_len:]

    # tcp header max len 32 bytes
    def _tcp(self):
        data = self._data

        tcp_header = tcp_header_unpack(data)
        self.src_port   = tcp_header[0]
        self.dst_port   = tcp_header[1]
        self.seq_number = tcp_header[2]
        self.ack_number = tcp_header[3]

        header_len = (tcp_header[4] >> 4 & 15) * 4

        self.proto_header = data[:header_len]
        self.payload = data[header_len:]

    # udp header 8 bytes
    def _udp(self):
        data = self._data

        udp_header = udp_header_unpack(data)
        self.src_port = udp_header[0]
        self.dst_port = udp_header[1]
        self.udp_len  = udp_header[2]
        self.udp_chk  = udp_header[3]

        self.proto_header = data[:8]
        self.payload = data[8:]

def parse(data):
    try:
        packet = RawPacket(data)
        packet.parse()

        print(packet)
    except:
        pass

def listen_forever(intf):
    sock = _socket.socket(_socket.AF_PACKET, _socket.SOCK_RAW)
    try:
        sock.bind((intf, 3))
    except OSError:
        _sys.exit(f'cannot bind interface: {intf}! exiting...')
    else:
        _write_err(f'now listening on {intf}!')

    while True:
        try:
            data = sock.recv(2048)
        except OSError:
            pass

        else:
            parse(data)

if __name__ == '__main__':
    if _os.geteuid():
        _sys.exit('listener must be ran as root! exiting...')

    listen_forever('eth0')
