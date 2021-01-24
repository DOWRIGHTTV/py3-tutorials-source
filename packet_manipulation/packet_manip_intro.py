#!/usr/bin/env python3

from ipaddress import IPv4Address
from enum import IntEnum

from socket import socket, AF_INET, SOCK_DGRAM

#NOTE: i went alittle crazy on the exceptions to validate input to make it easier to learn
# and mess around with code without wondering what is going wrong. normally i would not have
# this many validations since i trust the inputs from myself and want to save the cpu cycles.

# IntEnum because i like them like this.
class PROTO(IntEnum):
    TCP = 6
    UDP = 17


class PacketManipulation:
    '''

    class to manipulate tcp/ip packets. currently limited to UDP only!.

        packet = PacketManipulation(('127.0.0.1', 6969))

        packet.create_socket()
        packet.send_to(b'why me')

    '''

    __slots__ = ( # slots make things faster. just do them. :)
        'target', 'data', 'protocol', 'socket',

        'connect'
    )

    def __init__(self, target, *, protocol=PROTO.UDP):
        self.target = target

        self._validate_target()

        self.socket = socket() # initialization only
        self.connect = False
        self.protocol = PROTO.UDP # currently overriding argument passed in

    def create_socket(self, *, connect=False):
        self.socket = socket(AF_INET, SOCK_DGRAM)

        if connect:
            self.socket.connect(self.target)

            self.connect = True

    def send(self, data):
        '''

        calls send_to on the socket then sends the data to the specified target and prints how
        many bytes were sent. this requires the connect argument to be used at socket creation.

            packet.send(b'receive me')

        '''

        if not self.connect:
            raise RuntimeError('cannot call send method without connect argument in socket creation.')

        if not isinstance(data, bytes):
            raise TypeError('data must be a bytestring.')

        sent_count = self.socket.send(data)

        print(f'sent {sent_count} bytes!')

    def send_to(self, data, *, target=None):
        '''

        calls send_to on the socket then sends the data to the specified target and prints how many bytes
        were sent. can override instance target if needed.

            packet.send_to(b'receive me')

        '''

        if not isinstance(data, bytes):
            raise TypeError('data must be a bytestring.')

        if not target:
            target = self.target

            self._validate_target(target)

        sent_count = self.socket.sendto(data, target)

        print(f'sent {sent_count} bytes!')

    def _validate_target(self, target=None):
        if target is None:
            target = self.target

        if not isinstance(target, tuple) or len(target) != 2:
            raise TypeError('target must be a two tuple containing host ip/port.')

        try:
            IPv4Address(target[0])
        except:
            raise ValueError('invalid ip address provided for target.')

        if not isinstance(target[1], int):
            raise TypeError('target port must be an integer.')

        if not target[1] in range(0, 65536):
            raise ValueError('target port must be between 0-63535')


# NOTE: business logic. This module can be imported and used in the same manner

packet = PacketManipulation(('127.0.0.1', 6969))

# using "send_to"
packet.create_socket()
packet.send_to(b'why me')

# using "send"
#packet.create_socket(connect=True)
# packet.send(b'why me')

sock = socket(AF_INET, SOCK_DGRAM)
sock.sendto(b'LOL', ('127.0.0.1', 6999))