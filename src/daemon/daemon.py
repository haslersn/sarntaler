""" The RPC functionality the miner provides for the wallet and the blockchain explorer."""

import flask
import json

from src.blockchain.block import *
from src.blockchain.crypto import *

########
logging.basicConfig(level=logging.WARNING)
########


app = flask.Flask(__name__)

_blockchain = Blockchain()


def _dump_block_and_tx(block: Block):
    result = {}
    result['block'] = block.to_json_compatible()
    result['transactions'] = [tx.to_json_compatible()
                              for tx in block.skeleton.transactions]
    return json.dumps(result)


def _dump_block_and_tx_from_hash(hash: bytes):
    logging.info('Block requested with hash {}'.format(hash))
    block = _blockchain.block(hash)
    if block is None:
        logging.info('Requested block is unknown')
        return json.dumps(None)
    return _dump_block_and_tx(block)


@app.route("/get_highest_block", methods=['POST'])
def get_highest_block():
    """
    Returns the known block with the highest accumulated difficulty
    """
    heads = _blockchain.heads()
    if not heads:
        return json.dumps(None)
    highest = max(heads, key=lambda h: h.accumulated_difficulty)
    return _dump_block_and_tx(highest)


@app.route("/get_block_by_hash", methods=['POST'])
def get_block_by_hash():
    """
    Returns the block with the requested hash if it is known.
    """
    hash = hex_to_bytes(flask.request.json['hash'])
    return _dump_block_and_tx_from_hash(hash)


@app.route("/add_block", methods=['POST'])
def add_block():
    """
    Appends a block to the blockchain.
    """
    logging.info('Adding a block requested')
    transactions_compat = flask.request.json['transactions']
    logging.info('Transactions: {}'.format(transactions_compat))
    transactions = map(Transaction.from_json_compatible, transactions_compat)
    block_compat = flask.request.json['block']
    logging.info('Block: {}'.format(block_compat))
    _blockchain.push_head_from_json_compatible(block_compat, transactions)
    return json.dumps(True)
