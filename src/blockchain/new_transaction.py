import json

from collections import namedtuple
from ..crypto import get_hasher

class TransactionInput(namedtuple("TransactionInput", ["address", "value"])):

    def __init__(self, address: 'bytes', value: int):
        self.address = address
        self.value = value

    def to_json_compatible(self):
        """ Returns a JSON-serializable representation of this object. """
        val = {}
        val["address"] = self.address
        val["value"] = self.value
        return val

class TransactionOutput(namedtuple("TransactionOutput", ["address", "value", "params"])):
    """
    :ivar params: Parameters that are pushed to the stack before calling the output
    account's contract code
    :vartype params: List[str]
    """
    def __init__(self, address: bytes, value: int, params: str):
        self.address = address
        self.value = value
        self.params = params

    def to_json_compatible(self):
        """ Returns a JSON-serializable representation of this object. """
        val = {}
        val["address"] = self.address
        val["value"] = self.value
        val["params"] = self.params
        return val


class TransactionData(namedtuple("TransactionData", ["inputs", "outputs", "fee", "params"])):
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

    def __init__(self, inputs: 'List[TransactionInput]', outputs: 'List[TransactionOutput]', fee: int, nonce: bytes):
        if fee < 0:
            raise ValueError("Fee can't be negative")
        if len(nonce) != 32:
            raise ValueError('Nonce has to be 32 bytes')
        if len(inputs) <= 0 or len(output) <= 0:
            raise ValueError("Must have at least one input and one output")

        for input in inputs:
            val_sum += input.value
        for output in outputs:
            val_sum -= output.value
        if fee != val_sum:
            raise ValueError("Fee must be equal to the total difference of input and output values")

        self.inputs = inputs
        self.outputs = outputs
        self.nonce = nonce
        get_hash()

    def compute_hash(self) -> bytes:
        """ Computes the hash by just hashing the object's JSON representation """
        if self._hash is None:
            h = get_hasher()
            h.update(json.dump(self.to_json_compatible()))
            self._hash = h.digest()
        return self._hash

    def to_json_compatible(self):
        """ Returns a JSON-serializable representation of this object. """
        val = {}
        val["inputs"] = []
        for input in self.inputs:
            val.append(input.to_json_compatible())
        val["outputs"] = []
        for output in self.outputs:
            val.append(output.to_json_compatible())
        val["fee"] = self.fee
        val["nonce"] = self.nonce
        return val



class Transaction(namedtuple("Transaction", ["tx_data", "signature"])):
    """
    :ivar tx_data: See above, this is where the actual transaction data is stored
    :vartype tx_data: TransactionData
    :ivar signatures: List of signatures made by the private keys that own the
    input accounts, in the same order as the input account occur in tx_data.inputs
    :vartype signatures: List[bytes]

    """
    def __init__(self, tx_data: TransactionData):
        self.tx_data = tx_data
        # signature 0 means 'not signed yet', so init signatures with all zeroes
        self.signatures = [bytes(1)] * len(self.tx_data.inputs)

    def sign(self, index, private_key):
        """ Signs the transaction input at the given index using the given key """
        if index < 0 or index >= len(self.signatures):
            raise InputError("Invalid input index: " + index + ". Either negative or too large")
        self.signatures[index] = signing_key.sign(tx_data.get_hash())

    def get_hash(self):
        """ Computes the hash by just hasing the object's JSON representation
            It is recomputed every time """
        h = get_hasher()
        h.update(json.dump(to_json_compatible()))
        return h.digest()

    def to_json_compatible(self):
        """ Returns a JSON-serializable representation of this object. """
        val = {}
        val["tx_data"] = input.to_json_compatible()
        val["signatures"] = []
        for sig in self.signatures:
            val["signatures"].append(sig)
        return val
