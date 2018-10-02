from src.wallet import Wallet
from src.wallet_hierarchical import WalletHierarchical
from src.wallet_old import WalletOld


def init_Wallet(wallet_path: str, ip_address="localhost", miner_port=40203) -> Wallet:
    """
    A factory for the two wallet types.
    :param wallet_path: path to the wallet file. Ending: .wallet -> old Wallet
                                                         .hwallet -> hierarchical Wallet
    :param ip_address: address for the rpc_client
    :param miner_port: port for the rpc_client
    :return: The Wallet on this path. If there is no File, a new hierarchical Wallet is instantiated
    """
    if wallet_path.endswith(".wallet"):
        return WalletOld(wallet_path, ip_address, miner_port)
    if wallet_path.endswith(".hwallet"):
        return WalletHierarchical(wallet_path, ip_address, miner_port)