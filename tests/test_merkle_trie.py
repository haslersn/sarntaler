from src.blockchain.merkle_trie import *
import pytest

def test_put_and_remove():
    key = Crypto.compute_hash(bytes([ 1 ]))
    value = Crypto.compute_hash(bytes([ 2 ]))

    trie1 = MerkleTrie()
    assert not trie1.contains(key)

    trie2 = trie1.put(key, value)
    assert not trie2.contains(bytes([0x56] * 32))
    assert trie2.contains(key)
    assert trie2.get(key) == value
    assert trie1 != trie2

    trie3, did_remove = trie2.remove(key)
    assert did_remove
    assert not trie3.contains(key)
    print(trie1)
    print()
    print()
    print()
    print()
    print(trie3)
    assert trie1 == trie3

    trie4, did_remove = trie3.remove(key)
    assert not did_remove
    assert trie3 == trie4

def test_put_multiple():
    def key(i):
        return Crypto.compute_hash(bytes([i]))
    def value(i):
        return Crypto.compute_hash(bytes([0, i]))

    trie = MerkleTrie()
    for i in range(100):
        trie = trie.put(key(i), value(i))
        for j in range(100):
            k = key(j)
            if j <= i:
                assert trie.contains(k)
                assert trie.get(k) == value(j)
            else:
                assert not trie.contains(k)
                assert trie.get(k) is None

def test_cherry_pick_and_merge():
    def key(i):
        return Crypto.compute_hash(bytes([i]))
    def value(i):
        return Crypto.compute_hash(bytes([0, i]))

    trie1 = MerkleTrie()
    for i in range(10):
        trie1 = trie1.put(key(i), value(i))

    trie_a = trie1.cherry_pick(map(key, range(5)))
    trie_b = trie1.cherry_pick(map(key, range(5, 10)))
    for i in range(10):
        assert trie_a.contains(key(i)) != trie_b.contains(key(i))

    trie2 = MerkleTrie.merge(trie_a, trie_b)
    assert trie1 == trie2

test_put_and_remove()
test_put_multiple()
test_cherry_pick_and_merge()
