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

app = flask.Flask(__name__)
cb = None
pers = None
unusedtrans = []

def rpc_server(port: int, chainbuilder: ChainBuilder, persist: Persistence):
    #ToDo: right parameters
    """ Runs the RPC server (forever). """
    global cb
    cb = chainbuilder
    global pers
    pers = persist

    app.run(port=port)

@app.route("/get-status", methods=['POST'])
def get_status():
    """
    Returns the balance of an account.
    Route: `\"/get-status\"`.
    HTTP Method: `'POST'`
    """
    accounts = {Account.get_from_hash(addr): i for (i, addr) in enumerate(flask.request.json)}
    return accounts[:].to_json_compatible()

@app.route("/new-transaction", methods=['PUT'])
def send_transaction():
    """
    Sends a transaction to the network, and uses it for mining.
    Route: `\"/new-transaction\"`.
    HTTP Method: `'PUT'`
    """
    trans = Transaction.from_json_compatible(flask.request.json)
    #todo: transacton to blockchain
    unusedtrans.index(trans)
    return

def get_unusedtrans():
    """Returns locally saved Transaction, which are not validated yet
    to a miner/network which takes care of the Transactions."""
    tmptr = unusedtrans.copy()
    unusedtrans.clear()
    return tmptr

