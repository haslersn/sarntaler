""" The RPC functionality the miner provides for the wallet and the blockchain explorer."""

import binascii
import json
import time
from binascii import hexlify
from datetime import datetime
from sys import maxsize

from src.blockchain.account import Account
from src.blockchain.new_transaction import Transaction
import flask
from flask_api import status

#from .chainbuilder import ChainBuilder
from src.crypto import Key
#from .persistence import Persistence
#from .config import DIFFICULTY_BLOCK_INTERVAL
#from .transaction import TransactionInput

########
rest_port = 5000
########

class FlaskNode:
    def __init__(self, port: int):
        self._app = flask.Flask(__name__)
        self._app.run(port=port)
        self._latest_block = None # TODO: Maybe read the serialized blockchain from disk

node = FlaskNode(rest_port)
app = node._app

@app.route("/get_latest_block", methods=['POST'])
def get_latest_block():
    """
    Returns the known block with the highest accumulated difficulty
    """
    return '' if node._latest_block is None else json.dumps(node._latest_block.to_json_compatible())

@app.route("/get_block_by_hash", methods=['POST'])
def get_block_by_hash():
    """
    Returns the block with the requested hash if it is known.
    """
    hash = unhexlify(flask.request.json['hash'])
    return '' if hash not in node._blocks else json.dumps(node._blocks[hash].to_json_compatible())

@app.route("/get_block_transactions", methods=['POST'])
def get_block_transactions():
    """
    Returns a list of transactions that are contained in the block with the requested hash.
    """
    hash = unhexlify(flask.request.json['hash'])
    if hash not in node._blocks:
        return ''
    transactions = node._blocks[hash].transactions
    json_compat = [ tx.to_json_compatible() for tx in transactions ]
    return json.dumps(json_compat)

@app.route("/add_block", methods=['POST'])
def add_block():
    """
    Appends a block to the blockchain.
    """
    for i in range(10):
        print('debug')
    block_compat = flask.request.json['block']
    transactions_compat = flask.request.json['transactions']
    transactions = [ Transaction.from_json_compatible(tx_compat) for tx_compat in transactions_compat ]
    block = Block.from_json_compatible(block_compat, transactions)
    if node._latest_block is None or block.accumulated_difficulty > node._latest_block.difficulty:
        node._latest_block = block
