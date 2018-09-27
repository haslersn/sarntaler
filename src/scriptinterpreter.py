#! /usr/bin/env/python3
import hashlib
import logging
from .crypto import *
from binascii import hexlify, unhexlify
from datetime import datetime


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

        Crypto:
            OP_SHA256
            OP_CHECKSIG
            OP_RETURN


        Locktime:

            OP_CHECKLOCKTIME

        Stack:
            OP_SWAP
            OP_DUP

        Control Flow:
            OP_PUSHABS
            OP_PUSHFP
            OP_POPFP    

        Math:
            OP_ADD
            OP_SUB

    """
    operations = {
        'OP_SHA256',
        'OP_CHECKSIG',
        'OP_RETURN',
        'OP_CHECKLOCKTIME',
        'OP_SWAP',
        'OP_DUP',
        'OP_PUSHFP',
        'OP_POPFP',
        'OP_PUSHABS',
        'OP_ADD',
        'OP_SUB'
    }

    def __init__(self, input_script: str, output_script: str, tx_hash: bytes):
        self.output_script = output_script
        self.input_script = input_script
        self.tx_hash = tx_hash
        self.stack = []
        self.framepointer = 0  # maybe initialize with -1


    def to_string(self):
        return " ".join(self.stack)


    # operation implementations

    def op_sha256(self):
        #The input is hashed using SHA-256.

        if not self.stack:
            logging.warning("Stack is empty")
            return False

        sha256 = hashlib.sha256()
        sha256.update(str(self.stack.pop()).encode('utf-8'))
        sha256 = hexlify(sha256.digest())
        self.stack.append(sha256.decode('utf-8'))
        return True


    def op_checksig(self):
        # The signature used by OP_CHECKSIG must be a valid signature for
        # this hash and public key.
        #If it is, 1 is returned, 0 otherwise.

        if(len(self.stack) < 2):
            logging.warning("Not enough arguments")
            self.stack.append(str(0))
            return False

        pubKey = Key.from_json_compatible(self.stack.pop())

        sig = unhexlify(self.stack.pop())

        if pubKey.verify_sign(self.tx_hash, sig):
            self.stack.append(str(1))
            return True

        logging.warning("Signature not verified")
        self.stack.append(str(0))
        return False


    def op_return(self):

        """Marks transaction as invalid.
        A standard way of attaching extra data to transactions is to add a zero-value output with a
        scriptPubKey consisting of OP_RETURN followed by exactly one pushdata op. Such outputs are
        provably unspendable, reducing their cost to the network.
        Currently it is usually considered non-standard (though valid) for a transaction to have more
        than one OP_RETURN output or an OP_RETURN output with more than one pushdata op. """

        #DONE
        self.stack.append(str(0))
        logging.warning('Transaction can not be spent!')
        return False

    def op_checklocktime(self):

        #Error Indicator
        error = 0

        #Error if Stack is empty
        if not self.stack or len(self.stack) < 2:
            error = 1

        #if top stack item is greater than the transactions nLockTime field ERROR
        temp = float(self.stack.pop())
        try:
            timestamp = datetime.fromtimestamp(temp)
        except TypeError:
            logging.error("A timestamp needs to be supplied after the OP_CHECKLOCKTIME operation!")
            self.stack.append(str(0))
            return False

        #TODO we need to make sure that the timezones are being taken care of
        if(timestamp > datetime.utcnow()):
            print("You need to wait at least " + str(timestamp - datetime.utcnow()) + " to spend this Tx")
            error = 3

        if(error):
            #errno = 1 Stack is empty
            if(error == 1):
                logging.warning('Stack is empty!')
                self.stack.append(str(0))
                return False

            #errno = 2 Top-Stack-Value < 0
            if(error == 2):
                logging.warning('Top-Stack-Value < 0')
                self.stack.append(str(0))
                return False

            #errno = 3 top stack item is greater than the transactions
            if(error == 3):
                #logging.warning('you need to wait more to unlock the funds!')
                self.stack.append(str(0))
                return False

        return True

    def op_dup(self):
        if not self.stack:
            logging.warning("Stack is empty")
            return False
        self.stack.append(self.stack[-1])
        return True


    def op_swap(self):
        if (len(self.stack) < 2):
            logging.warning("Not enough arguments")
            self.stack.append(str(0))
            return False

        old_first = self.stack.pop()
        old_second = self.stack.pop()

        self.stack.append(old_first)
        self.stack.append(old_second)
        return True

    def op_pushabs(self):
        if not self.stack:
            logging.warning("Stack is empty")
            return False
        index = int(self.stack.pop())
        if index < 0 or index >= len(self.stack):
            logging.warning("Argument of PUSHABS is not an index in the stack")
            return False
        self.stack.append(self.stack[index])
        return True

    def op_pushfp(self):
        self.stack.append(self.framepointer)
        return True

    def op_popfp(self):
        if not self.stack:
            logging.warning("Stack is empty")
            return False

        self.framepointer = self.stack.pop()
        return True

    def op_add(self):
        if (len(self.stack) < 2):
            logging.warning("Not enough arguments")
            self.stack.append(str(0))
            return False

        old_first = self.stack.pop()
        old_second = self.stack.pop()

        try:
            sum = int(old_first) + int(old_second)
        except ValueError:
            logging.warning("Wrong type of arguments. Could not convert " + old_first + " and " + old_second + " to integers")
            self.stack.append(str(0))
            return False

        self.stack.append(str(sum))
        return True

    def op_sub(self):
        if (len(self.stack) < 2):
            logging.warning("Not enough arguments")
            return False

        old_first = self.stack.pop()
        old_second = self.stack.pop()

        try:
            result = int(old_second) - int(old_first)
        except ValueError:
            logging.warning("Wrong type of arguments. Could not convert " + old_first + " and " + old_second + " to integers")
            return False

        self.stack.append(str(result))
        return True



    def execute_script(self):
        """
            Run the script with the input and output scripts
        """
        script = self.input_script.split() + self.output_script.split()

        while script:

            next_item = script.pop(0) # Fetch next item (start reading from beginning of script)

            # Check if item is data or opcode. If data, push onto stack.
            if (next_item not in ScriptInterpreter.operations):
                self.stack.append(next_item)  # if it's data we add it to the stack
            else:
                op = getattr(self, next_item.lower())  # Proper operation to be executed
                op()  # execute the command!


        if (len(self.stack)==1 and self.stack[-1] == '1'):
            return True
        else:
            logging.warning("[!] Error: Invalid Tx.")
            return False

