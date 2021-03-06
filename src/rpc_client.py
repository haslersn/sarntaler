""" The RPC functionality used by the wallet to talk to the miner application. """

import json
import sys
from typing import List, Tuple, Iterator
from datetime import datetime

import requests

from .transaction import Transaction, TransactionTarget, TransactionInput
from .crypto import Key


class RPCClient:
    """ The RPC methods used by the wallet to talk to the miner application. """

    def __init__(self, miner_port: int):
        self.sess = requests.Session()
        self.url = "http://localhost:{}/".format(miner_port)

    def send_transaction(self, transaction: Transaction):
        """ Sends a transaction to the miner. """
        resp = self.sess.put(self.url + 'new-transaction', data=json.dumps(transaction.to_json_compatible()),
                             headers={"Content-Type": "application/json"})
        resp.raise_for_status()

    def network_info(self) -> List[Tuple[str, int]]:
        """ Returns the peers connected to the miner. """
        resp = self.sess.get(self.url + 'network-info')
        resp.raise_for_status()
        return [tuple(peer) for peer in resp.json()]

    def get_transactions(self, pubkey: Key) -> List[Transaction]:
        """ Returns all transactions involving a certain public key. """
        resp = self.sess.post(self.url + 'transactions', data=pubkey.as_bytes(),
                              headers={"Content-Type": "application/json"})
        resp.raise_for_status()
        return [Transaction.from_json_compatible(t) for t in resp.json()]

    def get_transaction(self, tx_hash: bytes) -> Transaction:
        """ Returns the transaction with hash tx_hash """
        resp = self.sess.post(self.url + 'transaction', data=tx_hash,          headers={"Content-Type": "application/json"})
        resp.raise_for_status()
        return Transaction.from_json_compatible(resp.json())

    def show_balance(self, pubkeys: List[Key]) -> Iterator[Tuple[Key, int]]:
        """ Returns the balance of a number of public keys. """
        resp = self.sess.post(self.url + "show-balance", data=json.dumps([pk.to_json_compatible() for pk in pubkeys]),
                              headers={"Content-Type": "application/json"})
        resp.raise_for_status()
        return zip(pubkeys, resp.json())

    def build_transaction(self, source_keys: List[Key], targets: List[TransactionTarget],
                          change_key: Key, transaction_fee: int, timestamp: datetime) -> Transaction:
        """
        Builds a transaction sending money from `source_keys` to `targets`, sending any change to the
        key `change_key` and a transaction fee `transaction_fee` to the miner.
        """
        resp = self.sess.post(self.url + "build-transaction", data=json.dumps({
            "sender-pubkeys": [k.to_json_compatible() for k in source_keys],
            "amount": sum(t.amount for t in targets) + transaction_fee,
        }), headers={"Content-Type": "application/json"})
        resp.raise_for_status()
        resp = resp.json()
        remaining = resp['remaining_amount']
        if remaining < 0:
            print("You do not have sufficient funds for this transaction. ({} missing)".format(-remaining),
                  file=sys.stderr)
            sys.exit(2)
        elif remaining > 0:
            targets = targets + [TransactionTarget(TransactionTarget.pay_to_pubkey(change_key), remaining)]

        temp_inputs = [TransactionInput.from_json_compatible(i) for i in resp['inputs']]
        temp_trans = Transaction(temp_inputs, targets, timestamp)

        keyidx = resp['key_indices']

        inputs = [(TransactionInput(inp.transaction_hash, inp.output_idx, temp_trans.sign(source_keys[keyidx[i]])))
                  for i, inp in enumerate(temp_inputs)]

        return Transaction(inputs, targets, timestamp)

