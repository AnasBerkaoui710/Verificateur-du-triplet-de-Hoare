# test_verifier.py
import sys
import os

from verifier.parser import parse_expression, parse_program
from verifier.evaluator import evaluate_expression
from verifier.interpreter import execute_program
from verifier.verifier import verify
from verifier.generator import generate_states

def run_tests():
    print("=== Testing Lexer and Parser ===")
    
    # Preconditions / Postconditions (Boolean Expressions)
    expr1 = parse_expression("x >= 0")
    print(f"Parsed 'x >= 0': {expr1}")
    
    expr2 = parse_expression("not (x > 5 and y < 10)")
    print(f"Parsed 'not (x > 5 and y < 10)': {expr2}")
    
    expr3 = parse_expression("x == y or z != 0")
    print(f"Parsed 'x == y or z != 0': {expr3}")
    
    # Program Statements
    prog1 = parse_program("x := x + 1;")
    print(f"Parsed program 1: {prog1}")
    
    prog2 = parse_program("if x > 0 then x := x - 1; y := y + 1 else skip end")
    print(f"Parsed program 2: {prog2}")
    
    prog3 = parse_program("while x < 5 do x := x + 1; z := z - 1 end")
    print(f"Parsed program 3: {prog3}")
    
    print("\n=== Testing Evaluator ===")
    state = {'x': 5, 'y': -2, 'z': 0}
    print(f"State: {state}")
    print(f"Evaluation of 'x >= 0': {evaluate_expression(expr1, state)}")
    print(f"Evaluation of 'not (x > 5 and y < 10)': {evaluate_expression(expr2, state)}")
    
    # Division / Modulo
    expr_div = parse_expression("x / 2 == 2")
    print(f"Evaluation of 'x / 2 == 2' (5/2 == 2): {evaluate_expression(expr_div, state)}")
    
    print("\n=== Testing Interpreter ===")
    print("Executing prog2 (if x > 0 then x := x - 1; y := y + 1 else skip end)...")
    final_state = execute_program(prog2, state)
    print(f"Initial: {state} | Final: {final_state}")
    
    print("Executing infinite loop test (should fail safety check)...")
    loop_prog = parse_program("while true do skip end")
    try:
        execute_program(loop_prog, state, max_steps=100)
        print("FAIL: Loop did not abort!")
    except RuntimeError as e:
        print(f"SUCCESS: Aborted infinite loop. Error message: {e}")
        
    print("\n=== Testing Generator ===")
    states = generate_states(num_tests=15, min_val=-3, max_val=3)
    print(f"Generated {len(states)} states. First 5: {states[:5]}")
    
    print("\n=== Testing Verifier Coordinator ===")
    # Valid triplet: {x >= 0} x := x + 1; {x > 0}
    res1 = verify("x >= 0", "x := x + 1;", "x > 0", num_tests=50, min_val=-10, max_val=10)
    print(f"Triplet 1 (Valid): Success={res1['success']}, Valid={res1.get('valid')}, Total={res1.get('total_tests')}, Passed={res1.get('passed_tests')}, Failed={res1.get('failed_tests')}, Ignored={res1.get('ignored_tests')}")
    
    # Invalid triplet: {x > 5} x := x - 10; {x > 0}
    res2 = verify("x > 5", "x := x - 10;", "x > 0", num_tests=50, min_val=-10, max_val=10)
    print(f"Triplet 2 (Invalid): Success={res2['success']}, Valid={res2.get('valid')}, Failed (Counterexamples)={res2.get('failed_tests')}")
    if res2.get('counterexamples'):
        print(f"Sample Counterexample: {res2['counterexamples'][0]}")

if __name__ == "__main__":
    run_tests()
