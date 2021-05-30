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

import ipaddress
import os

import netifaces


def check_network_addr_used(net : ipaddress.IPv4Network) -> bool:
    for iface in netifaces.interfaces():
        for ifaddr in netifaces.ifaddresses(iface)[netifaces.AF_INET]:
            if ipaddress.ip_address(ifaddr["addr"]) in net:
                return True
    return False


def check_netns_exists(name : str) -> bool:
    return os.path.exists(os.path.join("/var/run/netns/", name))


def check_device_exists(name : str) -> bool:
    return name in netifaces.interfaces()


def exec_cmd(cmd : str, netns=None, verbose=True):
    if netns is not None:
        cmd = "ip netns exec %s %s" % (netns, cmd)
    if verbose:
        print(">>> " + cmd)
    os.system(cmd)


def netns_delete(name : str):
    print("Deleting network namespace %s" % name)
    exec_cmd("ip netns delete %s" % name)


class Netdev:

    def __init__(self, name : str, addr : str):
        self.name = name
        self.addr = addr
        self.__validate()

    def __validate(self):
        if check_device_exists(self.name):
            raise ValueError("Device '%s' already exists" % self.name)

    def __str__(self):
        return self.name


class Netns:

    def __init__(self, name="ns0", net="11.0.0.0/24"):
        self.net = ipaddress.ip_network(net, strict=False)
        self.name = name
        self.__validate()
        hosts = self.net.hosts()
        self.eth0 = Netdev(name=self.name + "-veth0", addr=next(hosts))
        self.eth1 = Netdev(name=self.name + "-veth1", addr=next(hosts))

    def __validate(self):
        if check_network_addr_used(self.net):
            raise ValueError("Network '%s' already in use" % self.net)
        if check_netns_exists(self.name):
            raise ValueError("Namespace '%s' already exists" % self.name)

    def __enter__(self):
        self.start()
        return lambda cmd: exec_cmd(cmd, netns=self.name)

    def __exit__(self, type, value, traceback):
        self.stop()

    def start(self):
        print("Creating network namespace %s" % self.name)
        exec_cmd("ip netns add %s" % self.name)
        exec_cmd("ip link add %s type veth peer %s" % (self.eth0, self.eth1))
        exec_cmd("ip link set %s netns %s" % (self.eth1, self.name))
        exec_cmd("ip addr add %s/%d dev %s" % (self.eth0.addr, self.net.prefixlen,
            self.eth0))
        exec_cmd("ip addr add %s/%d dev %s" % (self.eth1.addr, self.net.prefixlen,
            self.eth1), netns=self.name)
        exec_cmd("ip link set %s up" % self.eth0)
        exec_cmd("ip link set %s up" % self.eth1, netns=self.name)

    def stop(self):
        netns_delete(self.name)
