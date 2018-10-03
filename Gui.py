import json
import os.path
from tkinter import *
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText

from src.gui_editor import SyntaxHiglighterMarm
from src.marm import *
from src.wallet_n import Wallet_New

# from docutils.utils import column_indices
# from src.wallet_n import *


# from src.chainbuilder import ChainBuilder
# from src.config import *
# from src.crypto import Key
# from src.mining import Miner
# from src.persistence import Persistence
# from src.protocol import Protocol
# from src.rpc_server import rpc_server
# from src.transaction import TransactionTarget
# import src.wallet as wallet
class Gui(object):

    __lblWidth = 25
    __btnWidth = 50
    __window = Tk()
    __balance = Label(__window, text="0.00", width=__btnWidth)
    __btnWalletId = Button(__window, text="Please select the path to your key.", width=__btnWidth)
    __listBtns = []
    
    _mining_pubkey: str = None
    _padx = 5
    _wallet = Wallet_New
    _minerRunning = FALSE
    _known_addresses = None

    def __init__(self):
        self.initializeGui()
        mainloop()
    
    def __enableButtons(self, enabled: bool):
        if enabled:
            for btn in self.__listBtns:
                btn.config(state=NORMAL)
        else:
            for btn in self.__listBtns:
                btn.config(state=DISABLED)
                
    def __selectPath(self, createNewAccount: bool=False):
        # ask for filename
        if createNewAccount:
            filename = filedialog.asksaveasfilename(parent=self.__window, title="Select location for key file", filetypes=[("key file", "*.wallet")])
        else:
            filename = filedialog.askopenfilename(parent=self.__window, title="Select your key", filetypes=[("key file", "*.wallet")])
            
        # Close opened wallet
        if self.__wallet is not None:
            self.__wallet.close()        
        # If no filename specified, report it to the user
        if filename == "":
            self.__btnWalletId.config(text="Please select the path to your key.")
            self.enableButtons(False)
            return
        
        # self.__wallet = Wallet_New(filename)
        self.__btnWalletId.config(text=filename)
        self.updateGui()
        self.enableButtons(True)
    
    def initializeGui(self):
        self.__window.title("Sarntaler Wallet")
        
        row = 0
        # label and dropdown for wallet
        lblWallet = Label(self.__window, text="Owner", width=self.__lblWidth)
        lblWallet.grid(row=0, column=0, padx=self.__padx)      
        self.__btnWalletId.config(command=self.selectPath)
        self.__btnWalletId.grid(row=row, column=1, pady=5, padx=self.__padx)
        row += 1
        btnNewWallet = Button(self.__window, text="Generate new account", command=lambda:self.selectPath(True))
        btnNewWallet.grid(row=row, column=1, padx=self.__padx)
        
        # balance components
        row += 1
        lblBalance = Label(self.__window, text="Balance:", width=self.__lblWidth)
        lblBalance.grid(row=row, column=0, padx=self.__padx)
        self.__balance.grid(row=row, column=1, padx=self.__padx)

        # Button for the creation of an Transaction
        row += 1
        btnCreateTransaction = Button(self.__window, text="new Transaction", width=self.__lblWidth, command=self.initPopup)
        btnCreateTransaction.grid(row=row, column=0, pady=10, padx=self.__padx)
        self.__listBtns.append(btnCreateTransaction)
        btnCreateContract = Button(self.__window, text="new Smart Contract", width=self.__lblWidth, command=self.initSmartContractView)
        btnCreateContract.grid(row=row, column=1, pady=10, padx=self.__padx)
        self.__listBtns.append(btnCreateContract)
        
        row += 1
        # update button
        btnUpdateGui = Button(self.__window, text="update", width=self.__lblWidth,
         command=lambda: self.updateGui())
        btnUpdateGui.grid(row=row, column=0, pady=10, padx=self.__padx)
        self.__listBtns.append(btnUpdateGui)
        # miner button
        btnStartMiner = Button(self.__window, text="start Miner (not supported yet)", width=self.__lblWidth)
        btnStartMiner.config(command=lambda: self.initMiner(btnStartMiner))
        btnStartMiner.grid(row=row, column=1, pady=10, padx=self.__padx)
        btnStartMiner.config(state=DISABLED)
        # self.__listBtns.append(btnStartMiner)
        
        # TODO self.enableButtons(False)
    
    def sendTransaction(self, popup, lblHint, my_key, target_key, strAmount, strFee):
        if not strAmount.isdigit():
            lblHint.config(text="Amount is no integer value")
            return
        if not strFee.isdigit():
            lblHint.config(text="Fee is no integer value")
            return
        
        amount = int(strAmount)  # use this variable to send (integer)
        fee = int(strFee)  # use this variable to send (integer)
        # TODO insert many target keys and amounts
        inputs = self._wallet.build_inputs([my_key, amount + fee])
        outputs = self._wallet.build_outputs([target_key, amount])
        self._wallet.build_transaction(inputs, outputs, fee, 0)
        '''  target_keys = Key.from_json_compatible(target_key)

        targets = [TransactionTarget(TransactionTarget.pay_to_pubkey(k), a) for k, a in
                   zip(target_keys, amounts)]
        print("Die Transaktion wurde gesendet")
        #TODO send information
        if self.__wallet is not None: 
            #TODO specify which private keys to use, does wallet.transfer return a string?
            message = self.__wallet.transfer(targets, fee, None, self.__wallet.get_keys(None))
        else:
            message = "You need to specify a wallet first!"
        #TODO output message to the user
        popup.destroy()
        '''
        
    def __saveContract(self, text):
        name = filedialog.asksaveasfile(mode='w', defaultextension=".marm", filetypes=[("Marm", "*.marm")])
        if(name is None):
            return
        name.write(text)
        name.close
     
    def __openContract(self, editor):
        name = filedialog.askopenfilename(filetypes=[("Marm", "*.marm")])
        if(name is ""):
            return
        file = open(name)
        editor.delete('1.0', END)
        editor.insert(END, file.read())
        
    def __sendSmartContract(self, code):
        errorhandler = marmcompiler.ErrorHandler()
        result = marmcompiler.marmcompiler("*editor*", code, errorhandler=errorhandler)
    
    def __checkSmartContract(self, code, console):
        errorhandler = marmcompiler.ErrorHandler()
        marmcompiler.marmcompiler("*editor*", code, errorhandler=errorhandler)

        console.config(state=NORMAL)
        console.delete('1.0', END)
        console.insert(END, errorhandler.tostring("red"))  # TODO
        console.config(state=DISABLED)
    
    def initSmartContractView(self):
        popup = Toplevel(self.__window)
        popup.title("New Smart Contract")
        popup.grab_set()
                
        editor = SyntaxHiglighterMarm(popup)
        editor.config(height=10)
        editor.pack(fill=BOTH, expand=YES, side=TOP)
        editor.bind("<Control-s>", lambda arg: self.__saveContract(editor.get(1.0, "end")))
        editor.bind("<Control-o>", lambda arg: self.__openContract(editor))
                
        menubar = Menu(popup)
        menubar.add_command(label="Save", command=lambda: self.saveContract(editor.get(1.0, "end")))
        menubar.add_command(label="Open", command=lambda: self.openContract(editor))
        popup.config(menu=menubar)
        
        console = ScrolledText(popup, height=5, state=DISABLED)
        console.pack(fill=BOTH, expand=NO, side=TOP)
        
        btnOk = Button(popup, text="Run", width=10, command=lambda: self.runSmartContract(editor.get("1.0", END), console))
        btnOk.pack(side=RIGHT)
        btnCancel = Button(popup, text="Check", width=10, command=lambda: self.checkSmartContract(editor.get("1.0", END)))
        btnCancel.pack(side=RIGHT)
        
    def initPopup(self):
        popup = Toplevel(self.__window)
        popup.title("New Transaction")
        popup.grab_set()
        
        lblSelectKey = Label(popup, text="Recipient", width=self.__btnWidth)
        lblSelectKey.grid(row=0, column=0, padx=self.__padx, pady=5)
        
        tkVarMyKey = StringVar(popup)
        choicesMyKey = self._wallet.keys.keys()
        tkVarMyKey.set(choicesMyKey[0])
        btnSelectKey = OptionMenu(popup, tkVarMyKey, *choicesMyKey)
        btnSelectKey.grid(row=0, column=1, padx=self._padx, pady=5, columnspan=2, sticky="ew")
        
        tkVar = StringVar(popup)
        choices = [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1 ]  # self.__known_addresses  # TODO replace choices with self._known_addresses
        # my address has to exist => length>1
        tkVar.set(choices[0])
        btnSelectKey = OptionMenu(popup, tkVar, *choices)
        btnSelectKey.grid(row=0, column=1, padx=self._padx, pady=5, columnspan=2, sticky="ew")
        
        lblAmount = Label(popup, text="Amount", width=self.__lblWidth)
        lblAmount.grid(row=1, column=0, padx=self._padx, pady=5)
        entAmount = Entry(popup, width=self._btnWidth)
        entAmount.grid(row=1, column=1, padx=self._padx, pady=5, columnspan=2)
        
        lblFee = Label(popup, text="Fee", width=self.__lblWidth)
        lblFee.grid(row=2, column=0, padx=self.__padx, pady=5)
        entFee = Entry(popup, width=self.__btnWidth)
        entFee.grid(row=2, column=1, padx=self.__padx, pady=5, columnspan=2)
        
        lblHint = Label(popup, text="", width=self.__lblWidth)
        lblHint.grid(row=3, column=0, padx=self.__padx, pady=5)
        
        btnOk = Button(popup, text="OK", width=10, command=lambda: self.sendTransaction(btnSelectKey, lblHint, self._wallet.keys[tkVarMyKey], tkVar.get(), entAmount.get(), entFee.get()))
        btnOk.grid(row=3, column=1, pady=5)
        btnCancel = Button(popup, text="Cancel", width=10, command=popup.destroy)
        btnCancel.grid(row=3, column=2, pady=5)
    
    def initMiner(self):
        popup2 = Toplevel(self.__window)
        popup2.title("Initialize Miner")
        popup2.grab_set()
        
        def selectPubkey():
            pubkey = filedialog.askopenfilename(parent=popup2, title="Select your public key", filetypes=[("public key file", "*.pem")])
            # print([s for s in pubkey], "\n")
            if pubkey != "":
                self.mining_pubkey = pubkey
                btnSelectPubkey.config(text=pubkey)
            else:
                btnSelectPubkey.config(text="Select your public key")
                # raise FileNotFoundError
                self.mining_pubkey = None
        
        btnSelectPubkey = Button(popup2, text="Select Pubkey for mining output", width=self.__lblWidth)
        btnSelectPubkey.config(command=selectPubkey)
        btnSelectPubkey.grid(row=1, column=1, pady=5, padx=self.__padx)

        entListenPort = Entry(popup2, width=self.__btnWidth)
        entListenPort.grid(row=2, column=1, pady=10, padx=self.__padx)
        entListenPort.insert(0, "listen-port")
        
        entListenAddress = Entry(popup2, width=self.__btnWidth)
        entListenAddress.grid(row=3, column=1, pady=10, padx=self.__padx)
        entListenAddress.insert(0, "listen-address")

        entBootstrapPeer = Entry(popup2, width=self.__btnWidth)
        entBootstrapPeer.grid(row=4, column=1, pady=5, padx=self.__padx)
        entBootstrapPeer.insert(0, "bootstrap-peer")

        entRpcPort = Entry(popup2, width=self.__btnWidth)
        entRpcPort.grid(row=5, column=1, pady=5, padx=self.__padx)
        entRpcPort.insert(0, "rpc-port")

        def selectPersistPath():
            persistPath = filedialog.askopenfilename(parent=popup2, title="Select Persist Path")
            if os.path.isfile(persistPath):
                btnPersistPath.config(text=persistPath)
            else:
                btnPersistPath.config(text="Select Persist Path")

        btnPersistPath = Button(popup2, text="Persist Path", width=self.__lblWidth)
        btnPersistPath.grid(row=6, column=1, pady=5, padx=self.__padx)
        btnPersistPath.config(command=selectPersistPath)

        btnStart = Button(popup2, text="Start", width=self.__btnWidth)
        btnStart.grid(row=7, column=0, pady=10, padx=self.__padx)
        
        def kwinput():
            output = dict()
            # if 
            return output

        btnStart.config(command=lambda : self.startMiner(self.mining_pubkey, **kwinput()))

        btnCancel = Button(popup2, text="Cancel", width=self.__btnWidth)
        btnCancel.grid(row=7, column=1, pady=10, padx=self.__padx)
        btnCancel.config(command=popup2.destroy)

    def startMiner(self, mining_pubkey, listen_address : str="", listen_port : int=0,
         bootstrap_peer=[], rpc_port : int=40203, persist_path : str=None):
        """
        if self.__minerRunning:
            #TODO: stop miner
            self.__minerRunning = FALSE
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
            self.__minerRunning = TRUE
            btn.config(text = "Stop Miner")
        """
        print("mining_pubkey:", mining_pubkey, ", listen-adress:", listen_address, ", listen-port:", listen_port,
        ", bootstrap-peer:", bootstrap_peer, ", rpc-port:", rpc_port, ", persist path:", persist_path, ".")
    
    def updateGui(self):
        _balance = 0  # TODO
        if self.__wallet is None:
            self.__known_addresses = None
        else:
            self.__known_addresses = list(json.loads(self.__wallet.get_addresses()))

     
Gui()
