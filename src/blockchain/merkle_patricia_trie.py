from collections import namedtuple
from hashlib import sha256

def is_hash(key: bytes) -> int:
    return len(key)

def compute_hash(to_hash: bytes) -> bytes:
    m = sha256()
    m.update(to_hash)
    return m.digest()

def _mpt_check_is_encoded_path(str: bytes):
    if len(str) != 32:
        raise ValueError('encoded_path must have length 32')

def _mpt_check_is_value(str: bytes):
    if len(str) != 32:
        raise ValueError('value must have length 32')

def _mpt_check_is_leaf(str: bytes):
    if str is None:
        return True
    if len(str) != 32:
        raise ValueError('leaf must have length 32')

def _mpt_check_is_inner(node):
    if type(node) not in [ MerklePatriciaTrie, type(None) ]:
        raise ValueError('Corructed merkle patricia tree. Expected MerklePatriciaTrie')

def _mpt_hash(node) -> bytes:
    if node is None:
        return bytes(32)
    if type(node) is MerklePatriciaTrie:
        return node.hash
    return node

class MerklePatriciaTrie(namedtuple("MerklePatriciaTrie", ["children", "hash"])):
    def __new__(self, children: tuple = (None,) * 16):
        if len(children) != 16:
            raise ValueError('Number of children must be 16')
        all_inner = all(type(child) in [ MerklePatriciaTrie, type(None) ] for child in children)
        if not all_inner and not all(type(child) in [ bytes, type(None) ] for child in children):
            raise ValueError('Illegal child type')
        to_hash = bytes()
        for child in children:
            # None is represented by the hash 0 (32 bytes of zeros)
            to_hash += _mpt_hash(child)
        assert(len(to_hash) == 32 * 16)
        hash = compute_hash(to_hash)
        return super().__new__(self, children, hash)

def _mpt_child_index(encoded_path: bytes, deepness: int):
    child_index = encoded_path[deepness // 2]
    if deepness % 2 == 0:
        child_index //= 16
    else:
        child_index %= 16
    return child_index

def _mpt_put_internal(root, encoded_path: bytes, value: bytes, deepness: int) -> MerklePatriciaTrie:
    if deepness == 64:
        _mpt_check_is_leaf(root)
        return value
    _mpt_check_is_inner(root)
    child_index = _mpt_child_index(encoded_path, deepness)
    old_children = (None,) * 16 if root is None else root.children
    old_child = old_children[child_index]
    new_child = _mpt_put_internal(old_child, encoded_path, value, deepness + 1)
    new_children = old_children[:child_index] + (new_child,) + old_children[child_index+1:]
    return MerklePatriciaTrie(new_children)

def _mpt_remove_internal(root: MerklePatriciaTrie, encoded_path: bytes, deepness: int):
    if root is None:
        return (None, False)
    if deepness == 64:
        _mpt_check_is_leaf(root)
        return (None, True)
    _mpt_check_is_inner(root)
    child_index = _mpt_child_index(encoded_path, deepness)
    old_children = root.children
    old_child = old_children[child_index]
    new_child, did_remove = _mpt_remove_internal(old_child, encoded_path, deepness + 1)
    if not did_remove:
        return (root, False)
    new_children = old_children[:child_index] + (new_child,) + old_children[child_index+1:]
    if deepness != 0 and new_children == (None,) * 16:
        return (None, True)
    return (MerklePatriciaTrie(new_children), True)

def _mpt_get_internal(root: MerklePatriciaTrie, encoded_path: bytes, deepness: int):
    if root is None:
        return None
    if deepness == 64:
        _mpt_check_is_leaf(root)
        return root.value
    child_index = _mpt_child_index(encoded_path, deepness)
    child = root.children[child_index]
    return _mpt_get_internal(child, encoded_path, deepness + 1)

def mpt_put(root: MerklePatriciaTrie, encoded_path: bytes, value: bytes) -> MerklePatriciaTrie:
    _mpt_check_is_encoded_path(encoded_path)
    _mpt_check_is_value(value)
    return _mpt_put_internal(root, encoded_path, value, 0)

def mpt_remove(root: MerklePatriciaTrie, encoded_path: bytes) -> MerklePatriciaTrie:
    _mpt_check_is_encoded_path(encoded_path)
    return _mpt_remove_internal(root, encoded_path, 0)

def mpt_get(root: MerklePatriciaTrie, encoded_path: bytes) -> bytes:
    _mpt_check_is_encoded_path(encoded_path)
    return _mpt_get_internal(root, encoded_path, 0)

def mpt_contains(root: MerklePatriciaTrie, encoded_path: bytes) -> bool:
    return mpt_get(root, encoded_path) is not None

def _mpt_hashes_stack(root: MerklePatriciaTrie, encoded_path: bytes, deepness: int) -> tuple:
    if root is None:
        return None
    if deepness == 64:
        _mpt_check_is_leaf(root)
        return () # empty tuple
    child_index = _mpt_child_index(encoded_path, deepness)
    child = root.children[child_index]
    intermediate = _mpt_hashes_stack(child, encoded_path, deepness + 1)
    return None if intermediate is None else intermediate + tuple(map_func(lambda c: _mpt_hash(c), root.children))

class MerkleProof(namedtuple("MerkleProof", [ "encoded_path", "hashes_stack", "root_hash"])):
    def __new__(cls, trie: MerklePatriciaTrie, encoded_path: bytes):
        _mpt_check_is_encoded_path(encoded_path)
        value = mpt_get(encoded_path)
        hashes_stack = _mpt_hashes_stack(trie, encoded_path, 0)
        root_hash = trie.hash
        return super().__new__(cls, encoded_path, value, hashes_stack, root_hash)

trie = MerklePatriciaTrie()
print(trie)
mpt_put(trie, bytes([0x55] * 32), bytes(32))
print(trie)
assert mpt_contains(trie, bytes([0x55] * 32))
assert not mpt_contains(trie, [0x77] * 32)
proof = MerkleProof(trie, [0x55] * 32)
print(proof)
