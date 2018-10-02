from src.blockchain.account import Account, StorageItem
from src.scriptinterpreter import ScriptInterpreter
from src.blockchain.merkle_trie import MerkleTrie, MerkleTrieStorage
from Crypto.PublicKey import RSA

from src.blockchain.crypto import *

empty_mt = MerkleTrie(MerkleTrieStorage()) # not relevant in this test yet, but needs to exist

def get_dummy_account():
    return Account(bytes(1), 0, "", 1, [])

def get_account(mt : MerkleTrie, program : str):
    acc = Account(bytes(1), 0, program, 1, [])
    nmt = mt.put(acc.address, acc.hash)
    return nmt, acc


def test_passWithOne():
    mt, acc = get_account(empty_mt, "1 OP_RET")
    si = ScriptInterpreter(mt, "", acc, None)
    ret = si.execute_script()
    assert ret != None
    _, retval = ret
    assert retval == 1

def test_failWithMoreThanOneStackElement():
    mt, acc = get_account(empty_mt, "1 2 3")
    si = ScriptInterpreter(mt, "", acc, None)
    assert si.execute_script() == None

def test_dup():
    si = ScriptInterpreter(empty_mt, None, get_dummy_account(), None)
    si.stack = ['3', '2']
    res = si.op_dup()
    assert si.stack == ['3', '2', '2']
    assert res == True

def test_dup_emptystack():
    si = ScriptInterpreter(empty_mt, None, get_dummy_account(), None)
    si.stack = []
    res = si.op_dup()
    assert res == False

def test_dup2():
    script_finalstack_test("3 2 OP_DUP 1 OP_RET", [3, 2, 2])

def test_swap():
    script_finalstack_test("3 2 1 OP_SWAP 1 OP_RET", [3, 1, 2])

def test_swapWithOneElement():
    mt, acc = get_account(empty_mt, "1 OP_SWAP 1 OP_RET")
    si = ScriptInterpreter(mt, "", acc, None)
    assert not si.execute_script()

def test_pushFP():
    mt, acc = get_account(empty_mt, "3 2 1 OP_PUSHFP 1 OP_RET")
    si = ScriptInterpreter(mt, "", acc, None)
    si.execute_script()
    assert si.stack == [3, 2, 1, -1]

def test_popFP():
    mt, acc = get_account(empty_mt, "3 2 42 OP_POPFP")
    si = ScriptInterpreter(mt, "", acc, None)
    si.execute_script()
    assert si.framepointer == 42
    emptystack_test("OP_POPFP")

def test_incfp():
    si = ScriptInterpreter(empty_mt, "", Account(bytes(1), 0, "3 2 7 OP_INCFP", 1, []), None)
    si.execute_script()
    assert si.stack == [3, 2]
    assert si.framepointer == 6
    emptystack_test("OP_INCFP")

## TEST UPDATED UNTIL HERE


def test_popVoid():
    script_finalstack_test("1 2 3 OP_POPVOID 1 OP_RET", [1, 2])
    emptystack_test("OP_POPVOID")

def test_pushabs_ok():
    script_finalstack_test("5 6 7 8 1 OP_PUSHABS 1 OP_RET", [5, 6, 7, 8, 6])


def test_pushabs_notok():
    si = ScriptInterpreter(empty_mt, None, get_dummy_account(), None)
    si.stack = [5, 6, 7, 8, 4]
    res = si.op_pushabs()
    assert res == False


def test_add():
    script_finalstack_test("3 2 42 OP_ADD 1 OP_RET", [3, 44])
    emptystack_noninteger_binaryop_test('OP_ADD')


def test_sub():
    script_finalstack_test("3 5 1 OP_SUB 1 OP_RET", [3, 4])
    emptystack_noninteger_binaryop_test('OP_SUB')


def test_mul():
    script_finalstack_test("3 5 2 OP_MUL 1 OP_RET", [3, 10])
    emptystack_noninteger_binaryop_test('OP_MUL')


def test_div():
    script_finalstack_test("3 10 2 OP_DIV 1 OP_RET", [3, 5])
    script_finalstack_test("3 5 2 OP_DIV 1 OP_RET", [3, 2])
    emptystack_noninteger_binaryop_test('OP_DIV')


def test_mod():
    script_finalstack_test("3 10 2 OP_MOD 1 OP_RET", [3, 0])
    script_finalstack_test("3 5 2 OP_MOD 1 OP_RET", [3, 1])
    emptystack_noninteger_binaryop_test('OP_MOD')


def test_and():
    script_finalstack_test("3 5 2 OP_AND 1 OP_RET", [3, 0])
    script_finalstack_test("3 3 2 OP_AND 1 OP_RET", [3, 2])
    emptystack_noninteger_binaryop_test('OP_AND')


def test_or():
    script_finalstack_test("3 5 1 OP_OR 1 OP_RET", [3, 5])
    script_finalstack_test("3 5 3 OP_OR 1 OP_RET", [3, 7])
    emptystack_noninteger_binaryop_test('OP_OR')


def test_xor():
    script_finalstack_test("3 5 1 OP_XOR 1 OP_RET", [3, 4])
    script_finalstack_test("3 5 3 OP_XOR 1 OP_RET", [3, 6])
    emptystack_noninteger_binaryop_test('OP_XOR')

def test_not():
    script_finalstack_test("3 1 OP_NOT 1 OP_RET", [3, 0])
    script_finalstack_test("3 0 OP_NOT 1 OP_RET", [3, 1])
    emptystack_noninteger_unaryop_test('OP_NOT')
    si_notbool_stack = ScriptInterpreter(empty_mt, 'OP_NOT', Account(bytes(1), 0, "2 OP_NOT", 1, []), None)
    assert not si_notbool_stack.execute_script()

def test_neg():
    script_finalstack_test("3 4 OP_NEG 1 OP_RET", [3, -4])
    emptystack_noninteger_unaryop_test('OP_NEG')

def test_equ():
    script_finalstack_test("3 4 5 OP_EQU 1 OP_RET", [3, 0])
    script_finalstack_test("3 4 4 OP_EQU 1 OP_RET", [3, 1])
    emptystack_test('OP_EQU')


def test_le():
    script_finalstack_test("3 5 1 OP_LE 1 OP_RET", [3, 0])
    script_finalstack_test("3 5 6 OP_LE 1 OP_RET", [3, 1])
    script_finalstack_test("3 5 5 OP_LE 1 OP_RET", [3, 1])
    emptystack_noninteger_binaryop_test('OP_LE')


def test_ge():
    script_finalstack_test("3 5 1 OP_GE 1 OP_RET", [3, 1])
    script_finalstack_test("3 5 6 OP_GE 1 OP_RET", [3, 0])
    script_finalstack_test("3 5 5 OP_GE 1 OP_RET", [3, 1])
    emptystack_noninteger_binaryop_test('OP_GE')


def test_lt():
    script_finalstack_test("3 5 1 OP_LT 1 OP_RET", [3, 0])
    script_finalstack_test("3 5 6 OP_LT 1 OP_RET", [3, 1])
    script_finalstack_test("3 5 5 OP_LT 1 OP_RET", [3, 0])
    emptystack_noninteger_binaryop_test('OP_LT')


def test_gt():
    script_finalstack_test("3 5 1 OP_GT 1 OP_RET", [3, 1])
    script_finalstack_test("3 5 6 OP_GT 1 OP_RET", [3, 0])
    script_finalstack_test("3 5 5 OP_GT 1 OP_RET", [3, 0])
    emptystack_noninteger_binaryop_test('OP_GT')


def test_pushr():
    mt, acc = get_account(empty_mt, "0 1 2 3 2 OP_PUSHR 1 OP_RET")
    si = ScriptInterpreter(mt, "", acc, None)
    si.framepointer = 3
    si.execute_script()  # should push 3 (framepointer) + 2 (operand) = 5th element
    assert si.stack == [0, 1, 2, 3, 1]

def test_pushr_2():
    mt, acc = get_account(empty_mt, '0 2 \"three\" 4 5 3 OP_PUSHR 1 OP_RET')
    si = ScriptInterpreter(mt, "", acc, None)
    si.framepointer = 0
    si.execute_script()  # should push 0 (framepointer) + 3 (operand) = 3rd element
    assert si.stack == [0, 2, "three", 4, 5, "three"]

def test_popr():
    mt, acc = get_account(empty_mt, '0 1 2 3 4 "storethis" 2 OP_POPR 1 OP_RET')
    si = ScriptInterpreter(mt, "", acc, None)
    si.framepointer = 1
    si.execute_script()  # should store to 1 (framepointer) + 2 (operand) = 3rd element
    assert si.stack == [0, "storethis", 2, 3, 4]
    emptystack_test('OP_POPR')

def script_finalstack_test(script: str, finalstack: list):
    mt, acc = get_account(empty_mt, script)
    si = ScriptInterpreter(mt, "", acc, None)
    si.execute_script()
    assert si.stack == finalstack

def test_div_nonintegers():
    mt, acc = get_account(empty_mt, "a b OP_DIV 1 OP_RET")
    si = ScriptInterpreter(mt, "", acc, None)
    assert not si.execute_script()

def test_pack():
    script_finalstack_test('3 2 1 3 OP_PACK 1 OP_RET', [[3, 2, 1]])
    script_finalstack_test('3 "Hello" -100 22 18 0 6 OP_PACK 1 OP_RET', [[3, "Hello", -100, 22, 18, 0]])

def test_unpack():
    #script_finalstack_test('"3 2 1" OP_UNPACK 1 OP_RET', [3, 2, 1, 3])
    script_finalstack_test('[3 \'Hello\' -100 22 18] OP_UNPACK 1 OP_RET', [3, "Hello", -100, 22, 18, 5])

#def emptystack_noninteger_test(op: str):

def emptystack_noninteger_binaryop_test(op: str):
    emptystack_test(op)
    si_one_elem_stack = ScriptInterpreter(empty_mt, op, Account(bytes(1), 0, "1 " + op, 1, []), None)
    assert not si_one_elem_stack.execute_script()
    si_noninteger = ScriptInterpreter(empty_mt, "a b " + op + " 1", get_dummy_account(), None)
    assert not si_noninteger.execute_script()

def emptystack_noninteger_unaryop_test(op: str):
    emptystack_test(op)
    si_noninteger = ScriptInterpreter(empty_mt, "a " + op + " 1", get_dummy_account(), None)
    assert not si_noninteger.execute_script()

def emptystack_test(op: str):
    si_emptystack = ScriptInterpreter(empty_mt, op, get_dummy_account(), None)
    assert not si_emptystack.execute_script()

# fixed until here


# TODO SHA256 test
from math import gcd, factorial
def test_gcd_script():
    a = 324432
    b = 2345223
    gcdfile = open("./src/labvm/testprograms/gcd.labvm","r")
    gcdstr = gcdfile.read()
    gcdstr = str(a) + "\n" + str(b) + "\n" + gcdstr
    gcdfile.close()
    mt, acc = get_account(empty_mt, gcdstr)
    si = ScriptInterpreter(mt, "", acc, None)
    si.execute_script()
    print("Stack after gcd script:",si.stack)
    assert si.stack[0] == gcd(a,b)

def test_call_test():
    #please use -s to debug, should add 1 onto stack
    f = open("./src/labvm/testprograms/calltest.labvm","r")
    fstr = f.read()
    f.close()
    mt, acc = get_account(empty_mt, fstr)
    si = ScriptInterpreter(mt, "", acc, None)
    assert si.execute_script()

import os
import time
def test_factorial():

    t = time.time()
    f = open("./src/labvm/testprograms/factorial.labvm", "r")
    fstr = f.read()
    f.close()
    #fstr = fstr.replace('FACOPERAND', str(i))
    #fstr = fstr.replace('FACRESULT', str(factorial(i)))
    mt, acc = get_account(empty_mt, fstr)
    si = ScriptInterpreter(mt, "", acc, None)
    si.execute_script()

def test_getbal():
    si = ScriptInterpreter(empty_mt, "", Account(bytes(1), 100, "OP_GETBAL 1 OP_RET", 1, []), None)
    assert si.execute_script()
    assert si.stack == [100]

def test_getstor():
    si = ScriptInterpreter(empty_mt, "", Account(bytes(1), 0, '"myvar" OP_GETSTOR 1 OP_RET', 1, [StorageItem('myvar', 'int', 42)]), None)
    assert si.execute_script()
    assert si.stack == [42]

def test_getstor_invalid():
    si = ScriptInterpreter(empty_mt, "", Account(bytes(1), 0, '"invalid" OP_GETSTOR 1 OP_RET', 1, [StorageItem('myvar', 'int', 42)]), None)
    assert not si.execute_script()

def test_setstor():
    myacc = Account(bytes(27), 278, '42 "myvar" OP_SETSTOR 1 OP_RET', 1, [StorageItem('myvar', 'int', 0)])
    my_mt = empty_mt.put(myacc.address, myacc.hash)
    si = ScriptInterpreter(my_mt, "", myacc, None)
    new_state,_ = si.execute_script()
    assert new_state
    new_acc = Account.get_from_hash(new_state.get(myacc.address))
    assert new_acc.get_storage('myvar') == 42

def test_setstor_invalid():
    si = ScriptInterpreter(empty_mt, "", Account(bytes(1), 0, '42 "invalid" OP_SETSTOR 1 OP_RET', 1, [StorageItem('myvar', 'int', 42)]), None)
    assert not si.execute_script()

def test_create_contr():
    si = ScriptInterpreter(empty_mt, '0 1 2 3 4 "storethis" 2 OP_POPR 1 OP_RET', get_dummy_account(), None)
    si.execute_script()

def test_pack_different_types():
    mt, acc = get_account(empty_mt, "h0xABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDABCD 0 'abc' 3 OP_PACK 'def' OP_SWAP 2 OP_PACK 1 OP_RET")
    si = ScriptInterpreter(mt, "", acc, None)
    assert si.execute_script()

def test_unpack_different_types():
    mt, acc = get_account(empty_mt, "h0xABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDABCD 0 'abc' 3 OP_PACK 'def' OP_SWAP 2 OP_PACK OP_UNPACK OP_POPVOID OP_UNPACK OP_POPVOID 1 OP_RET")
    si = ScriptInterpreter(mt, "", acc, None)
    assert si.execute_script()

def test_checkkeypair_suc():
    #succsess test
    key = RSA.generate(1024)

    privKey = key.exportKey('DER')
    pubKey = key.publickey().exportKey('DER')
    fstr = "K0x" + str(pubKey.hex()) + "\nK0x" + str(privKey.hex()) + "\nop_checkkeypair\n1 OP_RET"
    mt, acc = get_account(empty_mt, fstr)
    si = ScriptInterpreter(mt, "", acc, None)
    assert si.execute_script()

def test_checkkeypair_fail():
    #fail test
    key1 = RSA.generate(1024)
    key2 = RSA.generate(1024)

    privKey = key1.exportKey('DER')
    pubKey = key2.publickey().exportKey('DER')
    fstr = "K0x" + str(pubKey.hex()) + "\nK0x" + str(privKey.hex()) + "\nop_checkkeypair\n1 OP_RET"

    mt, acc = get_account(empty_mt, fstr)
    si = ScriptInterpreter(mt, "", acc, None)
    assert not si.execute_script()
