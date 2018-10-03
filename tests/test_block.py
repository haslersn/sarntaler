import json

from src.blockchain.new_block import *

example_keypair = generate_keypair()
example_keypair2 = generate_keypair()
example_pubkey = pubkey_from_keypair(example_keypair)
example_pubkey2 = pubkey_from_keypair(example_keypair2)
example_address = compute_hash(example_pubkey)
example_address2 = compute_hash(example_pubkey2)

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
    print(tx_output)
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


def test_create_and_call_gcd_account():
    f = open("src/labvm/testprograms/gcd_callable.labvm", "r")
    assert f is not None
    fstr = f.read()
    f.close()
    tx_output = TransactionOutput(compute_hash(BlockSkeleton.genesis_pubkey), 0, 
        "[] [] 0 '"  + fstr + "' k0x{}".format(hexlify(example_pubkey).decode()))
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
    print('Nonce of gcdblock was {}'.format(nonce_int))

    tx_output = TransactionOutput(example_address, 0, "120 16")
    tx_data = TransactionData([], [tx_output], 0, bytes(32))
    tx = Transaction(tx_data)
    skeleton = BlockSkeleton(block, [tx], bytes(32))
    nonce_int = 0
    block = None
    while block is None:
        nonce = nonce_int.to_bytes(32, 'big')
        try:
            block = Block(skeleton, nonce)
        except ValueError:
            nonce_int += 1
    print('Nonce of call block was {}'.format(nonce_int))
