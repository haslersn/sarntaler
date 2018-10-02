from tkinter import *
from tkinter import filedialog
from tkinter import SEPARATOR

from src.config import *
from src.crypto import Key
from src.transaction import TransactionTarget
from src.protocol import Protocol
from src.blockchain import GENESIS_BLOCK
from src.chainbuilder import ChainBuilder
from src.mining import Miner
from src.persistence import Persistence
from src.rpc_server import rpc_server
import src.wallet as wallet

import json
import os.path

class Gui(object):
    _lblWidth = 25
    _btnWidth = 50
    _window = Tk()
    _balance = Label(_window, text="0.00", width=_btnWidth)
    _walletId = Button(_window, text="Please select the path to your key.", width=_btnWidth)
    mining_pubkey: str = None
    _padx = 5
    _wallet = None
    _minerRunning = FALSE
    _known_addresses = None


    def __init__(self):
        self.initializeGui()
        mainloop()
    
    def initializeGui(self):
        self._window.title("Sarntaler Wallet")
        
        lblWallet = Label(self._window, text="Owner", width=self._lblWidth)
        lblWallet.grid(row=0, column=0, padx=self._padx)
        
        def selectPath():
            #TODO update allowed file endings
            filename = filedialog.askopenfilename(parent=self._window, title="Select your key", filetypes=[("key file", "*.wallet")])
            
            if self._wallet is not None:
                self._wallet.close()
            if filename == "":
                self._walletId.config(text = "No wallet file specified!")
                return
            else:
                self._wallet = wallet.Wallet(filename)
            self._walletId.config(text=filename)
            
        self._walletId.config(command=selectPath)
        self._walletId.grid(row=0, column=1, pady=5, padx=self._padx)
        
        lblBalance = Label(self._window, text="Balance:", width=self._lblWidth)
        lblBalance.grid(row=1, column=0, padx=self._padx)
        
        self._balance.grid(row=1, column=1, padx=self._padx)

        def newTransaction():
            self.initPopup()
            
        btnCreateTransaction = Button(self._window, text="new Transaction", width=self._lblWidth,
         command=newTransaction)
        btnCreateTransaction.grid(row=3, column=0, pady=10, padx=self._padx)

        btnUpdateGui = Button(self._window, text="update", width=self._lblWidth,
         command = lambda: self.updateGui())
        btnUpdateGui.grid(row=4, column=0, pady=10, padx=self._padx)
        
        # all about miner:
        btnStartMiner = Button(self._window, text="start Miner", width=self._lblWidth)
        btnStartMiner.config(command=lambda: self.initMiner(btnStartMiner))
        btnStartMiner.grid(row=5, column=2, pady=10, padx=self._padx)
    
    def sendTransaction(self, popup, lblHint, target_key, strAmount, strFee):
        if not strAmount.isdigit():
            lblHint.config(text = "Amount is no integer value")
            return
        if not strFee.isdigit():
            lblHint.config(text = "Fee is no integer value")
            return
        amount = int(strAmount) #use this variable to send (integer)
        fee = int(strFee) #use this variable to send (integer)
        #TODO insert many target keys and amounts
        amounts = amount
        target_keys = Key.from_json_compatible(target_key)

        targets = [TransactionTarget(TransactionTarget.pay_to_pubkey(k), a) for k, a in
                   zip(target_keys, amounts)]
        print("Die Transaktion wurde gesendet")
        #TODO send information
        if self._wallet is not None: 
            #TODO specify which private keys to use, does wallet.transfer return a string?
            message = self._wallet.transfer(targets, fee, None, self._wallet.get_keys(None))
        else:
            message = "You need to specify a wallet first!"
        #TODO output message to the user
        popup.destroy()
     
    def initPopup(self):
        popup = Tk()
        popup.title("New Transaction")
        
        lblSelectKey = Label(popup, text="Recipient", width=self._btnWidth)
        lblSelectKey.grid(row=0, column=0, padx=self._padx, pady=5)
        
        tkVar = StringVar(popup)
        choices = self._known_addresses #TODO replace choices with self._known_addresses
        tkVar.set(choices[0])
        btnSelectKey = OptionMenu(popup, tkVar, *choices)
        btnSelectKey.grid(row=0, column=1, padx=self._padx, pady=5, columnspan=2, sticky = "ew")
        
        lblAmount = Label(popup, text="Amount", width=self._lblWidth)
        lblAmount.grid(row=1, column=0, padx=self._padx, pady=5)
        entAmount = Entry(popup, width=self._btnWidth)
        entAmount.grid(row=1, column=1, padx=self._padx, pady=5, columnspan=2)
        
        lblFee = Label(popup, text="Fee", width=self._lblWidth)
        lblFee.grid(row=2, column=0, padx=self._padx, pady=5)
        entFee = Entry(popup, width=self._btnWidth)
        entFee.grid(row=2, column=1, padx=self._padx, pady=5, columnspan=2)
        
        lblHint = Label(popup, text = "", width = self._lblWidth)
        lblHint.grid(row = 3, column = 0, padx = self._padx, pady=5)
        
        btnOk = Button(popup, text="OK", width=10,
         command=lambda: self.sendTransaction(btnSelectKey, lblHint, tkVar.get(), entAmount.get(), entFee.get()))
        btnOk.grid(row=3, column=1, pady=5)
        btnCancel = Button(popup, text="Cancel", width=10, command=popup.destroy)
        btnCancel.grid(row=3, column=2, pady=5)
    
    def initMiner(self, btn):
        popup2 = Tk()
        popup2.title("Initialize Miner")
        
        def selectPubkey():
            pubkey = filedialog.askopenfilename(parent=popup2, title="Select your public key", filetypes=[("public key file", "*.pem")])
            #print([s for s in pubkey], "\n")
            if pubkey != "":
                self.mining_pubkey = pubkey
                btnSelectPubkey.config(text = pubkey)
            else:
                btnSelectPubkey.config(text = "Select your public key")
                #raise FileNotFoundError
                self.mining_pubkey = None
        
        
        btnSelectPubkey = Button(popup2, text = "Select Pubkey for mining output", width = self._lblWidth)
        btnSelectPubkey.config(command=selectPubkey)
        btnSelectPubkey.grid(row=1, column=1, pady=5, padx=self._padx)

        entListenPort = Entry(popup2, width = self._btnWidth)
        entListenPort.grid(row = 2, column = 1, pady = 10, padx = self._padx)
        entListenPort.insert(0, "listen-port")
        
        entListenAddress = Entry(popup2, width = self._btnWidth)
        entListenAddress.grid(row = 3, column = 1, pady = 10, padx = self._padx)
        entListenAddress.insert(0, "listen-address")

        entBootstrapPeer = Entry(popup2, width = self._btnWidth)
        entBootstrapPeer.grid(row = 4, column = 1, pady = 5, padx = self._padx)
        entBootstrapPeer.insert(0, "bootstrap-peer")

        entRpcPort = Entry(popup2, width = self._btnWidth)
        entRpcPort.grid(row = 5, column = 1, pady = 5, padx = self._padx)
        entRpcPort.insert(0, "rpc-port")

        def selectPersistPath():
            persistPath = filedialog.askopenfilename(parent = popup2, title = "Select Persist Path")
            if os.path.isfile(persistPath):
                btnPersistPath.config(text = persistPath)
            else:
                btnPersistPath.config(text = "Select Persist Path")

        btnPersistPath = Button(popup2, text = "Persist Path", width = self._lblWidth)
        btnPersistPath.grid(row = 6, column = 1, pady = 5, padx = self._padx)
        btnPersistPath.config(command = selectPersistPath)

        btnStart = Button(popup2, text = "Start", width = self._btnWidth)
        btnStart.grid(row = 7, column = 0, pady = 10, padx = self._padx)
        
        def kwinput():
            output = dict()
            #if 
            return output
        btnStart.config(command=lambda : self.startMiner(self.mining_pubkey, kwinput()))

        btnCancel = Button(popup2, text = "Cancel", width = self._btnWidth)
        btnCancel.grid(row= 7, column = 1, pady = 10, padx = self._padx)
        btnCancel.config(command = popup2.destroy)





    def startMiner(self, btn, mining_pubkey, listen_address : str = "", listen_port : int = 0,
         bootstrap_peer = [], rpc_port : int = 40203, persist_path : str = None):
        """
        if self._minerRunning:
            #TODO: stop miner
            self._minerRunning = FALSE
            btn.config(text = "Run Miner")
        else:
            #TODO: start miner
            proto = Protocol(bootstrap_peer, GENESIS_BLOCK, listen_port, listen_address)
            if mining_pubkey is not None:
                pubkey = Key(mining_pubkey.read())
                mining_pubkey.close()
                miner = Miner(proto, pubkey)
                miner.start_mining()
                chainbuilder = miner.chainbuilder
            else:
                chainbuilder = ChainBuilder(proto)
            
            if persist_path:
                persist = Persistence(persist_path, chainbuilder)
                try:
                    persist.load()
                except FileNotFoundError:
                    pass
            else:
                persist = None
            
            rpc_server(rpc_port, chainbuilder, persist)
            self._minerRunning = TRUE
            btn.config(text = "Stop Miner")
        """
        print("mining_pubkey:", mining_pubkey, ", listen-adress:", listen_address, ", listen-port:", listen_port, 
        ", bootstrap-peer:", bootstrap_peer, ", rpc-port:", rpc_port, ", persist path:", persist_path, ".")
    
    def updateGui(self):
        _balance = 0 #TODO
        if self._wallet is not None:
            self._known_addresses = list(json.loads(self._wallet.get_addresses()))
        else:
            self._known_addresses = None
     
Gui()
