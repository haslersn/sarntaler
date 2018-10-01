import json
from binascii import hexlify, unhexlify
from pydoc import locate
from typing import List
import logging

from src.blockchain.crypto import compute_hash
from collections import namedtuple

# TODO add mapping for types to support Hashes, Signatures, ...
class StorageItem(namedtuple("StorageItem", ["s_name", "s_type", "s_value"])):
    def __new__(cls, s_name: str, s_type: type, s_value: object):
        if type(s_value) != s_type:
            logging.warning("invalid initialization for " + s_name)
            return None
        return super().__new__(cls, s_name, s_type, s_value)

    def to_json_compatible(self):
        """ Returns a JSON-serializable representation of this object. """
        val = {}
        val["s_name"] = self.s_name
        val["s_type"] = self.s_type.__name__
        val["s_value"] = self.s_value
        return val

    @classmethod
    def from_json_compatible(cls, val):
        """ Create a new StorageItem from its JSON-serializable representation. """
        s_type = locate(val['s_type'])  # gets type from serialized string
        return cls(val["s_name"], s_type, val["s_value"])

    def set_value(self, var_name: str, var_value: object):
        if self.s_name != var_name or self.s_type != type(var_value):
            logging.warning("can't set storage for variable " + var_name)
            return None
        return StorageItem(var_name, self.s_type, var_value)


class Account(namedtuple("Account", ["pub_key", "balance", "code", "owner_access", "storage"])):
    _dict = dict()

    @classmethod
    def get_from_hash(cls, hash: bytes):
        if hash in cls._dict:
            return cls._dict[hash]
        else:
            return None

    def __new__(cls, pub_key: bytes, balance: int, code: str, owner_access: bool, storage: List[StorageItem]):
        if None in storage:
            logging.warning("storage can't contain None " + str(storage))
            return None
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
        val["storage"] = []
        for storage_item in self.storage:
            val["storage"].append(storage_item.to_json_compatible())
        return val

    @classmethod
    def from_json_compatible(cls, val):
        """ Create a new account from its JSON-serializable representation. """
        storage_items = []
        for item in val["storage"]:
            storage_items.append(StorageItem.from_json_compatible(item))
        return cls(unhexlify(val["pub_key"]),
                   val["balance"],
                   val["code"],
                   val["owner_access"],
                   storage_items)

    @property
    def hash(self):
        """ Computes the hash by just hashing the object's JSON representation
            It is recomputed every time """
        return compute_hash(json.dumps(self.to_json_compatible()).encode())

    @property
    def address(self):
        return compute_hash(self.pub_key)

    def add_to_balance(self, delta: int):
        new_balance = self.balance + delta
        if new_balance < 0:
            logging.warning("Invalid balance modification: New balance (" + str(new_balance) + ") would be negative")
            return None
        return Account(self.pub_key, self.balance + delta, self.code, self.owner_access, self.storage)

    def set_storage(self, var_name: str, var_value: object):
        # you can set new values for existing variables with the correct type
        find_item = list(
            filter(lambda storage_item: storage_item.s_name == var_name and storage_item.s_type == type(var_value),
                   self.storage))
        if not find_item or len(find_item) != 1:
            logging.warning("can't set storage for variable " + var_name)
            return None
        new_item = find_item[0].set_value(var_name, var_value)
        new_storage = self.storage + [new_item]
        new_storage.remove(find_item[0])
        return Account(self.pub_key, self.balance, self.code, self.owner_access, new_storage)

    def get_storage(self, var_name: str):
        find_item = list(filter(lambda storage_item: storage_item.s_name == var_name, self.storage))
        if not find_item or len(find_item) != 1:
            logging.warning("can't get storage for variable " + var_name)
            return None
        return find_item[0].s_value

#    def add_to_storage(self, storage_item: StorageItem):
#        new_storage = self.storage + [storage_item]
#        return Account(self.pub_key, self.balance, self.code, self.owner_access, new_storage)

#    def remove_from_storage(self, var_name):
#        new_storage = list(filter(lambda storage_item: storage_item.s_name != var_name, self.storage))
#        return Account(self.pub_key, self.balance, self.code, self.owner_access, new_storage)
