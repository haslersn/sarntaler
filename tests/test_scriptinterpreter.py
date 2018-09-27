from src.scriptinterpreter import ScriptInterpreter
from src.transaction import Transaction

def test_passWithOne():
    t = Transaction([], [], timestamp=None)
    si = ScriptInterpreter("1", "", t.get_hash())
    assert si.execute_script()


def test_failWithMoreThanOneStackElement():
    t = Transaction([], [], timestamp=None)
    si = ScriptInterpreter("1 2 3", "", t.get_hash())
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
    si = ScriptInterpreter("3 2 OP_DUP 1", "", None)
    res = si.execute_script()
    assert si.stack == [3, 2, 2]


def test_swap():
    si = ScriptInterpreter("3 2 1 OP_SWAP 1", "", None)
    si.execute_script()
    assert si.stack == [3, 1, 2]


def test_swapWithOneElement():
    si = ScriptInterpreter(None, None, None)
    si.stack = ['1']
    assert not si.op_swap()


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
    si = ScriptInterpreter("5 6 7 8 1 OP_PUSHABS 1", "", None)
    si.execute_script()
    assert si.stack == [5, 6, 7, 8, 6]

def test_pushabs_notok():
    si = ScriptInterpreter(None, None, None)
    si.stack = [5, 6, 7, 8, 4]
    res = si.op_pushabs()
    assert res == False

def test_add():
    si = ScriptInterpreter("3 2 42 OP_ADD 1", "", None)
    si.execute_script()
    assert si.stack == [3, 44]

def test_add_emptystack():
    si = ScriptInterpreter("OP_ADD", "", None)
    assert not si.execute_script()

def test_add_nonintegers():
    si = ScriptInterpreter("a b OP_ADD 1", "", None)
    assert not si.execute_script()

def test_sub():
    si = ScriptInterpreter("3 5 1 OP_SUB 1", "", None)
    si.execute_script()
    assert si.stack == [3, 4]

def test_sub_emptystack():
    si = ScriptInterpreter("OP_SUB", "", None)
    assert not si.execute_script()

def test_sub_nonintegers():
    si = ScriptInterpreter("a b OP_SUB 1", "", None)
    assert not si.execute_script()

def test_mul():
    si = ScriptInterpreter("3 5 2 OP_MUL 1", "", None)
    si.execute_script()
    assert si.stack == [3, 10]

def test_mul_emptystack():
    si = ScriptInterpreter("OP_MUL", "", None)
    assert not si.execute_script()

def test_mul_nonintegers():
    si = ScriptInterpreter("a b OP_MUL 1", "", None)
    assert not si.execute_script()

def test_div():
    si = ScriptInterpreter("3 10 2 OP_DIV 1", "", None)
    si.execute_script()
    assert si.stack == [3, 5]

def test_div_noneven():
    si = ScriptInterpreter("3 5 2 OP_DIV 1", "", None)
    si.execute_script()
    assert si.stack == [3, 2]

def test_div_emptystack():
    si = ScriptInterpreter("OP_DIV", "", None)
    assert not si.execute_script()

def test_div_nonintegers():
    si = ScriptInterpreter("a b OP_DIV 1", "", None)
    assert not si.execute_script()

def test_gcd_script():
    gcdfile = open("./src/labvm/gcd.labvm","r")
    gcdstr = gcdfile.read()
    gcdfile.close()
    si = ScriptInterpreter(gcdstr, "", None)
    print("Stack after gcd script:" ,si.stack)

