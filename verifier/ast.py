# verifier/ast.py

class ASTNode:
    """Base class for all AST nodes."""
    pass

class Expr(ASTNode):
    """Base class for all arithmetic and numeric expressions."""
    pass

class Var(Expr):
    """Represents a variable (x, y, or z)."""
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Var({self.name})"

class Num(Expr):
    """Represents a numeric constant (integer)."""
    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return f"Num({self.val})"

class BinOp(Expr):
    """Represents a binary arithmetic operation (e.g. +, -, *, /, %)."""
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinOp('{self.op}', {self.left}, {self.right})"

class BoolExpr(ASTNode):
    """Base class for all boolean/logical expressions."""
    pass

class BoolConst(BoolExpr):
    """Represents a boolean constant (True or False)."""
    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return f"BoolConst({self.val})"

class CompareOp(BoolExpr):
    """Represents a comparison operator (==, !=, <, <=, >, >=)."""
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"CompareOp('{self.op}', {self.left}, {self.right})"

class AndExpr(BoolExpr):
    """Represents a boolean AND operation."""
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"AndExpr({self.left}, {self.right})"

class OrExpr(BoolExpr):
    """Represents a boolean OR operation."""
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"OrExpr({self.left}, {self.right})"

class NotExpr(BoolExpr):
    """Represents a boolean NOT operation."""
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"NotExpr({self.expr})"

class Stmt(ASTNode):
    """Base class for statements."""
    pass

class AssignStmt(Stmt):
    """Represents an assignment statement (e.g. x := x + 1)."""
    def __init__(self, var_name, expr):
        self.var_name = var_name
        self.expr = expr

    def __repr__(self):
        return f"AssignStmt('{self.var_name}', {self.expr})"

class IfStmt(Stmt):
    """Represents an if-then-else statement."""
    def __init__(self, cond, then_branch, else_branch):
        self.cond = cond
        self.then_branch = then_branch
        self.else_branch = else_branch

    def __repr__(self):
        return f"IfStmt({self.cond}, {self.then_branch}, {self.else_branch})"

class WhileStmt(Stmt):
    """Represents a while-do statement."""
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def __repr__(self):
        return f"WhileStmt({self.cond}, {self.body})"

class SkipStmt(Stmt):
    """Represents a skip statement."""
    def __repr__(self):
        return "SkipStmt()"

class SeqStmt(Stmt):
    """Represents a sequence of statements (separated by ';')."""
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"SeqStmt({self.statements})"
