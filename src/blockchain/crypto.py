from hashlib import sha256

def compute_hash(to_hash: bytes) -> bytes:
    m = sha256()
    m.update(to_hash)
    return m.digest()

def is_hash(hash: bytes) -> bool:
    return len(hash) == 32 and hash != bytes(32) # mustn't be zero

def check_is_hash(hash: bytes):
    if not is_hash(hash):
        raise ValueError('non-zero hash with length 32 Byte expected')
