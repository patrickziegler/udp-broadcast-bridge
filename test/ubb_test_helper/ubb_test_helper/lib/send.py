# Copyright (C) 2021 Patrick Ziegler
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import random

import netifaces
from scapy.all import IP, UDP, Ether, fragment, sendp

from .data import kdeconnect_identity_request

KDECONNECT_DEFAULT_PORT = 1716


def create_udp_broadcast(payload : str, iface : str, dport : int):
    ifaddr = netifaces.ifaddresses(iface)
    packet = Ether(
        src=ifaddr[netifaces.AF_LINK][0]["addr"],
        dst="ff:ff:ff:ff:ff:ff"
    )
    packet /= IP(
        src=ifaddr[netifaces.AF_INET][0]["addr"],
        dst="255.255.255.255"
    )
    packet /= UDP(
        sport=random.randint(40000, 49999),
        dport=dport
    )
    packet /= payload
    return packet


def send_packet(packet, iface):
    print("Sending packet via %s\n" % iface)
    packet.show()
    sendp(fragment(packet), iface=iface)


def send_kdeconnect_identiy_request(iface="lo"):
    packet = create_udp_broadcast(
        payload=json.dumps(kdeconnect_identity_request),
        iface=iface,
        dport=KDECONNECT_DEFAULT_PORT
    )
    send_packet(packet, iface)
