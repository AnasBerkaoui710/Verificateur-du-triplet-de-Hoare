# verifier/evaluator.py

from verifier.ast import (
    Var, Num, BinOp, BoolConst, CompareOp, AndExpr, OrExpr, NotExpr
)

class Evaluator:
    def __init__(self, state):
        """
        state: dict mapping 'x', 'y', 'z' to their integer values.
        """
        self.state = state

    def evaluate(self, node):
        if isinstance(node, Var):
            # Default value to 0 if not found, though we should always have x, y, z in the state.
            return self.state.get(node.name, 0)
        
        elif isinstance(node, Num):
            return node.val
        
        elif isinstance(node, BinOp):
            left_val = self.evaluate(node.left)
            right_val = self.evaluate(node.right)
            
            if node.op == '+':
                return left_val + right_val
            elif node.op == '-':
                return left_val - right_val
            elif node.op == '*':
                return left_val * right_val
            elif node.op == '/':
                if right_val == 0:
                    raise ZeroDivisionError("Division by zero in expression evaluation.")
                # We perform integer division to keep values in integer domain for verification
                return left_val // right_val
            elif node.op == '%':
                if right_val == 0:
                    raise ZeroDivisionError("Modulo by zero in expression evaluation.")
                return left_val % right_val
            else:
                raise ValueError(f"Unknown arithmetic operator: {node.op}")
        
        elif isinstance(node, BoolConst):
            return node.val
        
        elif isinstance(node, CompareOp):
            left_val = self.evaluate(node.left)
            right_val = self.evaluate(node.right)
            
            if node.op == '==':
                return left_val == right_val
            elif node.op == '!=':
                return left_val != right_val
            elif node.op == '<':
                return left_val < right_val
            elif node.op == '<=':
                return left_val <= right_val
            elif node.op == '>':
                return left_val > right_val
            elif node.op == '>=':
                return left_val >= right_val
            else:
                raise ValueError(f"Unknown comparison operator: {node.op}")
        
        elif isinstance(node, AndExpr):
            # Short-circuiting evaluation
            left_val = self.evaluate(node.left)
            if not left_val:
                return False
            return bool(self.evaluate(node.right))
        
        elif isinstance(node, OrExpr):
            # Short-circuiting evaluation
            left_val = self.evaluate(node.left)
            if left_val:
                return True
            return bool(self.evaluate(node.right))
        
        elif isinstance(node, NotExpr):
            val = self.evaluate(node.expr)
            return not val
        
        else:
            raise TypeError(f"Unknown AST node type for evaluation: {type(node).__name__}")


def evaluate_expression(node, state):
    """Convenience function to evaluate expression or condition under a state."""
    evaluator = Evaluator(state)
    return evaluator.evaluate(node)
