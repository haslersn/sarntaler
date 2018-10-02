#! /usr/bin/env/python3
import hashlib
import logging

from src.blockchain.account import Account
from src.blockchain.merkle_trie import MerkleTrie
from .crypto import *
from binascii import hexlify, unhexlify
from datetime import datetime
import src.crypto as cr
from Crypto.PublicKey import RSA


# TODO: Put the following two classes into crypt.py

class Hash:
    def __init__(self, value: bytes):
        self.value = value

class Signature:
    def __init__(self, value: bytes):
        self.value = value

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

    operations = {
        'OP_SHA256',
        'OP_CHECKKEYPAIR',
        'OP_CHECKSIG',
        'OP_KILL',
        'OP_CHECKLOCKTIME',

        'OP_SWAP',
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
        'OP_SETSTOR',
        'OP_GETSTOR',

        'OP_PACK',
        'OP_UNPACK'
    }

    def __init__(self, state: MerkleTrie, params_script: str, acc: Account, tx_hash: bytes):
        self.acc = acc
        self.state = state
        self.params_script = params_script
        self.tx_hash = tx_hash

        self.stack = []
        self.program = []

        self.framepointer = 0  # maybe initialize with -1
        self.pc = 0            # maybe initialize with -1


    def to_string(self):
        return " ".join(self.stack)


    # operation implementations

    def __pop_checked(self, t: type):
        if not self.stack:
            logging.warning("Stack is empty. Expected {}".format(t.__name__))
            return None
        top = self.stack.pop()
        if type(top) is not t:
            logging.warning("Wrong type on top of stack. Expected {} but found {}".format(
                t.__name__, type(top).__name__))
            return None
        if type(top) in [ Hash, Signature ]:
            return top.value
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

    def op_checkkeypair(self):
        """Checks if public-key (1. argument) and privat-key (2. argument) are
        part of the same key-pair."""
        privKey = self.__pop_checked(Key)
        if privKey is None:
            logging.warning("OP_CHECKKEY: Stack is empty or top element not a key")
            return False

        pubKey = self.__pop_checked(Key)
        if pubKey is None:
            logging.warning("OP_CHECKKEY: Stack is empty or top element not a key")
            return False

        beforenc = cr.get_random_int(256)
        enctxt = pubKey.rsa.encrypt(beforenc, 1)[0]
        afterenc = privKey.rsa.decrypt(enctxt)
        if beforenc != afterenc:
            return False

        return True

    def op_checksig(self):
        # The signature used by OP_CHECKSIG must be a valid signature for
        # this hash and public key.
        #If it is, 1 is returned, 0 otherwise.
        pubKey = self.__pop_checked(Key)
        if pubKey is None:
            logging.warning("OP_CHECKSIG: Stack is empty or top element not a key")
            return False

        sig = self.__pop_checked(Signature)
        if sig is None:
            logging.warning("OP_CHECKSIG: Stack is empty or top element not a signature")
            return False

        if pubKey.verify_sign(self.tx_hash, sig):
            self.stack.append(1)
            return True

        logging.warning("OP_CHECKSIG: Signature not verified")
        self.stack.append(0)
        return True


    def op_kill(self):

        """Marks transaction as invalid.
        A standard way of attaching extra data to transactions is to add a zero-value output with a
        scriptPubKey consisting of OP_KILL followed by exactly one pushdata op. Such outputs are
        provably unspendable, reducing their cost to the network.
        Currently it is usually considered non-standard (though valid) for a transaction to have more
        than one OP_KILL output or an OP_KILL output with more than one pushdata op. """

        #DONE
        logging.warning('Transaction can not be spent!')
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

        if self.framepointer == -1:
            logging.warning("OP_RET: Last Return, gonna exit program")
            return "ret"
        result = self.stack.pop()
        self.pc = self.stack[self.framepointer + 1] # restore the program counter
        del self.stack[(self.framepointer+1):]          # reset the stack pointer
        self.framepointer = self.stack.pop()        # restore the framepointer
        self.stack.append(result)
        return True

    def op_getbal(self):
        self.stack.append(self.acc.balance)
        return True

    def op_getstor(self):
        if not self.stack:
            logging.warning("OP_GETSTOR: Stack is empty")
            return False
        var_name = self.__pop_checked(str)
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
        var_value = self.stack.pop()
        new_acc = self.acc.set_storage(var_name, var_value)
        if new_acc == None:
            logging.warning("OP_SETSTOR: Could not set storage for " + var_name)
            return False
        self.acc = new_acc
        self.state = self.state.put(self.acc.address, self.acc.hash)
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

    def _parse_numeric_item(self, item: str):
        try:
            if len(item) > 2:
                if item[0:3].lower() == 'k0x':
                    return Key(unhexlify(item[3:]))
                if item[0:3].lower() == 'h0x':
                    return Hash(unhexlify(item[3:]))
                if item[0:3].lower() == 's0x':
                    return Signature(unhexlify(item[3:]))
            return int(item, 0)
        except ValueError:
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

    def _parse_script(self, script: str, allow_opcodes = True, is_recursive_call = False):
        result = []
        script += '\n'  # tailing newline to not get errors at the end of file parsing
        while True:
            script = script.lstrip()
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
                    logging.warning("[!] Error: Invalid Tx: Could not parse numeric item")
                    return None
                result.append(to_append)  # Don't include the whitespace
            if script[first] != ']':
                first += 1
            script = script[first:]
        if is_recursive_call:
            logging.warning("[!] Error: Invalid Tx: Missing closing bracket in script")
            return None
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

        def execute_item(item: str, param=False):
            # Check if item is data or opcode
            if callable(item):
                if param:
                    return False
                # Execute the operation
                logging.warning(str(item) + " is an opcode")
                ret = item()
                if ret in [False, "ret"]:
                    return ret
            else:
                # Push data onto the stack
                logging.warning(str(item) + " is data")
                self.stack.append(item)
            return True

        def execute(script: str, param=False):
            self.pc = 1
            self.framepointer = -1
            self.program = self._parse_script(script)
            if self.program is None:
                return None
            while self.pc <= len(self.program):
                item = self.program[self.pc - 1] # Fetch the next item (given by the program counter)
                logging.info("pc = " + str(self.pc) + " " + "item = \'" + str(item) + "\'")
                self.pc = self.pc + 1
                ret = execute_item(item, param)
                if ret in [False, "ret"]:
                    return self.stack.pop() if ret == "ret" else None
                logging.warning("PC: " + str(self.pc) + ", FramePointer: " + str(self.framepointer) + ", Stack: " + str(self.stack))
            return True if param else None

        if not execute(self.params_script, True):
            return None
        ret = execute(self.acc.code, False)
        return None if not ret else (self.state, ret)

        ## exit_code = self.__pop_checked(int)
        ## if exit_code == 1:
        ## return self.state, exit_code
        ##  elif exit_code is None:
        ##      logging.error("Invalid Tx due to missing exit code")
        ##  else:
        ##      logging.error("Invalid Tx due to exit code {}".format(exit_code))
        ##  return None
