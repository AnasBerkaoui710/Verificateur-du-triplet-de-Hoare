
# verifier/interpreter.py

from verifier.ast import (
    AssignStmt, IfStmt, WhileStmt, SkipStmt, SeqStmt
)
from verifier.evaluator import evaluate_expression

class Interpreter:
    def __init__(self, max_steps=1000):
        self.max_steps = max_steps
        self.steps = 0

    def execute(self, stmt, initial_state):
        """
        Executes the AST statement on a copy of the initial state.
        Returns the final state.
        Raises RuntimeError on infinite loop or execution limit overrun.
        """
        self.steps = 0
        state = dict(initial_state)
        self._run(stmt, state)
        return state

    def _run(self, stmt, state):
        self.steps += 1
        if self.steps > self.max_steps:
            raise RuntimeError(
                f"Program execution exceeded limit of {self.max_steps} steps. "
                f"Possible infinite loop detected."
            )

        if isinstance(stmt, SkipStmt):
            pass

        elif isinstance(stmt, AssignStmt):
            val = evaluate_expression(stmt.expr, state)
            state[stmt.var_name] = val

        elif isinstance(stmt, IfStmt):
            cond_val = evaluate_expression(stmt.cond, state)
            if cond_val:
                self._run(stmt.then_branch, state)
            else:
                self._run(stmt.else_branch, state)

        elif isinstance(stmt, WhileStmt):
            # Check loop condition. Each check is a step.
            while True:
                self.steps += 1
                if self.steps > self.max_steps:
                    raise RuntimeError(
                        f"Program execution exceeded limit of {self.max_steps} steps. "
                        f"Possible infinite loop detected in while loop."
                    )
                
                cond_val = evaluate_expression(stmt.cond, state)
                if not cond_val:
                    break
                self._run(stmt.body, state)

        elif isinstance(stmt, SeqStmt):
            for s in stmt.statements:
                self._run(s, state)
        
        else:
            raise TypeError(f"Unknown statement AST node: {type(stmt).__name__}")


def execute_program(stmt, initial_state, max_steps=1000):
    """Convenience function to interpret program statements."""
    interpreter = Interpreter(max_steps)
    return interpreter.execute(stmt, initial_state)
