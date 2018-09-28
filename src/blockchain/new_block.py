

class Block:

    def __init__(self, prev_block_hash, time, nonce, height, received_time, target, transactions, tx_root_hash, id=None):
        """ This is not meant to be called from the outside, but by create()!  """
        self.id = id
        self.prev_block_hash = prev_block_hash
        self.time = time
        self.height = height
        self.received_time = received_time
        self.target = target
        self.transactions = transactions
        self.mpt_root_hash = mpt_root_hash
        self.id = id
        self._hash = _get_hash()

    @classmethod
    def create(cls, chain_difficulty: int, prev_block: 'Block', transactions: List[Transaction], ts=None):
        # verify and execute transactions
        state_trie = self.verify_txs(prev_block.state_trie) # TODO TODO TODO !!!
        # and build new merkle-patricia transaction tree tree
        tx_trie = MerkleTrie()
        for tx in transactions:
            trie = trie.put(tx.hash, tx.hash)
        id = prev_block.height + 1
        if ts is None: # ts = timestamp
            ts = datetime.utcnow()
        if ts <= prev_block.time:
            ts = prev_block..time + timedelta(microseconds=1)
        return Block(   prev_block_hash, ts, 0, prev_block.height + 1, None,
                        chain_difficulty, transactions, tx_trie.hash, id)
