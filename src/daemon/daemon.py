""" The RPC functionality the miner provides for the wallet and the blockchain explorer."""

import flask
import json

from src.blockchain.block import *
from src.blockchain.crypto import *

########
logging.basicConfig(level=logging.WARNING)
########


class SarntalerDaemon:
    def __init__(self):
        self._app = flask.Flask(__name__)
        self._latest_block = None  # TODO: Maybe read the serialized blockchain from disk


daemon = SarntalerDaemon()
app = daemon._app


def _get_block_by_hash(hash: bytes):
    logging.info('Block requested with hash {}'.format(hash))
    block = Block.get_from_hash(hash)
    if block is None:
        logging.info('Requested block is unknown')
        return '"None"'
    result = {}
    result['block'] = block.to_json_compatible()
    result['transactions'] = [tx.to_json_compatible()
                              for tx in block.skeleton.transactions]
    return json.dumps(result)


@app.route("/get_latest_block", methods=['POST'])
def get_latest_block():
    """
    Returns the known block with the highest accumulated difficulty
    """
    return '"None"' if daemon._latest_block is None else _get_block_by_hash(daemon._latest_block.hash)


@app.route("/get_block_by_hash", methods=['POST'])
def get_block_by_hash():
    """
    Returns the block with the requested hash if it is known.
    """
    hash = hex_to_bytes(flask.request.json['hash'])
    return _get_block_by_hash(hash)


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
    block = Block.from_json_compatible(block_compat, transactions)
    target = 0 if daemon._latest_block is None else daemon._latest_block.skeleton.accumulated_difficulty
    if block.skeleton.accumulated_difficulty > target:
        daemon._latest_block = block
    return json.dumps(True)
