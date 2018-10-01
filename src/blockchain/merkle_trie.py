from binascii import hexlify, unhexlify
from typing import List
from src.blockchain.crypto import compute_hash, is_hash

class MerkleTrie:
    _DICTS = tuple([ dict() for _ in range(64) ])

    def __init__(self, hash = bytes(32)):
        cls = type(self)
        cls._empty(hash) or cls._check_is_hash(hash)
        self._hash = hash

    def __eq__(self, other): 
        return self._hash == other._hash

    @property
    def hash(self):
        return self._hash

    @property
    def empty(self):
        return self.hash == bytes(32)

    @staticmethod
    def _empty(hash: bytes):
        return hash == bytes(32)

    @classmethod
    def _known(cls, hash: bytes, depth: int):
        return hash in cls._DICTS[depth]

    @classmethod
    def _check_known(cls, hash: bytes, depth: int):
        if not cls._known(hash, depth):
            raise ValueError('node was required to store its children')

    @classmethod
    def _children(cls, hash: bytes, depth: int):
        cls._check_known(hash, depth)
        return cls._DICTS[depth][hash]

    @staticmethod
    def _check_is_inner_depth(depth):
        if depth < 0 or depth >= 64:
            raise ValueError('Inner node index must be in [0, 63]')

    @classmethod
    def _create_inner_node(cls, children, depth) -> bytes:
        cls._check_is_inner_depth(depth)
        if type(children) != tuple or len(children) != 16:
            raise ValueError('Illegal type of children')
        if depth != 63 and not all(c == bytes(32) or c in cls._DICTS[depth + 1] for c in children):
            raise ValueError('Children aren\'t known')

        to_hash = bytes()
        for child in children:
            to_hash += child
        assert(len(to_hash) == 32 * 16)
        hash = compute_hash(to_hash)

        if hash in cls._DICTS[depth]:
            assert cls._DICTS[depth][hash] == children
        else:
            cls._DICTS[depth][hash] = children
        return hash

    @staticmethod
    def _check_is_hash(str: bytes):
        if not is_hash(str):
            raise ValueError('non-zero hash with length 32 Byte expected')

    @staticmethod
    def _child_index(encoded_path: bytes, depth: int):
        child_index = encoded_path[depth // 2]
        if depth % 2 == 0:
            child_index //= 16
        else:
            child_index %= 16
        return child_index

    @classmethod
    def _update_node(cls, hash: bytes, encoded_path: bytes, depth: int, fn):
        child_index = cls._child_index(encoded_path, depth)
        if not cls._empty(hash):
            old_children = cls._children(hash, depth)
            old_child = old_children[child_index]
            new_child = fn(old_child)
            new_children = old_children[:child_index] + (new_child,) + old_children[child_index+1:]
            if new_children == (bytes(32),) * 16:
                return bytes(32)
            else:
                return cls._create_inner_node(new_children, depth)
        else:
            new_child = fn(hash)
            if cls._empty(new_child):
                return hash
            else:
                new_children = (hash,) * child_index + (new_child,) + (hash,) * (15 - child_index)
                return cls._create_inner_node(new_children, depth)

    @classmethod
    def _put_internal(cls, hash: bytes, encoded_path: bytes, value: bytes, depth: int):
        if depth == 64:
            return value
        fn = lambda h: cls._put_internal(h, encoded_path, value, depth + 1)
        return cls._update_node(hash, encoded_path, depth, fn)

    @classmethod
    def _remove_internal(cls, hash: bytes, encoded_path: bytes, depth: int):
        if cls._empty(hash):
            return hash
        if depth == 64:
            return bytes(32)
        fn = lambda h: cls._remove_internal(h, encoded_path, depth + 1)
        return cls._update_node(hash, encoded_path, depth, fn)

    @classmethod
    def _get_internal(cls, hash: bytes, encoded_path: bytes, depth: int):
        if cls._empty(hash):
            return None
        if depth == 64:
            return hash
        children = cls._children(hash, depth)
        child_index = cls._child_index(encoded_path, depth)
        child = children[child_index]
        return cls._get_internal(child, encoded_path, depth + 1)

    def put(self, encoded_path: bytes, value: bytes):
        cls = type(self)
        cls._check_is_hash(encoded_path)
        cls._check_is_hash(value)
        return cls(cls._put_internal(self.hash, encoded_path, value, 0))

    def remove(self, encoded_path: bytes):
        cls = type(self)
        cls._check_is_hash(encoded_path)
        new_hash = cls._remove_internal(self.hash, encoded_path, 0)
        return (cls(new_hash), new_hash != self.hash)

    def get(self, encoded_path: bytes) -> bytes:
        cls = type(self)
        cls._check_is_hash(encoded_path)
        return cls._get_internal(self.hash, encoded_path, 0)

    def contains(self, encoded_path: bytes) -> bool:
        return self.get(encoded_path) is not None

    @classmethod
    def _to_json_compatible(cls, hash: bytes, encoded_paths: List[bytes], depth: int, let_know: bool):
        if cls._empty(hash):
            return None
        val = {}
        if depth == 64:
            val["value"] = hexlify(hash).decode()
        else:
            val["hash"] = hexlify(hash).decode()
            if let_know:
                children = cls._children(hash, depth)
                recurse = lambda c, lk: cls._to_json_compatible(c, encoded_paths, depth + 1, lk)
                if encoded_paths:
                    let_know_children_indices = map(lambda p: cls._child_index(encoded_path, depth), encoded_paths)
                    let_know_children = [ i in let_know_children_indices for i in range(16) ]
                    val["children"] = [ recurse(c, lk) for c, lk in zip(children, let_know_children) ]
                else:
                    val["children"] = [ recurse(c, True) for c in children ]
        return val

    @classmethod
    def _from_json_compatible(cls, val, depth: int):
        if val == None:
            return bytes(32)
        if depth == 64:
            return unhexlify(val["value"])
        fn = lambda v: cls._from_json_compatible(v, depth + 1)
        children = tuple(map(fn, val["children"]))
        return cls._create_inner_node(children, depth)

    def to_json_compatible(self, encoded_paths: List[bytes]):
        """ Returns a JSON-serializable representation of this object. """
        return type(self)._to_json_compatible(self.hash, encoded_paths, 0, True)

    @classmethod
    def from_json_compatible(cls, val):
        """ Create a new MerkleTrie from its JSON-serializable representation. """
        return cls(cls._from_json_compatible(val, 0))
