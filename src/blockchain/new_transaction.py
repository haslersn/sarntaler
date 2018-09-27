import json

from collections import namedtuple
from ..crypto import get_hasher
from typing import Tuple # needed for the type hint "Tuple[bytes]"
from binascii import hexlify, unhexlify

class TransactionInput(namedtuple("TransactionInput", ["address", "value"])):

    def __new__(self, address: bytes, value: int):
        return super().__new__(self, address, value)

    def to_json_compatible(self):
        """ Returns a JSON-serializable representation of this object. """
        val = {}
        val["address"] = hexlify(self.address).decode()
        val["value"] = self.value
        return val

    @classmethod
    def from_json_compatible(cls, val):
        """ Create a new TransactionInput from its JSON-serializable representation. """
        return cls(unhexlify(val["address"]), val["value"])

class TransactionOutput(namedtuple("TransactionOutput", ["address", "value", "params"])):
    """
    :ivar params: Parameters that are pushed to the stack before calling the output
    account's contract code
    :vartype params: List[str]
    """
    def __new__(self, address: bytes, value: int, params: str = None):
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
    def compute_hash(self) -> bytes:
        """ Computes the hash by just hashing the object's JSON representation """
        h = get_hasher()
        h.update(json.dumps(self.to_json_compatible()))
        return h.digest()

    def __new__(cls, inputs: 'List[TransactionInput]', outputs: 'List[TransactionOutput]', fee: int, nonce: bytes):
        if fee < 0:
            raise ValueError("Fee can't be negative")
        if len(nonce) != 32:
            raise ValueError('Nonce has to be 32 bytes')
        if len(inputs) <= 0 or len(outputs) <= 0:
            raise ValueError("Must have at least one input and one output")

        val_sum = 0
        for input in inputs:
            val_sum += input.value
        for output in outputs:
            val_sum -= output.value
        if fee != val_sum:
            raise ValueError("Fee must be equal to the total difference of input and output values")

        return super().__new__(cls, inputs, outputs, fee, nonce)

    def compute_hash(self) -> bytes:
        """ Computes the hash by just hashing the object's JSON representation """
        h = get_hasher()
        h.update(json.dumps(self.to_json_compatible()))
        return h.digest()

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
        if not self.hasattr('_hash'):
            self._hash = compute_hash()
        return self._hash



class Transaction(namedtuple("Transaction", ["tx_data", "signatures"])):
    """
    :ivar tx_data: See above, this is where the actual transaction data is stored
    :vartype tx_data: TransactionData
    :ivar signatures: List of signatures made by the private keys that own the
    input accounts, in the same order as the input account occur in tx_data.inputs
    :vartype signatures: List[bytes]

    """

    def __new__(self, tx_data: TransactionData, signatures: Tuple[bytes]=None):
        if signatures is None:
            signatures = (bytes(32),) * len(tx_data.inputs)
        return super().__new__(self, tx_data, signatures)

    def sign(self, index, private_key):
        """ Signs the transaction input at the given index using the given key """
        if index < 0 or index >= len(self.signatures):
            raise InputError("Invalid input index: " + index + ". Either negative or too large")
        new_sig = signing_key.sign(tx_data.get_hash())
        return Transaction(self, tx_data, signatures[0:index:] + (new_sig,) + signatures[index +1:len(signatures):])

    def get_hash(self):
        """ Computes the hash by just hasing the object's JSON representation
            It is recomputed every time """
        h = get_hasher()
        h.update(str.encode(json.dumps(self.to_json_compatible())))
        return h.digest()

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
        #24return cls(TransactionData.from_json_compatible(val["tx_data"]), signatures)
