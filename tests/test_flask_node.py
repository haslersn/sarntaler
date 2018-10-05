import pytest
import subprocess
import os
import signal
import time
import requests
import logging
import json
from src.blockchain.new_block import *

logging.basicConfig(level=logging.INFO)

example_keypair = generate_keypair()
example_keypair2 = generate_keypair()
example_pubkey = pubkey_from_keypair(example_keypair)
example_pubkey2 = pubkey_from_keypair(example_keypair2)
example_address = compute_hash(example_pubkey)
example_address2 = compute_hash(example_pubkey2)

session = requests.Session()
url = "http://localhost:5000/"

@pytest.fixture(scope='session', autouse=True)
def node():
    env = os.environ
    env['FLASK_APP'] = 'src/node/flask_node.py'
    env['FLASK_ENV'] = 'development'
    env['FLASK_DEBUG'] = '1'
    proc = subprocess.Popen(['python3', '-m', 'flask', 'run'], env=env)
    time.sleep(1)
    logging.info('NODE: Started with pid {}'.format(proc.pid))
    yield
    logging.info('NODE: Trying to kill process with pid {}'.format(proc.pid))
    os.kill(proc.pid, signal.SIGTERM)
    logging.info('NODE: Killed process with pid {}'.format(proc.pid))

def rest_call(relative_url: str, data: dict = None):
    logging.info('rest_call: Trying to access {} with data: {}'.format(relative_url, data))
    json_headers = {"Content-Type": "application/json"}
    if data is None:
        resp = session.post(url + relative_url, headers=json_headers)
    else:
        resp = session.post(url + relative_url, data=json.dumps(data).encode(), headers=json_headers)
    resp.raise_for_status()
    logging.info('Response: {}'.format(resp.content))
    return None if resp.content == b'' else json.loads(resp.content.decode())

def test_get_latest_block(node):
    rest_call('get_latest_block')

def test_add_empty_block(node):
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
   var['transactions'] = [ tx.to_json_compatible() for tx in block.skeleton.transactions ]
   rest_call('add_block', var)

def test_create_and_call_gcd_account(node):
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

    var = {}
    var['block'] = block.to_json_compatible()
    var['transactions'] = [ tx.to_json_compatible() for tx in block.skeleton.transactions ]
    rest_call('add_block', var)

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
    var['transactions'] = [ tx.to_json_compatible() for tx in block.skeleton.transactions ]
    rest_call('add_block', var)
