import pytest
import subprocess
import os
import signal
import time
import requests
import logging
import json

from src.blockchain.block import *
from src.node.flask_node import app

logging.basicConfig(level=logging.WARNING)

example_keypair = generate_keypair()
example_keypair2 = generate_keypair()
example_pubkey = pubkey_from_keypair(example_keypair)
example_pubkey2 = pubkey_from_keypair(example_keypair2)
example_address = compute_hash(example_pubkey)
example_address2 = compute_hash(example_pubkey2)

session = app.test_client()


def query_node(path: str, json_data: dict = None):
    logging.info('query_node: Trying to access {} with data: {}'.format(
        path, json_data))
    json_headers = {"Content-Type": "application/json"}
    bytes_data = None if json_data is None else json.dumps(json_data)
    bytes_resp = session.post(path, data=bytes_data, headers=json_headers).data
    return json.loads(bytes_resp.decode())


def test_get_latest_block():
    query_node('get_latest_block')


def test_add_empty_block():
    skeleton = BlockSkeleton(None, [], bytes(32))
    nonce_int = 0
    block = None
    while block is None:
        nonce = nonce_int.to_bytes(32, 'big')
        try:
            block = Block(skeleton, nonce)
        except ValueError:
            nonce_int += 1
    print('test_add_block: Nonce was {}'.format(nonce_int))

    var = {}
    var['block'] = block.to_json_compatible()
    var['transactions'] = [tx.to_json_compatible()
                           for tx in block.skeleton.transactions]
    query_node('add_block', var)


def test_create_and_call_gcd_account():
    f = open("src/labvm/testprograms/gcd_callable.labvm", "r")
    assert f is not None
    fstr = f.read()
    f.close()
    script = "[] [] 0 '{}' k0x{}".format(fstr, bytes_to_hex(example_pubkey))
    tx_output = TransactionOutput(compute_hash(
        BlockSkeleton.genesis_pubkey), 0, script)
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

    var = {}
    var['block'] = block.to_json_compatible()
    var['transactions'] = [tx.to_json_compatible()
                           for tx in block.skeleton.transactions]
    query_node('add_block', var)

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

    var = {}
    var['block'] = block.to_json_compatible()
    var['transactions'] = [tx.to_json_compatible()
                           for tx in block.skeleton.transactions]
    query_node('add_block', var)
