#!/usr/bin/env python3

"""
Super class for the wallet types:
One type is the standard wallet, the other is a hierarchical wallet

The wallet allows a user to query account balance, send money, and get status information about a
miner.
"""

__all__ = ['Wallet']
import json
import os.path

class WalletHierarchical(object):
    pass
class WalletOld(object):
    pass



from datetime import datetime
from binascii import hexlify
from io import IOBase
from typing import List, Tuple, Optional

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s")

from .transaction import TransactionTarget
from .crypto import Key
from .rpc_client import RPCClient


class Wallet:
    """
    :ivar _wallet_path: Path to the wallet file. Set in the constructor
    :vartype: string
    """

    @classmethod
    def init_Wallet(cls, wallet_path: str, ip_address="localhost", miner_port=40203):
        """
        A factory for the two wallet types.
        :param wallet_path: path to the wallet file. Ending: .wallet -> old Wallet
                                                             .hwallet -> hierarchical Wallet
        :param ip_address: address for the rpc_client
        :param miner_port: port for the rpc_client
        :return: The Wallet on this path. If there is no File, a new hierarchical Wallet is instantiated
        """
        if wallet_path.endswith(".wallet"):
            return WalletOld(wallet_path, ip_address, miner_port)
        if wallet_path.endswith(".hwallet"):
            return WalletHierarchical(wallet_path, ip_address, miner_port)

    def __init__(self, wallet_path: str, ip_address="localhost", miner_port=40203):
        """
        sets up RPCClient, 
        """
        if os.path.isfile(wallet_path):
            self._wallet_path = wallet_path
        else:
            raise FileNotFoundError  # TODO create new File ? but how to handle incorrect file ending

        self.rpc = RPCClient(ip_address, miner_port)

    def get_wallet_path(self):
        return self._wallet_path

    def read_wallet(self, path: str) -> Tuple[List[Key], str]:
        raise Exception("abstract method")

    def read_wallet_private(self, path: str) -> Tuple[List[Key], str]:
        """
        Parses the wallet from the command line.

        Returns a tuple with a list of keys from the wallet and the path to the wallet (for write
        operations).
        """
        try:
            with open(path, "rb") as f:
                contents = f.read()
        except FileNotFoundError:
            return ([], path)
        return (list(Key.read_many_private(contents)), path)

    def generate_next_key(self) -> Key:
        """generates a new private key for the wallet. In the hierarchical wallet this key is determined"""
        raise Exception("abstract method")

    def wallet_keys(self) -> List[Key]:
        return self.read_wallet(self._wallet_path)[0]

    def get_addresses(self):
        return json.dumps(self.rpc.get_addresses())

    def show_transaction(self, tx_hash: bytes):
        return self.rpc.get_transaction(tx_hash).to_json_compatible()

    def show_transactions(self, keys=None):
        """returns transactions of the keys as json
        :param keys:
        """
        if not keys:
            keys = self.wallet_keys()
        transactions = set()
        for key in keys:
            for trans in self.rpc.get_transactions(key):
                transactions.add(trans)
        return json.dumps(transactions)

    def create_address(self, outputs: List[IOBase]):
        """
        Generates for each file a private key and stores the key in this file.
        All generated keys are added to the wallet file as well.
        :param outputs: files to store the keys
        :return: --
        """

        keys = [self.generate_next_key() for _ in outputs]
        Key.write_many_private(self._wallet_path, self.wallet_keys() + keys)
        for fp, key in zip(outputs, keys):
            fp.write(key.as_bytes())
            fp.close()

    def show_balance(self, keys=None):
        if not keys:
            keys = self.wallet_keys()
        total = 0
        for pubkey, balance in self.rpc.show_balance(keys):
            print("{}: {}".format(hexlify(pubkey.as_bytes()), balance))
            total += balance
        print()
        print("total: {}".format(total))

    def network_info(self):
        for k, v in self.rpc.network_info():
            print("{}\t{}".format(k, v))

    def transfer(self, tx_targets: List[TransactionTarget], transaction_fee: int, change_key: Optional[Key],
                 priv_keys: List[Key]):
        if not change_key:
            change_key = self.generate_next_key()
            Key.write_many_private(self._wallet_path, self.wallet_keys() + [change_key])

        timestamp = datetime.utcnow()
        tx = self.rpc.build_transaction(priv_keys, tx_targets, change_key, transaction_fee, timestamp)
        print(hexlify(tx.get_hash()).decode())
        self.rpc.send_transaction(tx)

    def get_keys(self, keys: List[Key] = None) -> List[Key]:
        """
        Returns a combined list of keys from the `keys` and the wallet. Shows an error if empty.
        """
        if keys:
            all_keys = keys + self.wallet_keys()
        else:
            all_keys = self.wallet_keys()
        if not all_keys:
            raise Exception("empty Key List")
        return all_keys

    def close(self):
        """maybe close open files and release the used memory"""
