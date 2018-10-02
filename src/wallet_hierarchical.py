"""
This wallet is an hierarchical wallet for the labchain.
It offers the possibility to recover lost private keys of the wallet with one master key.

"""
from struct import pack
from typing import Tuple, List

from Crypto.Hash import HMAC
from Crypto.PublicKey import RSA

from src.crypto import Key
from src.rpc_client import RPCClient
from .wallet import Wallet

__all__ = ['WalletHierarchical']


class WalletHierarchical(Wallet):

    # random number generator (for the new keys)

    def __init__(self, wallet_path: str, ip_address="localhost", miner_port=40203):
        super().__init__(wallet_path, ip_address, miner_port)
        self._key_generation: RandomKeys = None  # just declaration instantiated in init_key_generation
        self.init_key_generation()

    def init_key_generation(self):
        if self._key_generation is None:
            keys = self.wallet_keys()
            if not keys:
                self._key_generation = RandomKeys(keys)
            else:
                self._key_generation = RandomKeys()
                Key.write_many_private(self._wallet_path, [self._key_generation.get_master_key()])

    def read_wallet(self, path: str) -> Tuple[List[Key], str]:
        (keys, path) = self.read_wallet_private(path)
        # checking if the keys were generated correctly
        # for this to work correct, the keys read from the file should be always read and wrote in the same order
        if RandomKeys.check_keys(keys):
            return keys, path
        raise RandomKeys.InvalidKeyFile()

    def generate_next_key(self) -> Key:
        self.init_key_generation()
        return self._key_generation.next_key()

    def write_master_key(self, backup_path: str):
        """writes the master key to a backup file. From this file the wallet can be recreated with the recover method"""
        self.init_key_generation()
        Key.write_many_private(backup_path, [self._key_generation.get_master_key()])

    @classmethod
    def recover(cls, master_path: str, recover_path: str, rpc_ip: str = "localhost", rpc_port: int = 40203):
        """
        recovers all private Keys from the master key, no wallet instance is created,
        to do this the recovered file must be read
        :param master_path: path to a file with the master key
        :param recover_path: path for the recovered wallet file
        :param rpc_ip: ip address for the rpc connection to the blockchain
        :param rpc_port: port for the rpc connection
        :return: --
        """
        # get the master key
        master_key = None
        with open(master_path, "rb") as f:
            contents = f.read()
        for m in Key.read_many_private(contents):
            master_key = m
            break

        if not master_key:
            raise Exception("No Key in the specified file: {}".format(master_path))

        # generating lost keys
        keys = [master_key]
        key_generator = RandomKeys(None, master_key)

        # generate so many keys until a key is found, which isn't used in the blockchain
        rpc = RPCClient(rpc_ip, rpc_port)
        addresses = rpc.get_addresses()  # addresses may be very big maybe searching for transcations is faster
        next_key = master_key

        while next_key in addresses:
            keys += next_key
            next_key = key_generator.next_key()

        # all keys were found, write them to the recover file
        Key.write_many_private(recover_path, keys)


class RandomKeys:
    """
    everything with the key generation, checking the keys and generating new Keys
    """

    class PRNG(object):
        """
        PRNG: Pseudo Random Number Generator
        The random function to generate a new Key
        #source: https://stackoverflow.com/questions/18264314/generating-a-public-private-key-pair-using-an-initial-key
        """

        def __init__(self, seed):
            self.index = 0
            if not seed:
                raise Exception("no seed specified")
            self.seed = seed
            self.buffer = b""

        def __call__(self, n):
            while len(self.buffer) < n:
                self.buffer += HMAC.new(self.seed +
                                        pack("<I", self.index)).digest()
                self.index += 1
            result, self.buffer = self.buffer[:n], self.buffer[n:]
            return result

    def __init__(self, keys: List[Key] = None, master_key: Key = None):
        """
        init the random number generator with a base key or a list of keys
        the first key in the list is used as master key
        """
        # derive the master key as seed for the random number generator
        if not keys and not master_key:
            self._master_key = Key.generate_private_key()
        elif not master_key:
            self._master_key = keys[0]
        else:
            if master_key != keys[0]:
                raise Exception("master key is not first in the list")
            self._master_key = keys[0]

        if not self._master_key.has_private:
            raise Exception("master key is not private")
        self._prng = RandomKeys.PRNG(self._master_key)
        if not keys:
            return

        # check if the list has correct generated keys
        # with this check the prng is updated, such that the next generated key will be a new key
        for k in keys[1:]:
            if k != self.next_key():
                raise RandomKeys.InvalidKeyFile

    @classmethod
    def check_keys(cls, keys: List[Key]) -> bool:
        if not keys:
            return True
        prng = RandomKeys.PRNG(keys[0])
        for k in keys[1:]:
            if k != RandomKeys.next_key_prng(prng):
                return False
        return True

    @classmethod
    def next_key_prng(cls, prng: PRNG) -> Key:
        """generates a ney private key from the random number generator"""
        # TODO check whether this is always a new key, because my Crypto package is not working
        return Key(RSA.generate(1024, prng).exportKey())

    def next_key(self) -> Key:
        return RandomKeys.next_key_prng(self._prng)

    def get_master_key(self):
        return self._master_key

    class InvalidKeyFile(Exception):
        """
        Exception thrown, if the Keys in a Wallet aren't consistent
        """

        def __init__(self, msg: str = ""):
            super().__init__(msg)
