import json

import pytest

from src.blockchain.account import Account

def test_tx_input():
    account = Account(bytes(1), 0, "code", True, "test")
    jsonstr = json.dumps(account.to_json_compatible())
    print(jsonstr)

    restoredAccount = Account.from_json_compatible(json.loads(jsonstr))

    assert account.hash == restoredAccount.hash
    account2 = account.add_to_balance(5)
    assert account2.balance == account.balance + 5
    account3 = account2.add_to_balance(-5)
    assert account3.hash == account.hash
    with pytest.raises(ValueError):
        account3.add_to_balance(-1)
