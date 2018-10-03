import pytest
import subprocess
import os
import signal
import time
import requests
import logging
import json
from src.blockchain.new_block import *

@pytest.fixture(scope='session', autouse=True)
def node():
    global session, url
    session = requests.Session()
    url = "http://localhost:5000/"

    env = os.environ
    env['FLASK_APP'] = 'src/node/flask_node.py'
    env['FLASK_ENV'] = 'development'
    env['FLASK_DEBUG'] = '1'
    proc = subprocess.Popen(['python3', '-m', 'flask', 'run'], env=env)
    time.sleep(1)
    print('NODE: Started with pid {}'.format(proc.pid))
    yield
    print('NODE: Trying to kill process with pid {}'.format(proc.pid))
    os.kill(proc.pid, signal.SIGTERM)
    print('NODE: Killed process with pid {}'.format(proc.pid))

def rest_call(relative_url: str, data: dict = None):
    print()
    print('rest_call: Trying to access {}'.format(relative_url))
    json_headers = {"Content-Type": "application/json"}
    if data is None:
        resp = session.post(url + relative_url, headers=json_headers)
    else:
        resp = session.post(url + relative_url, data=json.dumps(data).encode(), headers=json_headers)
    resp.raise_for_status()
    print('RESPONSE: {}'.format(resp.content))
    return None if resp.content == b'' else json.loads(resp.content.decode())

def test_get_latest_block(node):
    rest_call('get_latest_block')

def test_add_block(node):
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

def test_get_block_transactions(node):
   block_compat = rest_call('get_latest_block')
   block_hash = hexlify(compute_hash(json.dumps(block_compat).encode())).decode()
   rest_call('get_block_transactions', { 'hash': block_hash })
