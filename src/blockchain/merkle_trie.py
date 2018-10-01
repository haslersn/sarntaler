from binascii import hexlify, unhexlify
from typing import List
from src.blockchain.crypto import compute_hash, is_hash

def _empty(hash: bytes):
    return hash == bytes(32)

def _check_is_inner_depth(depth):
    if depth < 0 or depth >= 64:
        raise ValueError('Inner node index must be in [0, 63]')

def _check_is_hash(str: bytes):
    if not is_hash(str):
        raise ValueError('non-zero hash with length 32 Byte expected')

def _child_index(encoded_path: bytes, depth: int):
    child_index = encoded_path[depth // 2]
    if depth % 2 == 0:
        child_index //= 16
    else:
        child_index %= 16
    return child_index

class MerkleTrieStorage:
    def __init__(self):
        self._dicts = tuple([ dict() for _ in range(64) ])

    def _known(self, hash: bytes, depth: int):
        return hash in self._dicts[depth]

    def _check_known(self, hash: bytes, depth: int):
        if not self._known(hash, depth):
            raise ValueError('node was required to store its children')

    def _children(self, hash: bytes, depth: int):
        self._check_known(hash, depth)
        return self._dicts[depth][hash]

    def _create_inner_node(self, children, depth) -> bytes:
        _check_is_inner_depth(depth)
        if type(children) != tuple or len(children) != 16:
            raise ValueError('Illegal type of children')
        if depth != 63 and not all(c == bytes(32) or c in self._dicts[depth + 1] for c in children):
            raise ValueError('Children aren\'t known')

        to_hash = bytes()
        for child in children:
            to_hash += child
        assert(len(to_hash) == 32 * 16)
        hash = compute_hash(to_hash)

        if hash in self._dicts[depth]:
            assert self._dicts[depth][hash] == children
        else:
            self._dicts[depth][hash] = children
        return hash

    def _update_node(self, hash: bytes, encoded_path: bytes, depth: int, fn):
        child_index = _child_index(encoded_path, depth)
        if not _empty(hash):
            old_children = self._children(hash, depth)
            old_child = old_children[child_index]
            new_child = fn(old_child)
            new_children = old_children[:child_index] + (new_child,) + old_children[child_index+1:]
            if new_children == (bytes(32),) * 16:
                return bytes(32)
            else:
                return self._create_inner_node(new_children, depth)
        else:
            new_child = fn(hash)
            if _empty(new_child):
                return hash
            else:
                new_children = (hash,) * child_index + (new_child,) + (hash,) * (15 - child_index)
                return self._create_inner_node(new_children, depth)

    def _put_internal(self, hash: bytes, encoded_path: bytes, value: bytes, depth: int):
        if depth == 64:
            return value
        fn = lambda h: self._put_internal(h, encoded_path, value, depth + 1)
        return self._update_node(hash, encoded_path, depth, fn)

    def _remove_internal(self, hash: bytes, encoded_path: bytes, depth: int):
        if _empty(hash):
            return hash
        if depth == 64:
            return bytes(32)
        fn = lambda h: self._remove_internal(h, encoded_path, depth + 1)
        return self._update_node(hash, encoded_path, depth, fn)

    def _get_internal(self, hash: bytes, encoded_path: bytes, depth: int):
        if _empty(hash):
            return None
        if depth == 64:
            return hash
        children = self._children(hash, depth)
        child_index = _child_index(encoded_path, depth)
        child = children[child_index]
        return self._get_internal(child, encoded_path, depth + 1)

    def _get_all(self, hash: bytes, partial_path: bytearray, depth: int):
        if _empty(hash):
            return []
        if depth == 64:
            return [ (bytes(partial_path), hash) ]
        result = []
        for i, c in enumerate(self._children(hash, depth)):
            child_path = partial_path[:]
            if depth % 2 == 0:
                child_path.append(16 * i)
            else:
                child_path[-1] += i
            if child_path[-1] >= 256:
                assert False
            result += self._get_all(c, child_path, depth + 1)
        return result

    def _to_json_compatible(self, hash: bytes, encoded_paths: List[bytes], depth: int, let_know: bool):
        if _empty(hash):
            return None
        val = {}
        if depth == 64:
            val["value"] = hexlify(hash).decode()
        else:
            val["hash"] = hexlify(hash).decode()
            if let_know:
                children = self._children(hash, depth)
                recurse = lambda c, lk: self._to_json_compatible(c, encoded_paths, depth + 1, lk)
                if encoded_paths:
                    let_know_children_indices = map(lambda p: _child_index(encoded_path, depth), encoded_paths)
                    let_know_children = [ i in let_know_children_indices for i in range(16) ]
                    val["children"] = [ recurse(c, lk) for c, lk in zip(children, let_know_children) ]
                else:
                    val["children"] = [ recurse(c, True) for c in children ]
        return val

    def _from_json_compatible(self, val, depth: int):
        if val == None:
            return bytes(32)
        if depth == 64:
            return unhexlify(val["value"])
        fn = lambda v: self._from_json_compatible(v, depth + 1)
        children = tuple(map(fn, val["children"]))
        return self._create_inner_node(children, depth)


class MerkleTrie:
    def __init__(self, storage: MerkleTrieStorage, hash = bytes(32)):
        cls = type(self)
        _empty(hash) or _check_is_hash(hash)
        self._storage = storage
        self._hash = hash

    def __eq__(self, other): 
        return self._hash == other._hash

    @property
    def storage(self):
        return self._storage

    @property
    def hash(self):
        return self._hash

    @property
    def empty(self):
        return self.hash == bytes(32)

    def put(self, encoded_path: bytes, value: bytes):
        _check_is_hash(encoded_path)
        _check_is_hash(value)
        cls = type(self)
        return cls(self._storage, self._storage._put_internal(self.hash, encoded_path, value, 0))

    def remove(self, encoded_path: bytes):
        _check_is_hash(encoded_path)
        cls = type(self)
        new_hash = self._storage._remove_internal(self.hash, encoded_path, 0)
        return (cls(self._storage, new_hash), new_hash != self.hash)

    def get(self, encoded_path: bytes) -> bytes:
        _check_is_hash(encoded_path)
        return self._storage._get_internal(self.hash, encoded_path, 0)

    def contains(self, encoded_path: bytes) -> bool:
        return self.get(encoded_path) is not None

    def get_all(self) -> List[bytes]:
        return self._storage._get_all(self.hash, [], 0)

    def to_json_compatible(self, encoded_paths: List[bytes]):
        """ Returns a JSON-serializable representation of this object. """
        return self._storage._to_json_compatible(self.hash, encoded_paths, 0, True)

    @classmethod
    def from_json_compatible(cls, val, storage):
        """ Create a new MerkleTrie from its JSON-serializable representation. """
        return cls(storage, storage._from_json_compatible(val, 0))
