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

__version__ = "0.1.0"

import argparse

from .lib.send import send_kdeconnect_identity_request
from .lib.net import Netns, netns_delete

DEFAULT_NETNS_NAME = "ns0"
DEFAULT_NETNS_NET = "11.0.0.0/24"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", "-V",
        action="version",
        version="%(prog)s " + __version__ + " (C) 2021 Patrick Ziegler"
    )
    sub0 = parser.add_subparsers(dest="cmd")

    sub1 = sub0.add_parser("send")
    sub1.add_argument("iface", nargs="?", default="lo")

    sub2 = sub0.add_parser("start")
    sub2.add_argument("--name", default=DEFAULT_NETNS_NAME)
    sub2.add_argument("--net", default=DEFAULT_NETNS_NET)

    sub3 = sub0.add_parser("stop")
    sub3.add_argument("--name", default=DEFAULT_NETNS_NAME)

    return parser.parse_args()


def main():
    args = parse_args()

    if args.cmd == "send":
        send_kdeconnect_identity_request(iface=args.iface)

    elif args.cmd == "start":
        ns = Netns(name=args.name, net=args.net)
        ns.start()

    elif args.cmd == "stop":
        netns_delete(args.name)

    print("Done")
