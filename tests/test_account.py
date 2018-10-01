import json

from src.blockchain.account import Account, StorageItem


def test_account_serializing():
    storage = StorageItem("var", str, "value")
    account = Account(bytes(1), 0, "code", True, [storage])
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
    account_with_int = Account(bytes(1), 0, "code", True, [StorageItem("test_var", int, 42)])
    assert None == account_with_int.set_storage("nonexistent", 3)
    assert None == account_with_int.set_storage("test_var", "invalid")
    new_account = account_with_int.set_storage("test_var", 27)
    assert new_account.get_storage("test_var") == 27
