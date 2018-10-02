#!/usr/bin/env python3

"""
The cmd_wallet allows a user to manage his transactions over the commandline.
For the graphical user interface execute gui_wallet.py
"""

__all__ = []

import argparse
import sys
from binascii import unhexlify
from typing import List, Union, Callable, Tuple

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s")

from src.transaction import TransactionTarget
from src.crypto import Key
from src.wallet_factory import init_Wallet


def parse_targets() -> Callable[[str], Union[Key, int]]:
    """
    Parses transaction targets from the command line: the first value is a path to a key, the
    second an amount and so on.
    """
    start = True

    def parse(val):
        nonlocal start
        if start:
            val = Key.from_file(val)
        else:
            val = int(val)
        start = not start
        return val

    return parse


def private_signing(path: str) -> Key:
    """ Parses a path to a private key from the command line. """
    val = Key.from_file(path)
    if not val.has_private:
        raise ValueError("The specified key is not a private key.")
    return val



def main():
    """
    Initializes ArgumentParser and then reads the users input.
    """
    parser = argparse.ArgumentParser(description="Wallet.")
    parser.add_argument("--miner-port", default=40203, type=int,
                        help="The RPC port of the miner to connect to.")
    #reading wallet_file_path -> will be open in the Wallet
    parser.add_argument("--wallet", default='',
                        help="The wallet file containing the private keys to use.")
    subparsers = parser.add_subparsers(dest="command")

    balance = subparsers.add_parser("create-address",
                                    help="Creates new addresses and stores their secret keys in the wallet.")
    balance.add_argument("file", nargs="+", type=argparse.FileType("wb"),
                         help="Path to a file where the address should be stored.")

    balance = subparsers.add_parser("show-balance",
                                    help="Shows the current balance of the public key "
                                         "stored in the specified file.")
    balance.add_argument("key", nargs="*", type=Key.from_file)

    trans = subparsers.add_parser("show-transactions",
                                  help="Shows all transactions involving the public key "
                                       "stored in the specified file.")
    trans.add_argument("key", nargs="*", type=Key.from_file)

    single_trans = subparsers.add_parser("show-transaction", help="Show transaction for hash")
    single_trans.add_argument("hash", help="the hash")

    subparsers.add_parser("show-network",
                          help="Prints networking information about the miner.")

    transfer = subparsers.add_parser("transfer", help="Transfer money.")
    transfer.add_argument("--private-key", type=private_signing,
                          default=[], action="append", required=False,
                          help="The private key(s) whose coins should be used for the transfer.")
    transfer.add_argument("--change-key", type=Key.from_file, required=False,
                          help="The private key where any remaining coins are sent to.")
    transfer.add_argument("--transaction-fee", type=int, default=1,
                          help="The transaction fee you want to pay to the miner.")
    transfer.add_argument("target", nargs='*', metavar=("TARGET_KEY AMOUNT"),
                          type=parse_targets(),
                          help="The private key(s) whose coins should be used for the transfer.")

    data = subparsers.add_parser("burn", help="An unspendable transaction with random data attached")
    data.add_argument("--private-key", type=private_signing, default=[], action="append", required=False,
                          help="The private key(s) whose coins should be used for the transfer.")
    data.add_argument("--change-key", type=Key.from_file, required=False,
                          help="The private key where any remaining coins are sent to.")
    data.add_argument("--transaction-fee", type=int, default=1,
                          help="The transaction fee you want to pay to the miner.")


    args = parser.parse_args()
    #TODO: Error Handling
    """try:
        w = Wallet(args.miner_port, args.wallet)
    except FileNotFoundError:
        print("no wallet specified", file=sys.stderr)
        parser.parse_args(["--help"])
        return"""
    w = init_Wallet(args.wallet, args.miner_port)


    if args.command == 'show-transactions':
        print(w.show_transactions(w.get_keys(args.key)))
    elif args.command == 'show-transaction':
        print(w.show_transaction(unhexlify(args.hash)))
    elif args.command == "create-address":
        if not args.wallet[0]:
            print("no wallet specified", file=sys.stderr)
            parser.parse_args(["--help"])
        w.create_address(args.file)
    elif args.command == 'show-balance':
        print(w.show_balance(w.get_keys(args.key)))
    elif args.command == 'show-network':
        print(w.network_info())
    elif args.command == 'transfer':
        if len(args.target) % 2:
            print("Missing amount to transfer for last target key.\n", file=sys.stderr)
            parser.parse_args(["--help"])
        if not args.change_key and not args.wallet[0]:
            print("You need to specify either --wallet or --change-key.\n", file=sys.stderr)
            parser.parse_args(["--help"])
        targets = [TransactionTarget(TransactionTarget.pay_to_pubkey(k), a) for k, a in
                   zip(args.target[::2], args.target[1::2])]
        str = w.transfer(targets, args.transaction_fee, args.change_key, w.get_keys(args.private_key))
        print(str)

    elif args.command == 'burn':
        if not args.change_key and not args.wallet[0]:
            print("You need to specify either --wallet or --change-key.\n", file=sys.stderr)
            parser.parse_args(["--help"])
        import random
        randomness = random.randint(0, 128)
        target = TransactionTarget(TransactionTarget.burn(randomness.to_bytes(40, 'big')), 0)
        str = w.transfer([target], args.transaction_fee, args.change_key, w.get_keys(args.private_key))
        print(str)

    else:
        print("You need to specify what to do.\n", file=sys.stderr)
        parser.parse_args(["--help"])


if __name__ == '__main__':
    main()