import typing
from src.blockchain.new_transaction.py import *
from src.blockchain.merkle_trie import MerkleTrie
from src.blockchain.account import Account
from src.scriptinterpreter import ScriptInterpreter

def transit(state : MerkleTrie, transaction : Transaction, miner_address : bytes):
    tx_inputs =  transaction.tx_data.inputs
    tx_outputs = transaction.tx_data.outputs

    for input in tx_inputs:
        if not state.contains(input.address):
            # input address does not exist
            return None
        acc = Account.get_from_hash(state.get(input.address))
        acc = acc.add_to_balance(- input.value)
        if acc is None:
            # couldn't spend value
            return None
        state = state.put(input.address, acc.hash)

    for output in tx_outputs:
        if not state.contains(output.address):
            # output address does not exist
            return None
        acc = Account.get_from_hash(state.get(output.address))
        acc = acc.add_to_balance(output.value)
        state = state.put(output.address, acc.hash)
        if acc.code is not None:
            vm = ScriptInterpreter(state, output.params, acc, transaction.hash)
            state = vm.execute_script()

    if miner_address != bytes(32):
        # Miner gets his fee if the miner_address is not zero
        if not state.contains(miner_address):
            #no miner address
            return None
        acc = Account.get_from_hash(state.get(miner_address))
        acc = acc.add_to_balance(transaction.tx_data.fee)
        state = state.put(miner_address, acc.hash)

    return state