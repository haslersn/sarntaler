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
    si = ScriptInterpreter("3 2 OP_DUP", "", None)
    res = si.execute_script()
    assert si.stack == ['3', '2', '2']


def test_swap():
    si = ScriptInterpreter("3 2 1 OP_SWAP", "", None)
    si.execute_script()
    assert si.stack == ['3', '1', '2']


def test_swapWithOneElement():
    si = ScriptInterpreter(None, None, None)
    si.stack = ['1']
    assert not si.op_swap()


def test_pushFP():
    si = ScriptInterpreter("3 2 1 OP_PUSHFP", "", None)
    si.framepointer = '27'
    si.execute_script()
    assert si.stack == ['3', '2', '1', '27']


def test_popFP():
    si = ScriptInterpreter("3 2 42 OP_POPFP", "", None)
    si.execute_script()
    assert si.stack == ['3', '2']
    assert si.framepointer == '42'


def test_popFP_emptystack():
    si = ScriptInterpreter("OP_POPFP", "", None)
    assert not si.execute_script()


def test_pushabs_ok():
    si = ScriptInterpreter("5 6 7 8 1 OP_PUSHABS", "", None)
    si.execute_script()
    assert si.stack == ['5', '6', '7', '8', '6']
