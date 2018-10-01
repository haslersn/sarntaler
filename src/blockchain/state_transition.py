import typing
import src.blockchain.new_transaction.py as t
from src.blockchain.merkle_trie import MerkleTrie
from src.blockchain.account import Account
from src.scriptinterpreter import ScriptInterpreter

def transit(state : MerkleTrie, transaction : t.Transaction, miner_add : bytes):
    transInputs =  transaction.tx_data.inputs
    transOutputs = transaction.tx_data.outputs


    for transInput in transInputs:

        if not state.contains(transInput.address):
            #inputAcc not existing
            return None

        acc = Account.get_from_hash(state.get(transInput.address))

        try:
            acc = acc.add_to_balance(- transInput.value)
        except ValueError:
            # Transaction-Sender has not enough money
            return None

        state = state.put(transInput.address, acc.hash)

    for transOutput in transOutputs:
        if not state.contains(transOutput.address):
            #outputAcc not existing
            return None

        acc = acc.get_from_hash(state.get(transOutput.address))

        acc = acc.add_to_balance(transOutput.value)
        state = state.put(transOutput.address, acc.hash)

        if acc.code != None:
            vm = ScriptInterpreter(state, transOutput.params, acc, transaction.hash)
            state = vm.execute_script()


    #Miner gets his fee
    if not state.contains(miner_add):
        #no miner address
        return None

    acc = Account.get_from_hash(state.get(miner_add))
    acc = acc.add_to_balance(transaction.tx_data.fee)
    state = state.put(acc, acc.hash)

    return state
