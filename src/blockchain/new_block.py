from binascii import hexlify, unhexlify
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
        to_hash = skeleton.hash + nonce
        hash = compute_hash(to_hash)
        if hash > target:
            raise ValueError("Tried to create block, that doesn't fulfill the difficulty")

        if hash in cls._dict:
            return cls._dict[hash]

        constructed = super().__new__(cls)
        constructed._skeleton = skeleton
        constructed._nonce = nonce
        constructed._hash = hash
        cls._dict[hash] = constructed
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
        var['skeleton'] = skeleton.to_json_compatible()
        var['nonce'] = hexlify(nonce).decode()
        return var

    @classmethod
    def from_json_compatible(cls, var: dict, transactions: List[Transaction]):
        skeleton = Skeleton.from_json_compatible(var['skeleton'], transactions)
        nonce = unhexlify(var['nonce'])
        return cls(skeleton, nonce)


class BlockSkeleton: # contains everything a block needs except for a valid nonce
    genesis_pubkey = b'-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCYzqSGEhl/NbUHJ1rDEp/YQfk5\nvsuCnUpaI30r+J5eeNwOyXyXbvR/J+GtKU5LJfC0llfrJUXjYF2ChQIB2EqtLch6\nTmrZcy3r/TlB6N9GDrISZ+uw5DJ209wRlET6DIgIz+gymlCUv5gc4g2HrWwmRCXi\nvn+WrMSS0ZyZuYMhTQIDAQAB\n-----END PUBLIC KEY-----'

    def __new__(cls, prev_block: 'Block', transactions: List[Transaction], miner_address: Account, timestamp = None):
        miner_address == bytes(32) or check_is_hash(miner_address)

        if timestamp is None:
            timestamp = time.time()

        # sort transactions
        transactions = sorted(transactions, key = lambda tx: tx.hash)

        if not all(t.signed() for t in transactions):
            raise ValueError('Unsigned transaction')

        # merkle tries
        if prev_block is None:
            state_trie = MerkleTrie(MerkleTrieStorage())
            genesis_contract = Account(
                cls.genesis_pubkey,
                0,
                """
                    5
                    OP_PACK
                    OP_DUP
                    OP_UNPACK
                    OP_POPVOID
                    OP_CREATECONTR
                    2
                    OP_JUMPRC
                    OP_KILL
                    OP_UNPACK
                    OP_POPVOID
                    OP_HASH
                    []
                    OP_SWAP
                    OP_GETBAL
                    OP_TRANSFER
                    1
                    OP_RET
                """,
                False,
                [])
            state_trie = state_trie.put(genesis_contract.address, genesis_contract.hash)
        else:
            state_trie = prev_block.skeleton.state_trie

        tx_trie = MerkleTrie(MerkleTrieStorage())
        for tx in transactions:
            state_trie = transit(ScriptInterpreter, state_trie, tx, miner_address)
            if state_trie is None:
                raise ValueError('Invalid transaction')
            tx_trie = tx_trie.put(tx.hash, tx.hash)

        prev_accumulated_difficulty = 0 if prev_block is None else prev_block.skeleton.accumulated_difficulty

        constructed = super().__new__(cls)
        constructed._prev_block_hash = bytes(32) if prev_block is None else prev_block.hash
        constructed._timestamp = timestamp
        constructed._height = 1 if prev_block is None else prev_block.skeleton.height + 1
        constructed._difficulty = 1000 # TODO: protocol rule
        constructed._accumulated_difficulty = constructed._difficulty + prev_accumulated_difficulty
        constructed._miner_address = miner_address
        constructed._state_trie = state_trie
        constructed._tx_trie = tx_trie
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
    def state_trie(self):
        return self._state_trie

    @property
    def tx_trie(self):
        return self._tx_trie

    @property
    def hash(self):
        return compute_hash(json.dumps(self.to_json_compatible()).encode())

    def to_json_compatible(self):
        var = {}
        var['prev_block_hash'] = None if self.prev_block is None else hexlify(self.prev_block.hash).decode()
        var['timestamp'] = self.timestamp
        var['height'] = self.height
        var['difficulty'] = self.difficulty
        var['state_root'] = hexlify(self.state_trie.hash).decode()
        var['tx_root'] = hexlify(self.tx_trie.hash).decode()
        return var

    @classmethod
    def from_json_compatible(cls, var: dict, transactions: List[Transaction]):
        # prev_block
        prev_block_hash = var['prev_block_hash']
        if prev_block_hash is None:
            prev_block = None
        else:
            prev_block = Block.get_from_hash(prev_block_hash)
            if prev_block is None:
                raise ValueError('Previous block does not exist')

        miner_address = val['miner_address']
        timestamp = val['timestamp']

        skeleton = BlockSkeleton(prev_block, transactions, miner_address, timestamp)
        if skeleton.to_json_compatible() != val:
            raise ValueError('Block verification failed')
        return skeleton
