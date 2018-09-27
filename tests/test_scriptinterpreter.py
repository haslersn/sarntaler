from src.scriptinterpreter import ScriptInterpreter

def test_passWithOne():
    si = ScriptInterpreter("1", "", None)
    assert si.execute_script()


def test_failWithMoreThanOneStackElement():
    si = ScriptInterpreter("1 2 3", "", None)
    assert not si.execute_script()


def test_dup():
    si = ScriptInterpreter(None, None, None)
    si.stack = ['3', '2']
    res = si.op_dup()
    assert si.stack == ['3', '2', '2']
    assert res == True


def test_dup_emptystack():
    si = ScriptInterpreter(None, None, None)
    si.stack = []
    res = si.op_dup()
    assert res == False


def test_dup2():
    script_finalstack_test("3 2 OP_DUP 1", [3, 2, 2])


def test_swap():
    script_finalstack_test("3 2 1 OP_SWAP 1", [3, 1, 2])


def test_swapWithOneElement():
    si = ScriptInterpreter("1 OP_SWAP 1", None, None)
    assert not si.execute_script()


def test_pushFP():
    si = ScriptInterpreter("3 2 1 OP_PUSHFP 1", "", None)
    si.framepointer = 27
    si.execute_script()
    assert si.stack == [3, 2, 1, 27]


def test_popFP():
    si = ScriptInterpreter("3 2 42 OP_POPFP 1", "", None)
    si.execute_script()
    assert si.stack == [3, 2]
    assert si.framepointer == 42


def test_popFP_emptystack():
    si = ScriptInterpreter("OP_POPFP", "", None)
    assert not si.execute_script()


def test_pushabs_ok():
    script_finalstack_test("5 6 7 8 1 OP_PUSHABS 1", [5, 6, 7, 8, 6])


def test_pushabs_notok():
    si = ScriptInterpreter(None, None, None)
    si.stack = [5, 6, 7, 8, 4]
    res = si.op_pushabs()
    assert res == False


def test_add():
    script_finalstack_test("3 2 42 OP_ADD 1", [3, 44])
    emptystack_noninteger_binaryop_test('OP_ADD')


def test_sub():
    script_finalstack_test("3 5 1 OP_SUB 1", [3, 4])
    emptystack_noninteger_binaryop_test('OP_SUB')


def test_mul():
    script_finalstack_test("3 5 2 OP_MUL 1", [3, 10])
    emptystack_noninteger_binaryop_test('OP_MUL')


def test_div():
    script_finalstack_test("3 10 2 OP_DIV 1", [3, 5])
    script_finalstack_test("3 5 2 OP_DIV 1", [3, 2])
    emptystack_noninteger_binaryop_test('OP_DIV')


def test_mod():
    script_finalstack_test("3 10 2 OP_MOD 1", [3, 0])
    script_finalstack_test("3 5 2 OP_MOD 1", [3, 1])
    emptystack_noninteger_binaryop_test('OP_MOD')


def test_and():
    script_finalstack_test("3 5 2 OP_AND 1", [3, 0])
    script_finalstack_test("3 3 2 OP_AND 1", [3, 2])
    emptystack_noninteger_binaryop_test('OP_AND')


def test_or():
    script_finalstack_test("3 5 1 OP_OR 1", [3, 5])
    script_finalstack_test("3 5 3 OP_OR 1", [3, 7])
    emptystack_noninteger_binaryop_test('OP_OR')


def test_xor():
    script_finalstack_test("3 5 1 OP_XOR 1", [3, 4])
    script_finalstack_test("3 5 3 OP_XOR 1", [3, 6])
    emptystack_noninteger_binaryop_test('OP_XOR')

def test_not():
    script_finalstack_test("3 1 OP_NOT 1", [3, 0])
    script_finalstack_test("3 0 OP_NOT 1", [3, 1])
    emptystack_noninteger_unaryop_test('OP_NOT')
    si_notbool_stack = ScriptInterpreter('OP_NOT', "2 OP_NOT", None)
    assert not si_notbool_stack.execute_script()

def test_neg():
    script_finalstack_test("3 4 OP_NEG 1", [3, -4])
    emptystack_noninteger_unaryop_test('OP_NEG')

def test_equ():
    script_finalstack_test("3 4 5 OP_EQU 1", [3, 0])
    script_finalstack_test("3 4 4 OP_EQU 1", [3, 1])
    emptystack_test('OP_EQU')


def test_le():
    script_finalstack_test("3 5 1 OP_LE 1", [3, 0])
    script_finalstack_test("3 5 6 OP_LE 1", [3, 1])
    script_finalstack_test("3 5 5 OP_LE 1", [3, 1])
    emptystack_noninteger_binaryop_test('OP_LE')


def test_ge():
    script_finalstack_test("3 5 1 OP_GE 1", [3, 1])
    script_finalstack_test("3 5 6 OP_GE 1", [3, 0])
    script_finalstack_test("3 5 5 OP_GE 1", [3, 1])
    emptystack_noninteger_binaryop_test('OP_GE')


def test_lt():
    script_finalstack_test("3 5 1 OP_LT 1", [3, 0])
    script_finalstack_test("3 5 6 OP_LT 1", [3, 1])
    script_finalstack_test("3 5 5 OP_LT 1", [3, 0])
    emptystack_noninteger_binaryop_test('OP_LT')


def test_gt():
    script_finalstack_test("3 5 1 OP_GT 1", [3, 1])
    script_finalstack_test("3 5 6 OP_GT 1", [3, 0])
    script_finalstack_test("3 5 5 OP_GT 1", [3, 0])
    emptystack_noninteger_binaryop_test('OP_GT')


def script_finalstack_test(script: str, finalstack: list):
    si = ScriptInterpreter(script, "", None)
    si.execute_script()
    assert si.stack == finalstack

def test_div_nonintegers():
    si = ScriptInterpreter("a b OP_DIV 1", "", None)
    assert not si.execute_script()

#def emptystack_noninteger_test(op: str):

def emptystack_noninteger_binaryop_test(op: str):
    emptystack_test(op)
    si_one_elem_stack = ScriptInterpreter(op, "1 " + op, None)
    assert not si_one_elem_stack.execute_script()
    si_noninteger = ScriptInterpreter("a b " + op + " 1", "", None)
    assert not si_noninteger.execute_script()

def emptystack_noninteger_unaryop_test(op: str):
    emptystack_test(op)
    si_noninteger = ScriptInterpreter("a " + op + " 1", "", None)
    assert not si_noninteger.execute_script()

def emptystack_test(op: str):
    si_emptystack = ScriptInterpreter(op, "", None)
    assert not si_emptystack.execute_script()


# TODO SHA256 test
from math import gcd
def test_gcd_script():
    a = 12
    b = 6
    gcdfile = open("./src/labvm/gcd.labvm","r")
    gcdstr = gcdfile.read()
    gcdstr = str(a) + "\n" + str(b) + "\n" + gcdstr
    gcdfile.close()
    si = ScriptInterpreter(gcdstr, "", None)
    si.execute_script()
    print("Stack after gcd script:",si.stack)
    assert si.stack[3] == gcd(a,b)
