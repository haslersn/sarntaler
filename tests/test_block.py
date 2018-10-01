import json

from src.blockchain.new_block import *

def test_skeleton_after_genesis():
    skeleton = BlockSkeleton(None, [], bytes(32))
    assert skeleton.height == 1
    assert skeleton.tx_trie.empty
    assert skeleton.state_trie.empty
    assert skeleton.prev_block == None
    assert skeleton.difficulty == skeleton.accumulated_difficulty

def test_mining_blocks():
    block = None
    for i in range(10):
        skeleton = BlockSkeleton(block, [], bytes(32))
        nonce_int = 0
        block = None
        while block is None:
            nonce = nonce_int.to_bytes(32, 'big')
            try:
                block = Block(skeleton, nonce)
            except ValueError:
                pass
            nonce_int += 1
        print('Nonce was {}'.format(nonce_int))
