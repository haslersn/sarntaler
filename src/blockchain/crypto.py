from hashlib import sha256
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

def compute_hash(to_hash: bytes) -> bytes:
    m = sha256()
    m.update(to_hash)
    return m.digest()

def is_hash(hash: bytes) -> bool:
    return len(hash) == 32 and hash != bytes(32) # mustn't be zero

def is_keypair(keypair: bytes) -> bool:
    try:
        RSA.importKey(keypair)
    except ValueError:
        return False
    return len(keypair) == 886 and keypair != bytes(886)

def is_pubkey(pubkey: bytes) -> bool:
    try:
        RSA.importKey(pubkey)
    except ValueError:
        return False
    return len(pubkey) == 271 and pubkey != bytes(271)

def check_is_hash(hash: bytes):
    if not is_hash(hash):
        raise ValueError('non-zero hash with length 32 Byte expected')

def check_is_keypair(keypair: bytes):
    if not is_keypair(keypair):
        raise ValueError('non-zero keypair with length 886 Byte expected')

def check_is_pubkey(pubkey: bytes):
    if not is_pubkey(pubkey):
        raise ValueError('non-zero pubkey with length 271 Byte expected')

def sign(keypair: bytes, hash: bytes) -> bytes:
    """ Sign a hashed value with the private key. """
    signer = PKCS1_PSS.new(RSA.importKey(keypair))
    h = SHA256.new()
    h.update(hashed_value)
    return signer.sign(h)

def verify_sign(pubkey: bytes, hash: bytes, signature: bytes):
    """ Verify a signature for an already hashed value and a public key. """
    signer = PKCS1_PSS.new(RSA.importKey(pubkey))
    h = SHA256.new()
    h.update(hashed_value)
    return singer.verify(h, signature)

def generate_keypair():
    """ Generate a new key pair. """
    return RSA.generate(1024).exportKey()

def pubkey_from_keypair(keypair: bytes):
    return RSA.importKey(keypair).publickey().exportKey()
