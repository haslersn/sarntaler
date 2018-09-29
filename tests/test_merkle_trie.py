from src.blockchain.merkle_trie import *
import pytest
import json

def gen_key(i):
    return Crypto.compute_hash(bytes([i]))
def gen_value(i):
    return Crypto.compute_hash(bytes([0, i]))

def test_put_and_remove():
    key = gen_key(1)
    value = gen_value(1)

    # construct
    trie1 = MerkleTrie()
    assert not trie1.contains(key)

    # put
    trie2 = trie1.put(key, value)
    assert not trie2.contains(bytes([0x56] * 32))
    assert trie2.contains(key)
    got = trie2.get(key)
    assert got == value
    assert trie1 != trie2

    # remove
    trie3, did_remove = trie2.remove(key)
    assert did_remove
    assert not trie3.contains(key)
    assert trie1 == trie3

    # remove again (checking idempotence)
    trie4, did_remove = trie3.remove(key)
    assert not did_remove
    assert trie3 == trie4

def test_put_multiple():
    trie = MerkleTrie()
    for i in range(10):
        trie = trie.put(gen_key(i), gen_value(i))
        for j in range(10):
            key = gen_key(j)
            if j <= i:
                assert trie.contains(key)
                assert trie.get(key) == gen_value(j)
            else:
                assert not trie.contains(key)
                assert trie.get(key) is None
