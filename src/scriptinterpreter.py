#! /usr/bin/env/python3
import hashlib
import logging
import random
from collections import namedtuple
from binascii import hexlify, unhexlify
from datetime import datetime
from Crypto.PublicKey import RSA
from typing import List

from src.blockchain.account import Account, StorageItem
from src.blockchain.crypto import *
from src.blockchain.merkle_trie import MerkleTrie
from src.blockchain.new_transaction import TransactionInput, TransactionOutput, TransactionData, Transaction
from src.blockchain.state_transition import transit
import src.crypto as cr


# TODO: Put the following two classes into crypt.py

class Hash(namedtuple('Hash', [ 'value' ])):
    def __init__(self, value):
        check_is_hash(value)

class Signature(namedtuple('Signature', [ 'value' ])):
    def __init__(self, value):
        check_is_signature(value)

class Pubkey(namedtuple('Pubkey', [ 'value' ])):
    def __init__(self, value):
        check_is_pubkey(value)

class Keypair(namedtuple('Keypair', [ 'value' ])):
    def __init__(self, value):
        check_is_keypair(value)


class ScriptInterpreter:
    """
    ScriptInterpreter is a simple imperative stack-based script language. This class
    implements a script as a List of commands to be executed from left to
    right. The items in the list of commands can be any data or an operation.

    USAGE:
    The constructor is called using a string that represents the script.
    This string is a long chain consisting of commands, which are arbitrary
    substrings, each separated by a whitespace. If a command substring matches
    an opcode string, as specified in the OPLIST below, the interpreter will
    parse opcode into an operation and execute its behavior. Any other command
    will be simply pushed onto the stack as data.
    """

    """
    Following is an overview  of all implemented operations sorted after area
    of application.
    For more information go to https://en.bitcoin.it/wiki/Script
    or read the explanation within the op-implementation below:
    """

    types = [ list, int, str, Hash, Signature, Pubkey, Keypair ]

    operations = {
        'OP_SHA256',
        'OP_PUBKEYFROMKEYPAIR',
        'OP_VERIFYSIGN',
        'OP_KILL',
        'OP_CHECKLOCKTIME',

        'OP_SWAP',
        'OP_SWAPANY',
        'OP_DUP',

        'OP_PUSHABS',
        'OP_POPABS',
        'OP_PUSHR',
        'OP_POPR',
        'OP_PUSHFP',
        'OP_POPFP',
        'OP_INCFP',
        'OP_PUSHSP',
        'OP_POPSP',
        'OP_PUSHPC',
        'OP_POPVOID',
        'OP_PUSHR',

        'OP_JUMP',
        'OP_JUMPR',
        'OP_JUMPC',
        'OP_JUMPRC',

        'OP_CALL',
        'OP_RET',

        'OP_ADD',
        'OP_SUB',
        'OP_MUL',
        'OP_DIV',
        'OP_MOD',
        'OP_AND',
        'OP_OR',
        'OP_XOR',
        'OP_NOT',
        'OP_NEG',
        'OP_EQU',
        'OP_LE',
        'OP_GE',
        'OP_LT',
        'OP_GT',

        'OP_GETBAL',
        'OP_GETOWNBAL',
        'OP_SETSTOR',
        'OP_GETSTOR',
        'OP_TRANSFER',

        'OP_PACK',
        'OP_UNPACK',

        'OP_CREATECONTR',
        'OP_HASH',
        'OP_GENPUBKEY',
        'OP_GETCODE'
    }


    def __init__(self, state: MerkleTrie, params_script: str, calleeAcc: Account, inaddresses : List[bytes], amount : int):
        self.state = state
        self.params_script = params_script
        self.acc = calleeAcc
        self.inaddresses = inaddresses
        self.amountspent = amount

    def to_string(self):
        return " ".join(self.stack)


    # operation implementations

    def __pop_checked(self, t: type):
        assert t in [ str, int, list, Hash, Signature, Pubkey, Keypair]
        if not self.stack:
            logging.warning("Stack is empty. Expected {}".format(t.__name__))
            return None
        top = self.stack.pop()
        if type(top) is not t:
            logging.warning("Wrong type on top of stack. Expected {} but found {}".format(
                t.__name__, type(top).__name__))
            return None
        return top

    def op_sha256(self):
        #The input is hashed using SHA-256.
        param = self.__pop_checked(str)
        if param is None:
            logging.warning("OP_SHA256: Stack is empty or top element not a string")
            return False
        sha256 = hashlib.sha256()
        sha256.update(param)
        self.stack.append(Hash(sha256.digest()))
        return True

    def op_pubkeyfromkeypair(self):
        """Pushes a public key obtained from a key pair (1. argument)."""
        keypair = self.__pop_checked(Keypair)
        if keypair is None:
            logging.warning("OP_CHECKKEY: Stack is empty or top element not a key")
            return False
        self.stack.append(Pubkey(pubkey_from_keypair(keypair.value)))
        return True

    def op_verifysign(self):
        # The signature used by OP_CHECKSIG must be a valid signature for
        # this hash and public key.
        #If it is, 1 is returned, 0 otherwise.
        pubkey = self.__pop_checked(Pubkey)
        if pubkey is None:
            logging.warning("OP_VERIFYSIGN: Stack is empty or top element not a key")
            return False
        hash = self.__pop_checked(Hash)
        if hash is None:
            logging.warning("OP_VERIFYSIGN: Stack is empty or top element not a hash")
            return False
        sig = self.__pop_checked(Signature)
        if sig is None:
            logging.warning("OP_VERIFYSIGN: Stack is empty or top element not a signature")
            return False
        result = 1 if verify_sign(pubkey,hash, sig) else 0
        return True

    def op_kill(self):

        """Marks transaction as invalid.
        A standard way of attaching extra data to transactions is to add a zero-value output with a
        scriptPubKey consisting of OP_KILL followed by exactly one pushdata op. Such outputs are
        provably unspendable, reducing their cost to the network.
        Currently it is usually considered non-standard (though valid) for a transaction to have more
        than one OP_KILL output or an OP_KILL output with more than one pushdata op. """

        #DONE
        logging.warning('OP_KILL was executed!')
        return False

    # TODO: update to the current parser version
    # def op_checklocktime(self):

    #     #Error Indicator
    #     error = 0

    #     #Error if Stack is empty
    #     if not self.stack or len(self.stack) < 2:
    #         error = 1

    #     #if top stack item is greater than the transactions nLockTime field ERROR
    #     temp = float(self.stack.pop())
    #     try:
    #         timestamp = datetime.fromtimestamp(temp)
    #     except TypeError:
    #         logging.error("A timestamp needs to be supplied after the OP_CHECKLOCKTIME operation!")
    #         self.stack.append(str(0))
    #         return False

    #     #TODO we need to make sure that the timezones are being taken care of
    #     if(timestamp > datetime.utcnow()):
    #         print("You need to wait at least " + str(timestamp - datetime.utcnow()) + " to spend this Tx")
    #         error = 3

    #     if(error):
    #         #errno = 1 Stack is empty
    #         if(error == 1):
    #             logging.warning('Stack is empty!')
    #             self.stack.append(str(0))
    #             return False

    #         #errno = 2 Top-Stack-Value < 0
    #         if(error == 2):
    #             logging.warning('Top-Stack-Value < 0')
    #             self.stack.append(str(0))
    #             return False

    #         #errno = 3 top stack item is greater than the transactions
    #         if(error == 3):
    #             #logging.warning('you need to wait more to unlock the funds!')
    #             self.stack.append(str(0))
    #             return False

    #     return True

    def op_dup(self):
        if not self.stack:
            logging.warning("OP_DUP: Stack is empty")
            return False
        self.stack.append(self.stack[-1])
        return True

    def op_swap(self):
        if (len(self.stack) < 2):
            logging.warning("OP_SWAP: Not enough arguments")
            return False

        old_first = self.stack.pop()
        old_second = self.stack.pop()

        self.stack.append(old_first)
        self.stack.append(old_second)
        return True
    
    def op_swapany(self):
        i = self.__pop_checked(int)
        if i is None or i < 0 or len(self.stack) < i + 1:
            logging.warning("OP_SWAPANY: Invalid argument or not enough stack items")
        sp = len(self.stack) - 1
        temp = self.stack[sp] # second element from top is at top after __pop_checked()!!
        self.stack[sp] = self.stack[sp - i]
        self.stack[sp - i] = temp
        return True

    def op_pushabs(self):
        index = self.__pop_checked(int)
        if index is None:
            logging.warning("OP_PUSHABS: Stack is empty or top element not an int")
            return False
        if index < 0 or index >= len(self.stack):
            logging.warning("OP_PUSHABS: Argument is not an index in the stack")
            return False
        self.stack.append(self.stack[index])
        return True

    def op_popabs(self):
        index = self.__pop_checked(int)
        if index is None:
            logging.warning("OP_POPABS: Stack is empty or top element not an int")
            return False
        if index < 0 or index >= len(self.stack):
            logging.warning("OP_POPABS: Argument is not an index in the stack")
            return False

        elem = self.stack.pop()
        if elem is None:
            logging.warning("OP_POPABS: Stack has only one element")
            return False

        self.stack[index] = elem
        return True

    def op_pushpc(self):
        self.stack.append(self.pc)
        return True

    def op_pushfp(self):
        self.stack.append(self.framepointer)
        return True

    def op_popfp(self):
        popped = self.__pop_checked(int)
        if popped is None:
            logging.warning("OP_POPFP: Stack is empty or top element not an int")
            return False
        self.framepointer = popped
        return True

    def op_pushsp(self):
        self.stack.append(len(self.stack) - 1)
        return True

    def op_popsp(self):
        if not self.stack:
            logging.warning("OP_POPSP: Stack is empty")
            return False

        index = self.stack.pop()
        del self.stack[(index+1):]
        return True

    def op_popvoid(self):
        if not self.stack:
            logging.warning("OP_POPVOID: Stack is empty")
            return False

        self.stack.pop()
        return True

    def op_jump(self):
        if not self.stack:
            logging.warning("OP_JUMP: Stack is empty")
            return False

        index = self.stack.pop()
        if index < 1 or index > len(self.program):
            logging.warning("OP_JUMP: Argument is not an index in the program")
            return False
        self.pc = index
        return True

    def op_jumpr(self):
        if not self.stack:
            logging.warning("OP_JUMPR: Stack is empty")
            return False

        index = self.stack.pop()
        new_index = self.pc + index - 1
        if new_index-1 < 1 or new_index-1 > len(self.program):
            logging.warning("OP_JUMPR: New program counter does not point in the program "+str(new_index))
            return False
        self.pc = new_index
        return True

    def op_jumpc(self):
        if(len(self.stack) < 2):
            logging.warning("OP_JUMPC: Not enough arguments")
            return False

        index = self.stack.pop()
        cond = self.stack.pop()
        if cond == 1:
            if index < 1 or index > len(self.program):
                logging.warning("OP_JUMPC: New program counter does not point in the program")
                return False
            self.pc = index
        return True

    def op_jumprc(self):
        if(len(self.stack) < 2):
            logging.warning("OP_JUMPRC: Not enough arguments")
            return False

        index = self.stack.pop()
        cond = self.stack.pop()
        if cond == 1:
            new_index = self.pc + index -1
            if new_index-1 < 1 or new_index-1 > len(self.program):
                logging.warning("OP_JUMPRC: New program counter does not point in the program")
                return False
            self.pc = new_index
        return True


    def op_add(self):
        return self.math_operations(lambda first, second: second + first)

    def op_sub(self):
        return self.math_operations(lambda first, second: second - first)

    def op_mul(self):
        return self.math_operations(lambda first, second: second * first)

    def op_div(self):
        return self.math_operations(lambda first, second: second // first)

    def op_neg(self):
        param = self.__pop_checked(int)
        if param is None:
            logging.warning("OP_NEG: Stack is empty or top element not an integer")
            return False

        self.stack.append(-param)
        return True

    def op_mod(self):
        return self.math_operations(lambda first, second: second % first)

    def op_and(self):
        return self.math_operations(lambda first, second: second & first)

    def op_or(self):
        return self.math_operations(lambda first, second: second | first)

    def op_xor(self):
        return self.math_operations(lambda first, second: second ^ first)

    def op_not(self):
        param = self.__pop_checked(int)
        if param is None:
            logging.warning("OP_NOT: Stack is empty or top element not an integer")
            return False

        if (param != 0 and param != 1):
            logging.warning("OP_NOT: Top element not a bool (i.e. not 0 or 1)")
            return False

        self.stack.append(1 - param)
        return True

    def op_equ(self):
        if (len(self.stack) < 2):
            logging.warning("Not enough arguments")
            return False

        old_first = self.stack.pop()
        old_second = self.stack.pop()

        result = 1 if old_first == old_second else 0
        self.stack.append(result)
        return True

    def op_le(self):
        return self.math_operations(lambda first, second: 1 if second <= first else 0)

    def op_ge(self):
        return self.math_operations(lambda first, second: 1 if second >= first else 0)

    def op_lt(self):
        return self.math_operations(lambda first, second: 1 if second < first else 0)

    def op_gt(self):
        return self.math_operations(lambda first, second: 1 if second > first else 0)

    def op_pushr(self):
        return self.op_pushfp() and self.op_add() and self.op_pushabs()

    def op_popr(self):
        return self.op_pushfp() and self.op_add() and self.op_popabs()

    def op_incfp(self):
        return self.op_pushfp() and self.op_add() and self.op_popfp()

    def op_call(self):
        if not self.stack:
            logging.warning("OP_CALL: Stack is empty")
            return False

        proc_addr = self.__pop_checked(int)  # get procedure address from the top of the stack
        if proc_addr < 1 or proc_addr > len(self.program):
            logging.warning("OP_CALL: Argument is not an index in the program")
            return False

        self.stack.append(self.framepointer)        # store the old frame pointer
        self.framepointer = len(self.stack) - 1     # set the new frame pointer
        self.stack.append(self.pc)                  # store the return address
        self.pc = proc_addr                         # prepare for execution of the procedure
        return True

    def op_ret(self):
        if not self.stack:
            logging.warning("OP_RET: Stack is empty")
            return False

        result = self.stack.pop()
        if self.stack[self.framepointer] == -1:
            logging.warning("OP_RET: Last Return, gonna exit program " + str(result))
            self.retval = result
            return False
        self.pc = self.stack[self.framepointer + 1] # restore the program counter
        del self.stack[(self.framepointer+1):]          # reset the stack pointer
        self.framepointer = self.stack.pop()        # restore the framepointer
        self.stack.append(result)
        return True

    def op_getbal(self):
        address = self.__pop_checked(Hash)
        if address is None:
            logging.warning("OP_GETBAL: Stack is empty")
            return False
        acc_to_get_bal_from = Account.get_from_hash(self.state.get(address.value))
        if acc_to_get_bal_from is None:
            self.stack.append(-1)
        else:
            self.stack.append(acc_to_get_bal_from.balance)
        return True

    def op_getownbal(self):
        self.stack.append(self.acc.balance)
        return True


    def op_getstor(self):
        if not self.stack:
            logging.warning("OP_GETSTOR: Stack is empty")
            return False
        var_name = self.__pop_checked(str)
        if var_name is None:
            logging.warning("OP_GETSTOR: s_1 not existing or wrong type")
            return False
        var_value = self.acc.get_storage(var_name)
        if None == var_value:
            return False
        self.stack.append(var_value)
        return True

    def op_setstor(self):
        if len(self.stack) < 2:
            logging.warning("OP_SETSTOR: Not enough arguments")
            return False
        var_name = self.__pop_checked(str)
        if var_name is None:
            logging.warning("OP_SETSTOR: s_1 not existing or wrong type")
            return False
        var_value = self.stack.pop()
        new_acc = self.acc.set_storage(var_name, var_value)
        if new_acc is None:
            logging.warning("OP_SETSTOR: Could not set storage for " + var_name)
            return False
        self.acc = new_acc
        self.state = self.state.put(self.acc.address, self.acc.hash)
        return True

    def op_createcontr(self):
        if len(self.stack) < 5:
            logging.warning("OP_CREATECONTR: Not enough arguments")
            return False
        pub_key = self.__pop_checked(Pubkey)
        code = self.__pop_checked(str)
        owner_access_flag = self.__pop_checked(int)
        storage_var_names = self.__pop_checked(list)
        storage_initial_values = self.__pop_checked(list)
        if any(v is None for v in [pub_key, code, owner_access_flag, storage_var_names, storage_initial_values]):
            logging.warning("OP_CREATECONTR: error parsing arguments")
            return False
        if len(storage_var_names) != len(storage_initial_values):
            logging.warning("OP_CREATECONTR: storage lists are not of equal length")
            return False
        storage = list()
        for name, initval in zip(storage_var_names, storage_initial_values):
            typ = type(initval).__name__
            if type(initval) in [Hash, Signature, Pubkey, Keypair]:
                initval = initval.value
            item = StorageItem(name, typ, initval)
            if item is None:
                logging.warning("OP_CREATECONTR: error parsing storage lists")
                return False
            storage.append(item)

        if self.state.contains(compute_hash(pub_key.value)):
            logging.warning("OP_CREATECONTR: Address already exists")
            self.stack.append(0)
            return True
        new_acc = Account(pub_key.value, 0, code, owner_access_flag, storage)
        self.state = self.state.put(new_acc.address, new_acc.hash)
        self.stack.append(1)
        return True


    def op_pack(self):
        n = self.__pop_checked(int)
        if n is None:
            logging.warning("OP_PACK: s_1 not existing or wrong type")
            return False
        packed_str = ""
        if len(self.stack) < n:
            logging.warning("OP_PACK: not enough stack elements")
            return False
        to_push = list(reversed([ self.stack.pop() for i in range(n) ]))
        assert to_push[0] is not None
        self.stack.append(to_push)
        return True

    def op_unpack(self):
        popped = self.__pop_checked(list)
        if popped is None:
            logging.warning("OP_UNPACK: s_1 not existing or wrong type")
            return False
        for item in popped:
            self.stack.append(item)
        self.stack.append(len(popped))
        return True

    def op_hash(self):
        if not self.stack:
            logging.warning("OP_HASH: Stack is empty")
            return False
        popped = self.stack.pop()
        if type(popped) == int:
            popped = str(popped)
        if type(popped) == str:
            popped = popped.encode()
        if type(popped) in [Hash, Signature, Pubkey, Keypair]:
            popped = popped.value
        self.stack.append(Hash(compute_hash(popped)))
        return True

    def op_transfer(self):
        logging.info("OP_TRANSFER called")
        amount = self.__pop_checked(int)
        target_address = self.__pop_checked(Hash)
        params = self.__pop_checked(list)
        if amount is None:
            logging.warning("OP_TRANSFER: Amount must be int")
            return False
        if target_address is None:
            logging.warning("OP_TRANSFER: Target must be Hash")
            return False
        if params is None:
            logging.warning("OP_TRANSFER: Params must be Array")
            return False
        target_address = target_address.value # now bytes

        if not self.state.contains(target_address):
            logging.warning("state transition: output address does not exist")
            return False

        assert self.state.contains(self.acc.address)

        # deduct amount
        self.acc = self.acc.add_to_balance(- amount)
        if self.acc is None:
            # couldn't spend value
            logging.warning("OP_TRANSFER: couldn't deduct value from input account")
            self.stack.append(0)
            return True
        self.state = self.state.put(self.acc.address, self.acc.hash)

        # add amount
        target_acc = Account.get_from_hash(self.state.get(target_address))
        target_acc = target_acc.add_to_balance(amount)
        self.state = self.state.put(target_address, target_acc.hash)

        if target_acc.code is not None:
            vm = ScriptInterpreter(self.state, params, target_acc, [self.acc.address], amount)
            result = vm.execute_script()
            if result is None:
                logging.warning("OP_TRANSFER: target account code execution failed")
                self.stack.append(0)
                return True
            self.state = result[0]

        assert self.state is not None
        self.stack.append(1)
        return True
    
    def op_genpubkey(self):

        def rand(n) -> bytes:
            return bytes(random.getrandbits(8) for _ in range(n))

        seed = self.__pop_checked(int)
        if seed is None:
            logging.warning("OP_GETPUBKEY: seed must exist and be int")
            return False
        random.seed(seed)
        keypair = generate_keypair(rand)
        self.stack.append(Pubkey(pubkey_from_keypair(keypair)))
        return True
    
    def op_getcode(self):
        addr = self.__pop_checked(Hash)
        if addr is None:
            logging.warning("OP_GETCODE: Address must exist and be a Hash")
            return False
        acc = Account.get_from_hash(self.state.get(addr.value))
        if acc is None:
            logging.warning("OP_GETCODE: invalid account address")
            return False
        self.stack.append(acc.code)
        return True

    def _parse_numeric_item(self, item: str):
        try:
            if len(item) > 2:
                if item[0:3].lower() == 'k0x':
                    return Pubkey(unhexlify(item[3:]))
                if item[0:3].lower() == 'h0x':
                    return Hash(unhexlify(item[3:]))
                if item[0:3].lower() == 's0x':
                    return Signature(unhexlify(item[3:]))
                if item[0:3].lower() == 'p0x':
                    return Keypair(unhexlify(item[3:]))
            return int(item, 0)
        except ValueError:
            logging.warning("could not parse " + item)
            return None

    def _parse_string_item(self, item: str):
        quote = item[0]
        if quote not in [ '"', '\'' ]:
            logging.error("Could not parse: {}".format(item))
            return False
        closing_quote = False
        i = 1
        while (i < len(item)):
            if item[i] == quote:
                if i+1 == len(item):
                    closing_quote = True
                else:
                    logging.error("Unescaped quote in: {}".format(item))
                    return None
            elif item[i] == '\\':
                if i+1 == len(item):
                    logging.error("Trailing escape character in: {}".format(item))
                    return None
                if item[i+1] not in [ '\\', '"' ]:
                    logging.error("Trailing escape sequence in: {}".format(item))
                    return None
                item = item[:i] + item[i+1:]  # remove the escape character & skip next
            i += 1
        if not closing_quote:
            logging.error("Missing closing quote after: {}".format(item))
            return None
        item = item[1:-1]
        return item

    def _parse_script(self, script: str, allow_opcodes = False, is_recursive_call = False):
        result = []
        script += '\n'  # tailing newline to not get errors at the end of file parsing
        #logging.warning("script: " + script)
        while True:
            script = script.lstrip()
            #logging.warning("current result: " + str(result))
            if not script:
                break
            if script.startswith('//'):
                first = next(i for i, chr in enumerate(script) if chr == '\n')
                script = script[first+1:]
                continue
            if script[0] in [ '"', '\'' ]:
                first_quote = script[0]
                first = script[1:].find(first_quote)
                if first == -1:
                    logging.warning("[!] Error: Invalid Tx: Missing closing quote in script")
                    return None
                item = script[:first+2]
                result.append(self._parse_string_item(item))
                if result[-1] is None:
                    logging.warning("[!] Error: Invalid Tx: Could not parse string item")
                    return None
                script = script[first+2:]
                continue
            if script[0] == '[':
                sub_call = self._parse_script(script[1:], False, True)
                if sub_call is None:
                    return None
                parsed_list, script = sub_call
                result.append(parsed_list)
                continue
            if script[0] == ']':
                if not is_recursive_call:
                    logging.warning("[!] Error: Invalid Tx: Unexpected closing bracket in script")
                    return None
                return (result, script[1:])
            first = next(i for i, chr in enumerate(script) if chr in [ ' ', '\t', '\n', ']' ])
            item = script[:first]
            if item.upper() in ScriptInterpreter.operations:
                result.append(getattr(self, item.lower()))
            else:
                to_append = self._parse_numeric_item(item)
                if to_append is None:
                    logging.warning("[!] Error: Invalid Tx: Could not parse numeric item " + item)
                    return None
                result.append(to_append)  # Don't include the whitespace
            if script[first] != ']':
                first += 1
            script = script[first:]
        if is_recursive_call:
            logging.warning("[!] Error: Invalid Tx: Missing closing bracket in script")
            return None
        #logging.warning("end result: " + str(result))
        return result

    def math_operations(self, op):
        if (len(self.stack) < 2):
            logging.warning("binary math operation: Not enough arguments")
            return False

        old_first = self.__pop_checked(int)
        if old_first is None:
            return False

        old_second = self.__pop_checked(int)
        if old_second is None:
            return False

        result = op(old_first, old_second)
        if result is None:
            return False

        self.stack.append(result)
        return True

    def execute_script(self):
        """
            Run the script with the input and output scripts
            Returns None, if script failed,
            Returns (State, RetVal) if script succeeded
        """

        def execute_item(item: str):
            # Check if item is data or opcode
            if callable(item):
                # Execute the operation
                logging.warning(str(item) + " is an opcode")
                if not item():
                    return False
            else:
                # Push data onto the stack
                logging.warning(str(item) + " is data")
                self.stack.append(item)
            return True

        def execute(script: str):
            self.pc = 1
            self.retval = None
            self.program = self._parse_script(script, True)

            if self.program is None:
                return False
            while self.pc <= len(self.program):
                item = self.program[self.pc - 1] # Fetch the next item (given by the program counter)
                #logging.warning("executing " + str(item))
                logging.info("pc = " + str(self.pc) + " " + "item = \'" + str(item) + "\'")
                self.pc = self.pc + 1
                if not execute_item(item):
                    if self.retval is None:
                        logging.warning("execution failed: " + str(item))
                    else:
                        logging.warning("gonna return " + str(self.retval))
                        return True
                    return False
                logging.warning("PC: " + str(self.pc) + ", FramePointer: " + str(self.framepointer) + ", Stack: " + str(self.stack))
            return False

        logging.warning("executing new script: " + self.acc.code)

        self.stack = []
        self.stack.append(Hash(self.acc.address))
        self.stack.append([Hash(inaddr) for inaddr in self.inaddresses])
        self.stack.append(self.amountspent)

        if type(self.params_script) == list:
            #logging.warning("params_script iss list " + str(self.params_script))
            self.stack.extend(self.params_script)
        else:
            #logging.warning("params script ist script " + self.params_script)
            self.stack.extend(self._parse_script(self.params_script))
        self.stack.append(-1)
        self.framepointer = len(self.stack) - 1
        self.stack.append(-1)


        if self.stack is None:
            logging.warning("Parse failed")
            return None

        execute(self.acc.code)

        return None if self.retval is None else (self.state, self.retval)

        ## exit_code = self.__pop_checked(int)
        ## if exit_code == 1:
        ## return self.state, exit_code
        ##  elif exit_code is None:
        ##      logging.error("Invalid Tx due to missing exit code")
        ##  else:
        ##      logging.error("Invalid Tx due to exit code {}".format(exit_code))
        ##  return None
