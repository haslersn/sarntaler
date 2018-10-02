import json

from collections import namedtuple
from typing import Tuple # needed for the type hint "Tuple[bytes]"
from binascii import hexlify, unhexlify
from src.blockchain.crypto import *

class TransactionInput(namedtuple("TransactionInput", ["address", "value"])):

    def __new__(cls, address: bytes, value: int):
        (address == bytes(32) and value == 0) or check_is_hash(address)
        if value < 0:
            raise ValueError('transaction value mustn\'t be negative')
        return super().__new__(cls, address, value)

    def to_json_compatible(self):
        """ Returns a JSON-serializable representation of this object. """
        var = {}
        var["address"] = hexlify(self.address).decode()
        var["value"] = self.value
        return var

    @classmethod
    def from_json_compatible(cls, var):
        """ Create a new TransactionInput from its JSON-serializable representation. """
        return cls(unhexlify(var["address"]), var["value"])

class TransactionOutput(namedtuple("TransactionOutput", ["address", "value", "params"])):
    """
    :ivar params: Parameters that are pushed to the stack before calling the output
    account's contract code
    :vartype params: List[str]
    """

    def __new__(self, address: bytes, value: int, params: str = None):
        address == bytes(32) or check_is_hash(address)
        if value < 0:
            raise ValueError('transaction value mustn\'t be negative')
        return super().__new__(self, address, value, params)

    def to_json_compatible(self):
        """ Returns a JSON-serializable representation of this object. """
        val = {}
        val["address"] = hexlify(self.address).decode()
        val["value"] = self.value
        val["params"] = self.params
        return val

    @classmethod
    def from_json_compatible(cls, val):
        """ Create a new transaction ouptut from its JSON-serializable representation. """
        return cls( unhexlify(val["address"]),
                    val["value"],
                    val["params"])


class TransactionData(namedtuple("TransactionData", ["inputs", "outputs", "fee", "nonce"])):
    """
    This class contains all data that belongs to a transaction, except for the
    signature. This is to separate the data that needs to be signed from the
    signature, so that we have an object we can sign in its entirety.

    :ivar inputs: A list of inputs (i.e. input account and value) of this transaction
    :vartype inputs: List[TransactionInput]
    :ivar outputs: A list of outputs (i.e. output account and value) where the money goes
    :vartype outputs: List[TransactionOutput]
    :ivar fee: The fee paid to the miner that verifies this transaction. This is implicit
    by the difference between the sum of input and output values, but is stored
    separately to prevent handling errors.
    :vartype fee: int
    :ivar nonce: A nonce (32 bytes, e.g. sequential number or timestamp) to prevent two transactions from
    being identical when sending the same value to / from the same input / output
    :vartype nonce: int
    :ivar _hash: The data's hash, this is computed at construction and saved
    :vartype hash: bytes
    """

    def __new__(cls, inputs: 'List[TransactionInput]', outputs: 'List[TransactionOutput]', fee: int, nonce: bytes):
        if fee < 0:
            raise ValueError("Fee can't be negative")
        if len(nonce) != 32:
            raise ValueError('Nonce has to be 32 bytes')
        if len(outputs) <= 0:
            raise ValueError("Must have at least one output")

        val_sum = 0
        for input in inputs:
            val_sum += input.value
        for output in outputs:
            val_sum -= output.value
        if fee != val_sum:
            raise ValueError("Fee must be equal to the total difference of input and output values")

        return super().__new__(cls, inputs, outputs, fee, nonce)

    def to_json_compatible(self):
        """ Returns a JSON-serializable representation of this object. """
        val = {}
        val["inputs"] = []
        for input in self.inputs:
            val["inputs"].append(input.to_json_compatible())
        val["outputs"] = []
        for output in self.outputs:
            val["outputs"].append(output.to_json_compatible())
        val["fee"] = self.fee
        val["nonce"] = hexlify(self.nonce).decode()
        return val

    @classmethod
    def from_json_compatible(cls, val):
        """ Create a new transaction data from its JSON-serializable representation. """
        inputs = []
        for inp in val["inputs"]:
            inputs.append(TransactionInput.from_json_compatible(inp))
        outputs = []
        for out in val["outputs"]:
            outputs.append(TransactionOutput.from_json_compatible(out))
        fee = val["fee"]
        nonce = unhexlify(val["nonce"])
        return cls(inputs, outputs, fee, nonce)

    @property
    def hash(self):
        """ Computes the hash by just hashing the object's JSON representation """
        return compute_hash(json.dumps(self.to_json_compatible()).encode())


class Transaction(namedtuple("Transaction", ["tx_data", "signatures"])):
    """
    :ivar tx_data: See above, this is where the actual transaction data is stored
    :vartype tx_data: TransactionData
    :ivar signatures: List of signatures made by the private keys that own the
    input accounts, in the same order as the input account occur in tx_data.inputs
    :vartype signatures: Tuple[bytes]

    """

    def __new__(cls, tx_data: TransactionData, signatures: Tuple[bytes]=None):
        if signatures is None:
            signatures = (bytes(32),) * len(tx_data.inputs)
        elif len(signatures) != len(tx_data.inputs):
            raise ValueError('Number of inputs and signatures does not match')
        return super().__new__(cls, tx_data, signatures)

    def sign(self, index, keypair: bytes):
        """ Signs the transaction input at the given index using the given key """
        if index < 0 or index >= len(self.signatures):
            raise ValueError("Invalid input index: " + index + ". Either negative or too large")
        check_is_keypair(keypair)
        signer_pubkey = pubkey_from_keypair(keypair)
        signer_address = self.tx_data.inputs[index].address
        if signer_address != compute_hash(signer_pubkey):
            raise ValueError('Keypair not entitled to sign this transaction/index')
        new_sig = sign(keypair, tx_data.hash)
        return Transaction(self, tx_data, signatures[0:index:] + (new_sig,) + signatures[index+1:])

    @property
    def hash(self):
        """ Computes the hash by just hasing the object's JSON representation
            It is recomputed every time """
        return compute_hash(json.dumps(self.to_json_compatible()).encode())

    def to_json_compatible(self):
        """ Returns a JSON-serializable representation of this object. """
        val = {}
        val["tx_data"] = self.tx_data.to_json_compatible()
        val["signatures"] = []
        for sig in self.signatures:
            val["signatures"].append(hexlify(sig).decode())
        return val

    @classmethod
    def from_json_compatible(cls, val):
        """ Create a new Transaction from its JSON-serializable representation. """
        signatures = []
        for hex_sig in val["signatures"]:
            signatures.append(unhexlify(hex_sig))
        return cls(TransactionData.from_json_compatible(val["tx_data"]), signatures)
