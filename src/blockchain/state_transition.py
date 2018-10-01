import typing
import src.blockchain.new_transaction.py as t
from src.blockchain.merkle_trie import MerkleTrie
from src.blockchain.account import Account as acc
#TODO: import vm

def transit(state : MerkleTrie, transaction : t.Transaction, miner_add : bytes):
    transInputs =  transaction.tx_data.inputs
    transOutputs = transaction.tx_data.outputs

    for transOutput in transOutputs:
        if not state.contains(transOutput.address):
            #outputAcc not existing
            return None

        outAcc = acc.get_from_hash(state.get(transOutput.address))
        if outAcc.code != None:
            new_state = vm.execute(transOutput.params + "\n" + outAcc.code)

        newAcc = outAcc.add_to_balance(transOutput.value)
        state = state.put(transOutput.address, newAcc.hash)


    for transInput in transInputs:

        if not state.contains(transInput.address):
            #inputAcc not existing
            return None

        inputAcc = acc.get_from_hash(state.get(transInput.address))

        try:
            newAcc = inputAcc.add_to_balance(- transInput.value)
        except ValueError:
            # Transaction-Sender has not enough money
            return None

        state = state.put(transInput.address, newAcc.hash)


    #Miner gets his fee
    if not state.contains(miner_add):
        #no miner address
        return None

    minerAcc = acc.get_from_hash(state.get(miner_add))
    newAcc = minerAcc.add_to_balance(transaction.tx_data.fee)
    state = state.put(minerAcc, newAcc.hash)

    return state

