import json
from binascii import hexlify, unhexlify
from typing import TypeVar, Generic

from src.blockchain.crypto import compute_hash
from collections import namedtuple


T = TypeVar('T')  # maybe understand why this is needed
class Storage(Generic[T]):
    pass

class Account(namedtuple("Account", ["pub_key", "balance", "code", "owner_access", "storage"])):
    _dict = dict()

    @classmethod
    def get_from_hash(cls, hash: bytes):
        if hash in cls._dict:
            return cls._dict[hash]
        else:
            return None

    def __new__(cls, pub_key: bytes, balance: int, code: str, owner_access: bool, storage: list):
        constructed = super().__new__(cls, pub_key, balance, code, owner_access, storage)
        if constructed.hash in cls._dict:
            return cls._dict[constructed.hash]
        else:
            cls._dict[constructed.hash] = constructed
            return constructed

    def to_json_compatible(self):
        """ Returns a JSON-serializable representation of this object. """
        val = {}
        val["pub_key"] = hexlify(self.pub_key).decode()
        val["balance"] = self.balance
        val["code"] = self.code
        val["owner_access"] = self.owner_access
        val["storage"] = self.storage
        return val

    @classmethod
    def from_json_compatible(cls, val):
        """ Create a new account from its JSON-serializable representation. """
        return cls(unhexlify(val["pub_key"]),
                   val["balance"],
                   val["code"],
                   val["owner_access"],
                   val["storage"])

    @property
    def hash(self):
        """ Computes the hash by just hashing the object's JSON representation
            It is recomputed every time """
        return compute_hash(json.dumps(self.to_json_compatible()).encode())

    @property
    def address(self):
        return compute_hash(self.pub_key)

    def add_to_balance(self, delta: int):
        newbalance = self.balance + delta
        if newbalance < 0:
            raise ValueError("Invalid balance modification: New balance (" + str(newbalance) + ") would be negative")
        return Account(self.pub_key, self.balance + delta, self.code, self.owner_access, self.storage)
