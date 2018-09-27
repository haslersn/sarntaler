class Boolex(Node):
    def __init__(self, op):
        self.op = op


class BoolexBinary(Boolex):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class BoolexNot(Boolex):
    def __init__(self, operand):
        self.operand = operand
