#!/usr/bin/env python3

"""
The executable that participates in the P2P network and optionally mines new blocks. Can be reached
through a REST API by the wallet.
"""

__all__ = []

import argparse
from urllib.parse import urlparse
from typing import Tuple

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s")

from src.config import *
from src.crypto import Key
from src.protocol import Protocol
from src.blockchain import GENESIS_BLOCK
from src.chainbuilder import ChainBuilder
from src.mining import Miner
from src.persistence import Persistence
from src.rpc_server import rpc_server


def parse_addr_port(val: str) -> Tuple[str, int]:
    """ Parse a user-specified `host:port` value to a tuple. """
    url = urlparse("//" + val)
    assert url.scheme == ''
    assert url.path == ''
    assert url.params == ''
    assert url.query == ''
    assert url.fragment == ''
    assert url.port is not None
    assert url.hostname is not None
    return (url.hostname, url.port)


def main():
    """
    Takes arguments:
    `listen-address`: The IP address where the P2P server should bind to. Default is: `\"\"`
    `listen-port`: The port where the P2P server should listen. Defaults a dynamically assigned port. Default is: `0`
    `mining-pubkey`: The public key where mining rewards should be sent to. No mining is performed if this is left unspecified.
    `bootstrap-peer`: Addresses of other P2P peers in the network. Default is: `[]`
    `rpc-port`: The port number where the wallet can find an RPC server. Default is: `40203`
    `persist-path`: The file where data is persisted.
    """
    parser = argparse.ArgumentParser(description="Blockchain Miner.")
    parser.add_argument("--listen-address", default="",
                        help="The IP address where the P2P server should bind to.")
    parser.add_argument("--listen-port", default=0, type=int,
                        help="The port where the P2P server should listen. Defaults a dynamically assigned port.")
    parser.add_argument("--mining-pubkey", type=argparse.FileType('rb'),
                        help="The public key where mining rewards should be sent to. No mining is performed if this is left unspecified.")
    parser.add_argument("--bootstrap-peer", action='append', type=parse_addr_port, default=[],
                        help="Addresses of other P2P peers in the network.")
    parser.add_argument("--rpc-port", type=int, default=40203,
                        help="The port number where the wallet can find an RPC server.")
    parser.add_argument("--persist-path",
                        help="The file where data is persisted.")

    args = parser.parse_args()

    proto = Protocol(args.bootstrap_peer, GENESIS_BLOCK, args.listen_port, args.listen_address)
    if args.mining_pubkey is not None:
        pubkey = Key(args.mining_pubkey.read())
        args.mining_pubkey.close()
        miner = Miner(proto, pubkey)
        miner.start_mining()
        chainbuilder = miner.chainbuilder
    else:
        chainbuilder = ChainBuilder(proto)

    if args.persist_path:
        persist = Persistence(args.persist_path, chainbuilder)
        try:
            persist.load()
        except FileNotFoundError:
            pass
    else:
        persist = None

    rpc_server(args.rpc_port, chainbuilder, persist)


def start_listener(rpc_port: int, bootstrap_peer: str, listen_port: int, listen_address: str):
    """ Starts the RPC Server and initializes the protocol. """
    proto = Protocol([parse_addr_port(bootstrap_peer)], GENESIS_BLOCK, listen_port, listen_address)
    chainbuilder = ChainBuilder(proto)
    rpc_server(rpc_port, chainbuilder, None)


if __name__ == '__main__':
    main()
