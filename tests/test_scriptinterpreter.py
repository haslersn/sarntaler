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

def test_swap():
    si = ScriptInterpreter(None, None, None)
    si.stack = ['3', '2', '1']
    si.op_swap()
    assert si.stack == ['3', '1', '2']