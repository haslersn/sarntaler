import logging

import typing
from src.blockchain.transaction import *
from src.blockchain.merkle_trie import MerkleTrie
from src.blockchain.account import Account


def transit(script_interpreter_cls: type, state: MerkleTrie, transaction: Transaction, miner_address: bytes):
    tx_inputs = transaction.tx_data.inputs
    tx_outputs = transaction.tx_data.outputs

    for input in tx_inputs:
        if not state.contains(input.address):
            # input address does not exist
            logging.warning("state_transition: input address doesn't exist")
            return None
        acc = state.get(input.address)
        acc = acc.add_to_balance(- input.value)
        if acc is None:
            # couldn't spend value
            logging.warning(
                "state_transition: couldn't deduct value from input account")
            return None
        state = state.put(input.address, acc)

    for output in tx_outputs:
        if not state.contains(output.address):
            logging.warning("state transition: output address does not exist")
            return None
        acc = state.get(output.address)
        acc = acc.add_to_balance(output.value)
        state = state.put(output.address, acc)
        if acc.code is not None:
            vm = script_interpreter_cls(state, output.params, acc, [
                                        txin.address for txin in tx_inputs], output.value)
            result = vm.execute_script()
            if result is None:
                logging.warning(
                    "state transition: target account code execution failed")
                return None
            state = result[0]

    if miner_address != bytes(32):
        # Miner gets his fee if the miner_address is not zero
        if not state.contains(miner_address):
            # no miner address
            return None
        acc = state.get(miner_address)
        acc = acc.add_to_balance(transaction.tx_data.fee)
        state = state.put(miner_address, acc)

    return state
