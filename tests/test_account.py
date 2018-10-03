import json
import pytest

from src.blockchain.account import Account, StorageItem
from src.blockchain.crypto import *

example_keypair = generate_keypair()
example_pubkey = pubkey_from_keypair(example_keypair)

def test_account_serializing():
    storage = StorageItem("var", "str", "value")
    account = Account(example_pubkey, 0, "code", True, [storage])
    jsonstr = json.dumps(account.to_json_compatible())
    print(jsonstr)

    restoredAccount = Account.from_json_compatible(json.loads(jsonstr))
    assert account.hash == restoredAccount.hash
    account2 = account.add_to_balance(5)
    assert account2.balance == account.balance + 5
    account3 = account2.add_to_balance(-5)
    assert account3.hash == account.hash
    assert None == account3.add_to_balance(-1)


def test_account_storage():
    account = Account(example_pubkey, 0, "code", True, [StorageItem("test_var", "int", 42), StorageItem("test_string", "str", "init")])
    assert None == account.set_storage("nonexistent", 3)
    assert None == account.set_storage("test_var", "invalid")
    new_account = account.set_storage("test_var", 27)
    assert new_account.get_storage("test_var") == 27
    assert None == new_account.get_storage("nonexistent")

    assert "init" == account.get_storage("test_string")
    assert None == account.set_storage("test_string", 2)

    with pytest.raises(ValueError):
        assert None == Account(example_pubkey, 0, "code", True, [StorageItem("test_var", "int", "not an int"), StorageItem("test_string", "str", "init")])
