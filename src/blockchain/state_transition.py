import typing

def transit(old_state, transaction : Transaction):
    transInputs =  transaction.tx_data.inputs
    transOutputs = transaction.tx_data.outputs
    for transInput in transInputs:

