from collections import namedtuple
from hashlib import sha256
from typing import *

class Crypto:
    @staticmethod
    def compute_hash(to_hash: bytes) -> bytes:
        m = sha256()
        m.update(to_hash)
        return m.digest()

    @staticmethod
    def is_hash(hash: bytes) -> int:
        return len(hash) == 32 and hash != bytes(32) # mustn't be zero

class MerkleTrie(namedtuple("MerkleTrie", ["children", "hash"])):
    def __new__(cls, children = None, hash = bytes(32)):
        return super().__new__(cls, children, hash)

    @property
    def empty(self):
        return self.hash == bytes(32)

    @property
    def known(self):
        return self.empty or self.children is not None

    @classmethod
    def _create_unknown(cls, hash: bytes):
        cls._check_is_hash(hash)
        return cls.__new__(cls, None, hash)

    @classmethod
    def _create_with_children(cls, children):
        if type(children) != tuple or len(children) != 16 or not all(type(c) == MerkleTrie for c in children):
            raise ValueError('Illegal type of children')
        to_hash = bytes()
        for child in children:
            to_hash += child.hash
        assert(len(to_hash) == 32 * 16)
        hash = Crypto.compute_hash(to_hash)
        return cls.__new__(cls, children, hash)

    @staticmethod
    def _check_is_hash(str: bytes):
        if not Crypto.is_hash(str):
            raise ValueError('non-zero hash with length 32 Byte expected')

    def _check_known(self):
        if not self.known:
            raise ValueError('node was required to store its children')

    @staticmethod
    def _child_index(encoded_path: bytes, deepness: int):
        child_index = encoded_path[deepness // 2]
        if deepness % 2 == 0:
            child_index //= 16
        else:
            child_index %= 16
        return child_index

    def _put_internal(self, encoded_path: bytes, value: bytes, deepness: int):
        if deepness == 64:
            assert self.children is None
            return type(self)._create_unknown(value)
        self._check_known()
        child_index = type(self)._child_index(encoded_path, deepness)
        old_children = (MerkleTrie(),) * 16 if self.empty else self.children
        old_child = old_children[child_index]
        new_child = old_child._put_internal(encoded_path, value, deepness + 1)
        new_children = old_children[:child_index] + (new_child,) + old_children[child_index+1:]
        return type(self)._create_with_children(new_children)

    def _remove_internal(self, encoded_path: bytes, deepness: int):
        if self.empty:
            return (self, False)
        if deepness == 64:
            assert self.children is None
            return (MerkleTrie(), True)
        self._check_known()
        child_index = type(self)._child_index(encoded_path, deepness)
        old_children = self.children
        old_child = old_children[child_index]
        new_child, did_remove = old_child._remove_internal(encoded_path, deepness + 1)
        if not did_remove:
            return (self, False)
        new_children = old_children[:child_index] + (new_child,) + old_children[child_index+1:]
        if new_children == (None,) * 16:
            return (MerkleTrie(), True)
        return (type(self)._create_with_children(new_children), True)

    def _get_internal(self, encoded_path: bytes, deepness: int):
        if self.empty:
            return None
        if deepness == 64:
            assert self.children is None
            return self.hash
        self._check_known()
        child_index = type(self)._child_index(encoded_path, deepness)
        child = self.children[child_index]
        return child._get_internal(encoded_path, deepness + 1)

    def _cherry_pick_internal(self, encoded_path, deepness: int):
        if self.empty:
            return MerkleTrie()
        if deepness == 64:
            assert self.children is None
            return self
        self._check_known()
        child_index = type(self)._child_index(encoded_path, deepness)
        old_children = self.children
        old_child = old_children[child_index]
        new_child = old_child._cherry_pick_internal(encoded_path, deepness + 1)
        fn = lambda c: c if c.empty else type(self)._create_unknown(c.hash)
        new_children = tuple(map(fn, old_children[:child_index])) + (new_child,) + tuple(map(fn, old_children[child_index+1:]))
        return type(self)._create_with_children(new_children)

    @staticmethod
    def _merge_internal(first, second, deepness: int):
        assert first.hash == second.hash
        if deepness == 64:
            assert first.children is None
            assert second.children is None
            return first
        if second.children is None:
            return first
        if first.children is None:
            return second
        fn = lambda f, s: type(first)._merge_internal(f, s, deepness + 1)
        new_children = tuple([ fn(f, s) for (f, s) in zip(first.children, second.children) ])
        return type(first)._create_with_children(new_children)

    def put(self, encoded_path: bytes, value: bytes) :
        type(self)._check_is_hash(encoded_path)
        type(self)._check_is_hash(value)
        return self._put_internal(encoded_path, value, 0)

    def remove(self, encoded_path: bytes):
        type(self)._check_is_hash(encoded_path)
        return self._remove_internal(encoded_path, 0)

    def get(self, encoded_path: bytes) -> bytes:
        type(self)._check_is_hash(encoded_path)
        return self._get_internal(encoded_path, 0)

    def contains(self, encoded_path: bytes) -> bool:
        return self.get(encoded_path) is not None

    @staticmethod
    def merge(first, second):
        return type(first)._merge_internal(first, second, 0)

    def cherry_pick(self, encoded_paths: List[bytes]):
        result = type(self)._create_unknown(self.hash)
        for path in encoded_paths:
            additional = self._cherry_pick_internal(path, 0)
            result = type(self).merge(result, additional)
        return result
