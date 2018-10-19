import json
import logging
from typing import List
from collections import namedtuple

from src.blockchain.crypto import *


def check_int_type(value: int):
    return type(value) == int


def check_str_type(value: str):
    return type(value) == str


def check_hash_type(value: bytes):
    return is_hash(value)


def check_address_type(value: bytes):
    return is_hash(value)


def check_signature_type(value: bytes):  # TODO length
    return is_signature(value)


def check_pubkey_type(value: bytes):  # TODO length
    return is_pubkey(value)


def check_keypair_type(value: bytes):  # TODO length
    return is_keypair(value)


class StorageItem(namedtuple("StorageItem", ["s_name", "s_type", "s_value"])):
    _supported_types = {'int': check_int_type, 'str': check_str_type, 'hash': check_hash_type,
                        'signature': check_signature_type, 'pubkey': check_pubkey_type,
                        'keypair': check_keypair_type}

    def __new__(cls, s_name: str, s_type: str, s_value: object):
        s_type = s_type.lower()
        if s_type not in cls._supported_types or not cls._supported_types[s_type](s_value):
            logging.warning("invalid storage item for " + s_name)
            return None
        return super().__new__(cls, s_name, s_type, s_value)

    def to_json_compatible(self):
        """ Returns a JSON-serializable representation of this object. """
        val = {}
        val["s_name"] = self.s_name
        val["s_type"] = self.s_type
        if (self.s_type in ['pubkey', 'keypair', 'signature', 'hash']):
            val["s_value"] = bytes_to_hex(self.s_value)
        else:
            val["s_value"] = self.s_value
        return val

    @classmethod
    def from_json_compatible(cls, val):
        """ Create a new StorageItem from its JSON-serializable representation. """
        if (val['s_type'] in ['key', 'signature', 'address', 'hash']):
            s_value = hex_to_bytes(val['s_value'])
        else:
            s_value = val['s_value']
        return cls(val["s_name"], val['s_type'], val["s_value"])

    def set_value(self, var_name: str, var_value: object):
        if self.s_name != var_name or not self._supported_types[self.s_type](var_value):
            logging.warning("can't set storage for variable " + var_name)
            return None
        return StorageItem(var_name, self.s_type, var_value)


class Account(namedtuple("Account", ["pub_key", "balance", "code", "owner_access", "storage"])):
    _dict = dict()

    def __new__(cls, pubkey: bytes, balance: int, code: str, owner_access: bool, storage: List[StorageItem]):
        if None in storage:
            raise ValueError("storage can't contain None " + str(storage))
        check_is_pubkey(pubkey)
        constructed = super().__new__(cls, pubkey, balance, code, owner_access, storage)
        if constructed.hash in cls._dict:
            return cls._dict[constructed.hash]
        else:
            cls._dict[constructed.hash] = constructed
            return constructed

    def to_json_compatible(self):
        """ Returns a JSON-serializable representation of this object. """
        val = {}
        val["pub_key"] = bytes_to_hex(self.pub_key)
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
        return cls(hex_to_bytes(val["pub_key"]),
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
            logging.warning("Invalid balance modification: New balance (" +
                            str(new_balance) + ") would be negative")
            return None
        return Account(self.pub_key, self.balance + delta, self.code, self.owner_access, self.storage)

    def set_storage(self, var_name: str, var_value: object):
        # you can set new values for existing variables with the correct type
        find_item = list(
            filter(lambda storage_item: storage_item.s_name == var_name and StorageItem._supported_types[
                storage_item.s_type](var_value), self.storage))
        if not find_item or len(find_item) != 1:
            logging.warning("can't set storage for variable " + var_name)
            return None
        new_item = find_item[0].set_value(var_name, var_value)
        if new_item == None:
            logging.warning("can't set storage for variable " + var_name)
            return None
        new_storage = self.storage + [new_item]
        new_storage.remove(find_item[0])
        return Account(self.pub_key, self.balance, self.code, self.owner_access, new_storage)

    def get_storage(self, var_name: str):
        find_item = list(
            filter(lambda storage_item: storage_item.s_name == var_name, self.storage))
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
