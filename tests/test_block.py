import json

from src.blockchain.new_block import *

example_keypair = generate_keypair()
example_pubkey = pubkey_from_keypair(example_keypair)
example_address = compute_hash(example_pubkey)

def test_skeleton_after_genesis():
    skeleton = BlockSkeleton(None, [], bytes(32))
    assert skeleton.height == 1
    assert skeleton.tx_trie.empty
    assert len(skeleton.state_trie.get_all()) == 1
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
                nonce_int += 1
        print('Nonce was {}'.format(nonce_int))

def test_create_account():
    tx_output = TransactionOutput(compute_hash(BlockSkeleton.genesis_pubkey), 0, """
        [] [] 1 '' k0x{}
    """.format(hexlify(example_pubkey).decode()))
    tx_data = TransactionData([], [tx_output], 0, bytes(32))
    tx = Transaction(tx_data)
    skeleton = BlockSkeleton(None, [tx], bytes(32))
    nonce_int = 0
    block = None
    while block is None:
        nonce = nonce_int.to_bytes(32, 'big')
        try:
            block = Block(skeleton, nonce)
        except ValueError:
            nonce_int += 1
    print('Nonce was {}'.format(nonce_int))
