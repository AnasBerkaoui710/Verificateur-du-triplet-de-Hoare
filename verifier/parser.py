# verifier/parser.py

import re
from verifier.ast import (
    Var, Num, BinOp, BoolConst, CompareOp, AndExpr, OrExpr, NotExpr,
    AssignStmt, IfStmt, WhileStmt, SkipStmt, SeqStmt
)

class Token:
    def __init__(self, type_, value, line=1, column=1):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, line={self.line}, col={self.column})"


class Lexer:
    TOKEN_SPEC = [
        ('ASSIGN',    r':='),
        ('EQ',        r'=='),
        ('NE',        r'!='),
        ('LE',        r'<='),
        ('GE',        r'>='),
        ('LT',        r'<'),
        ('GT',        r'>'),
        ('SEMICOLON', r';'),
        ('PLUS',      r'\+'),
        ('MINUS',     r'-'),
        ('MUL',       r'\*'),
        ('DIV',       r'/'),
        ('MOD',       r'%'),
        ('LPAREN',    r'\('),
        ('RPAREN',    r'\)'),
        ('NUM',       r'\d+'),
        ('ID',        r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('NEWLINE',   r'\n'),
        ('SKIP_WS',   r'[ \t\r]+'),
        ('MISMATCH',  r'.'),
    ]

    KEYWORDS = {
        'if', 'then', 'else', 'while', 'do', 'end',
        'and', 'or', 'not', 'skip', 'true', 'false'
    }

    VALID_VARS = {'x', 'y', 'z'}

    def __init__(self, text):
        self.text = text
        self.tokens = []

    def tokenize(self):
        regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.TOKEN_SPEC)
        line_num = 1
        line_start = 0
        
        for mo in re.finditer(regex, self.text):
            kind = mo.lastgroup
            value = mo.group(kind)
            column = mo.start() - line_start + 1

            if kind == 'NEWLINE':
                line_num += 1
                line_start = mo.end()
            elif kind == 'SKIP_WS':
                pass
            elif kind == 'MISMATCH':
                raise SyntaxError(f"Unexpected character '{value}' at line {line_num}, column {column}")
            else:
                if kind == 'ID':
                    if value in self.KEYWORDS:
                        kind = value.upper()  # Keyword token type is the uppercase word
                    elif value in self.VALID_VARS:
                        kind = 'VAR'
                    else:
                        raise SyntaxError(
                            f"Invalid identifier '{value}' at line {line_num}, column {column}. "
                            f"Only variables 'x', 'y', and 'z' are allowed."
                        )
                
                self.tokens.append(Token(kind, value, line_num, column))
        
        self.tokens.append(Token('EOF', None, line_num, len(self.text) - line_start + 1))
        return self.tokens


class Parser:
    """
    Grammar:
    
    expr ::= b_expr
    
    b_expr ::= b_term ('OR' b_term)*
    b_term ::= b_factor ('AND' b_factor)*
    b_factor ::= 'NOT' b_factor
               | a_expr compare_op a_expr
               | 'TRUE'
               | 'FALSE'
               | '(' b_expr ')'
               
    compare_op ::= '==' | '!=' | '<' | '<=' | '>' | '>='
    
    a_expr ::= a_term (('PLUS' | 'MINUS') a_term)*
    a_term ::= a_factor (('MUL' | 'DIV' | 'MOD') a_factor)*
    a_factor ::= 'MINUS' a_factor  (unary minus)
               | 'VAR'
               | 'NUM'
               | '(' a_expr ')'
               
    program ::= stmt_list
    stmt_list ::= stmt ('SEMICOLON' stmt)* 'SEMICOLON'?
    stmt ::= 'SKIP'
           | 'VAR' 'ASSIGN' a_expr
           | 'IF' b_expr 'THEN' stmt_list 'ELSE' stmt_list 'END'
           | 'WHILE' b_expr 'DO' stmt_list 'END'
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token('EOF', None)

    def consume(self, token_type):
        tok = self.current_token()
        if tok.type == token_type:
            self.pos += 1
            return tok
        raise SyntaxError(
            f"Expected token {token_type}, but got '{tok.value}' (type: {tok.type}) "
            f"at line {tok.line}, column {tok.column}"
        )

    def match(self, token_type):
        tok = self.current_token()
        if tok.type == token_type:
            self.pos += 1
            return True
        return False

    def parse_expression(self):
        """Parse an expression. Precondition and Postconditions are expressions (typically boolean)."""
        # Try to parse boolean expression. If it is actually a plain arithmetic expression,
        # our parse_b_expr will fall back to compare_expr or fail. 
        # Actually, preconditions and postconditions should evaluate to booleans.
        return self.parse_b_expr()

    # --- Boolean Expressions ---
    def parse_b_expr(self):
        node = self.parse_b_term()
        while self.match('OR'):
            right = self.parse_b_term()
            node = OrExpr(node, right)
        return node

    def parse_b_term(self):
        node = self.parse_b_factor()
        while self.match('AND'):
            right = self.parse_b_factor()
            node = AndExpr(node, right)
        return node

    def parse_b_factor(self):
        tok = self.current_token()
        if self.match('NOT'):
            expr = self.parse_b_factor()
            return NotExpr(expr)
        elif self.match('TRUE'):
            return BoolConst(True)
        elif self.match('FALSE'):
            return BoolConst(False)
        elif tok.type == 'LPAREN':
            # This could be (b_expr) or (a_expr compare_op a_expr).
            # We save self.pos and try to parse b_expr. If it fails or does not consume the whole paren,
            # we reset and parse compare_expr.
            saved_pos = self.pos
            try:
                self.consume('LPAREN')
                node = self.parse_b_expr()
                self.consume('RPAREN')
                return node
            except SyntaxError:
                # Reset and try arithmetic/comparison
                self.pos = saved_pos
        
        # Must be comparison expr: a_expr compare_op a_expr
        left = self.parse_a_expr()
        op_tok = self.current_token()
        if op_tok.type in {'EQ', 'NE', 'LT', 'LE', 'GT', 'GE'}:
            self.pos += 1
            right = self.parse_a_expr()
            return CompareOp(op_tok.value, left, right)
        else:
            # If no comparison operator, and we got here, check if it's just a single arithmetic expression.
            # Technically, in Hoare Logic, preconditions/postconditions are predicates (booleans).
            # If a user provides just 'x', it is a type error (since x is integer).
            # But let's raise a helpful error.
            raise SyntaxError(
                f"Expected comparison operator (==, !=, <, <=, >, >=) after arithmetic expression at line {op_tok.line}, column {op_tok.column}."
            )

    # --- Arithmetic Expressions ---
    def parse_a_expr(self):
        node = self.parse_a_term()
        while True:
            tok = self.current_token()
            if tok.type in {'PLUS', 'MINUS'}:
                self.pos += 1
                right = self.parse_a_term()
                node = BinOp(tok.value, node, right)
            else:
                break
        return node

    def parse_a_term(self):
        node = self.parse_a_factor()
        while True:
            tok = self.current_token()
            if tok.type in {'MUL', 'DIV', 'MOD'}:
                self.pos += 1
                right = self.parse_a_factor()
                node = BinOp(tok.value, node, right)
            else:
                break
        return node

    def parse_a_factor(self):
        tok = self.current_token()
        if self.match('MINUS'):
            factor = self.parse_a_factor()
            # Represent unary minus as 0 - factor
            return BinOp('-', Num(0), factor)
        elif tok.type == 'VAR':
            self.pos += 1
            return Var(tok.value)
        elif tok.type == 'NUM':
            self.pos += 1
            return Num(int(tok.value))
        elif self.match('LPAREN'):
            node = self.parse_a_expr()
            self.consume('RPAREN')
            return node
        else:
            raise SyntaxError(
                f"Unexpected token '{tok.value}' (type: {tok.type}) when parsing arithmetic factor at line {tok.line}, column {tok.column}"
            )

    # --- Statements and Program ---
    def parse_program(self):
        node = self.parse_stmt_list()
        self.consume('EOF')
        return node

    def parse_stmt_list(self):
        stmts = []
        # Parse first statement
        stmts.append(self.parse_stmt())
        
        while self.match('SEMICOLON'):
            # If next is EOF or END or ELSE, semicolon was just a trailing one
            next_tok = self.current_token()
            if next_tok.type in {'EOF', 'END', 'ELSE'}:
                break
            stmts.append(self.parse_stmt())
            
        # Return single statement if only one, otherwise SeqStmt
        if len(stmts) == 1:
            return stmts[0]
        return SeqStmt(stmts)

    def parse_stmt(self):
        tok = self.current_token()
        if self.match('SKIP'):
            return SkipStmt()
        elif tok.type == 'VAR':
            self.pos += 1
            var_name = tok.value
            self.consume('ASSIGN')
            expr = self.parse_a_expr()
            return AssignStmt(var_name, expr)
        elif self.match('IF'):
            cond = self.parse_b_expr()
            self.consume('THEN')
            then_branch = self.parse_stmt_list()
            self.consume('ELSE')
            else_branch = self.parse_stmt_list()
            self.consume('END')
            return IfStmt(cond, then_branch, else_branch)
        elif self.match('WHILE'):
            cond = self.parse_b_expr()
            self.consume('DO')
            body = self.parse_stmt_list()
            self.consume('END')
            return WhileStmt(cond, body)
        else:
            raise SyntaxError(
                f"Unexpected token '{tok.value}' (type: {tok.type}) when parsing statement at line {tok.line}, column {tok.column}. "
                f"Expected 'skip', a variable assignment, 'if', or 'while'."
            )


def parse_expression(text):
    """Parses a boolean/arithmetic expression (pre/postcondition)."""
    lexer = Lexer(text)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    node = parser.parse_expression()
    parser.consume('EOF')
    return node

def parse_program(text):
    """Parses a sequence of statements (program)."""
    lexer = Lexer(text)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse_program()
