#!/usr/bin/env python3

from src.crypto import Key
from .wallet import Wallet

"""
This is the standard Wallet
All generated Keys are random. They are lost if the key is lost and can't be created again.
"""

__all__ = ['WalletOld']

from typing import List, Tuple

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s")


class WalletOld(Wallet):

    def __init__(self, wallet_path: str, ip_address="localhost", miner_port=40203):
        super().__init__(wallet_path, ip_address, miner_port)

    def read_wallet(self, path: str) -> Tuple[List[Key], str]:
        return super().read_wallet_private(path)

    def generate_next_key(self) -> Key:
        return Key.generate_private_key()
