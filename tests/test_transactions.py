import json

from src.blockchain.new_transaction import Transaction, TransactionData, TransactionInput, TransactionOutput

def test_tx_input():
    tx_input = TransactionInput(bytes(32), 10)
    assert json.dumps(tx_input.to_json_compatible()) == '{"address": "0000000000000000000000000000000000000000000000000000000000000000", "value": 10}'
    tx_output = TransactionOutput(b"2342342", 8)
    tx_data = TransactionData([tx_input], [tx_output], 2, bytes(32))
    #tx = Transaction(tx_data, (bytes(32),) * len(tx_data.inputs))

    tx = Transaction(tx_data)
    jsonstr = json.dumps(tx.to_json_compatible())
    #print(jsonstr)

    tx2 = Transaction.from_json_compatible(json.loads(jsonstr))

    assert tx.hash == tx2.hash
