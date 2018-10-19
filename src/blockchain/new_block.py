import time
import json
from typing import List

from src.scriptinterpreter import ScriptInterpreter
from src.blockchain.new_transaction import *
from src.blockchain.account import *
from src.blockchain.crypto import *
from src.blockchain.merkle_trie import *
from src.blockchain.state_transition import transit


class Block:
    _dict = dict()

    @classmethod
    def get_from_hash(cls, hash: bytes):
        if hash in cls._dict:
            return cls._dict[hash]
        else:
            return None

    def __new__(cls, skeleton: 'BlockSkeleton', nonce: bytes):
        target = (2**256 // skeleton._difficulty).to_bytes(32, 'big')
        constructed = super().__new__(cls)
        constructed._skeleton = skeleton
        constructed._nonce = nonce
        constructed._hash = compute_hash(json.dumps(
            constructed.to_json_compatible()).encode())

        if constructed._hash > target:
            raise ValueError(
                "Tried to create block, that doesn't fulfill the difficulty")

        if constructed._hash in cls._dict:
            return cls._dict[constructed._hash]

        cls._dict[constructed._hash] = constructed
        return constructed

    @property
    def skeleton(self):
        return self._skeleton

    @property
    def nonce(self):
        return self._nonce

    @property
    def hash(self):
        return self._hash

    def to_json_compatible(self):
        var = {}
        var['skeleton'] = self.skeleton.to_json_compatible()
        var['nonce'] = bytes_to_hex(self.nonce)
        return var

    @classmethod
    def from_json_compatible(cls, var: dict, transactions: List[Transaction]):
        skeleton = BlockSkeleton.from_json_compatible(
            var['skeleton'], transactions)
        nonce = hex_to_bytes(var['nonce'])
        return cls(skeleton, nonce)


class BlockSkeleton:  # contains everything a block needs except for a valid nonce
    genesis_pubkey = b'-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCYzqSGEhl/NbUHJ1rDEp/YQfk5\nvsuCnUpaI30r+J5eeNwOyXyXbvR/J+GtKU5LJfC0llfrJUXjYF2ChQIB2EqtLch6\nTmrZcy3r/TlB6N9GDrISZ+uw5DJ209wRlET6DIgIz+gymlCUv5gc4g2HrWwmRCXi\nvn+WrMSS0ZyZuYMhTQIDAQAB\n-----END PUBLIC KEY-----'

    def __new__(cls, prev_block: 'Block', transactions: List[Transaction], miner_address: bytes, timestamp=None):
        miner_address == bytes(32) or check_is_hash(miner_address)

        if timestamp is None:
            timestamp = time.time()

        # sort transactions
        transactions = sorted(transactions, key=lambda tx: tx.hash)

        if not all(t.signed() for t in transactions):
            raise ValueError('Unsigned transaction')

        # merkle tries
        if prev_block is None:
            state_trie = MerkleTrie(MerkleTrieStorage(Account))
            genesis_contract = Account(
                cls.genesis_pubkey,
                0,
                """
                    OP_PUSHFP
                    8
                    OP_EQU
                    2
                    OP_JUMPRC
                    OP_KILL
                    -1
                    OP_PUSHR
                    OP_HASH
                    -5
                    OP_PUSHR
                    -4
                    OP_PUSHR
                    -3
                    OP_PUSHR
                    -2
                    OP_PUSHR
                    -1
                    OP_PUSHR
                    OP_CREATECONTR
                    2
                    OP_JUMPRC
                    OP_KILL
                    []
                    OP_SWAP
                    OP_GETOWNBAL
                    OP_TRANSFER
                    2
                    OP_JUMPRC
                    OP_KILL
                    1
                    OP_RET
                """,
                False,
                [])
            state_trie = state_trie.put(
                genesis_contract.address, genesis_contract)
        else:
            state_trie = prev_block.skeleton.state_trie

        tx_trie = MerkleTrie(MerkleTrieStorage(Transaction))
        for tx in transactions:
            state_trie = transit(
                ScriptInterpreter, state_trie, tx, miner_address)
            if state_trie is None:
                raise ValueError('Invalid transaction')
            tx_trie = tx_trie.put(tx.hash, tx)

        prev_accumulated_difficulty = 0 if prev_block is None else prev_block.skeleton.accumulated_difficulty

        constructed = super().__new__(cls)
        constructed._prev_block_hash = bytes(
            32) if prev_block is None else prev_block.hash
        constructed._timestamp = timestamp
        constructed._height = 1 if prev_block is None else prev_block.skeleton.height + 1
        constructed._difficulty = 1000  # TODO: protocol rule
        constructed._accumulated_difficulty = constructed._difficulty + \
            prev_accumulated_difficulty
        constructed._miner_address = miner_address
        constructed._state_trie = state_trie
        constructed._tx_trie = tx_trie
        constructed._transactions = transactions
        return constructed

    @property
    def prev_block(self):
        return Block.get_from_hash(self._prev_block_hash)

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def height(self):
        return self._height

    @property
    def difficulty(self):
        return self._difficulty

    @property
    def accumulated_difficulty(self):
        return self._accumulated_difficulty

    @property
    def miner_address(self):
        return self._miner_address

    @property
    def state_trie(self):
        return self._state_trie

    @property
    def tx_trie(self):
        return self._tx_trie

    @property
    def transactions(self):
        return self._transactions

    @property
    def hash(self):
        return compute_hash(json.dumps(self.to_json_compatible()).encode())

    def to_json_compatible(self):
        var = {}
        var['prev_block_hash'] = bytes_to_hex(self._prev_block_hash)
        var['timestamp'] = self.timestamp
        var['height'] = self.height
        var['difficulty'] = self.difficulty
        var['miner_address'] = bytes_to_hex(self.miner_address)
        var['state_root'] = bytes_to_hex(self.state_trie.hash)
        var['tx_root'] = bytes_to_hex(self.tx_trie.hash)
        return var

    @classmethod
    def from_json_compatible(cls, var: dict, transactions: List[Transaction]):
        # prev_block
        prev_block_hash = hex_to_bytes(var['prev_block_hash'])
        if prev_block_hash == bytes(32):
            prev_block = None
        else:
            prev_block = Block.get_from_hash(prev_block_hash)
            if prev_block is None:
                raise ValueError('Previous block does not exist')

        miner_address = hex_to_bytes(var['miner_address'])
        timestamp = var['timestamp']

        skeleton = BlockSkeleton(
            prev_block, transactions, miner_address, timestamp)
        if skeleton.to_json_compatible() != var:
            raise ValueError('Block verification failed')
        return skeleton
