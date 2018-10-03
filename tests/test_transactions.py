import json

from src.blockchain.new_transaction import Transaction, TransactionData, TransactionInput, TransactionOutput

def test_tx():
    tx_input = TransactionInput(bytes([17] * 32), 10)
    assert json.dumps(tx_input.to_json_compatible()) == '{"address": "1111111111111111111111111111111111111111111111111111111111111111", "value": 10}'

    tx_output = TransactionOutput(bytes([1] * 32), 8)
    assert json.dumps(tx_output.to_json_compatible()) == '{"address": "0101010101010101010101010101010101010101010101010101010101010101", "value": 8, "params": null}'

    tx_data = TransactionData([tx_input], [tx_output], 2, bytes(32))
    assert json.dumps(tx_data.to_json_compatible()) == '{"inputs": [{"address": "1111111111111111111111111111111111111111111111111111111111111111", "value": 10}], "outputs": [{"address": "0101010101010101010101010101010101010101010101010101010101010101", "value": 8, "params": null}], "fee": 2, "nonce": "0000000000000000000000000000000000000000000000000000000000000000"}'

    tx = Transaction(tx_data)
    serialized = json.dumps(tx.to_json_compatible())
    assert serialized == '{"tx_data": {"inputs": [{"address": "1111111111111111111111111111111111111111111111111111111111111111", "value": 10}], "outputs": [{"address": "0101010101010101010101010101010101010101010101010101010101010101", "value": 8, "params": null}], "fee": 2, "nonce": "0000000000000000000000000000000000000000000000000000000000000000"}, "signatures": ["0000000000000000000000000000000000000000000000000000000000000000"]}'

    deserialized = Transaction.from_json_compatible(json.loads(serialized))
    serialized_again = json.dumps(tx.to_json_compatible())

    assert tx.hash == deserialized.hash # TODO: just use tx eq function
    assert serialized == serialized_again
