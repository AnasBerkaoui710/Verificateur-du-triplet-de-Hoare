# verifier/verifier.py

import time
from verifier.parser import parse_expression, parse_program
from verifier.evaluator import evaluate_expression
from verifier.interpreter import execute_program
from verifier.generator import generate_states

def verify(pre_text, prog_text, post_text, num_tests=100, min_val=-10, max_val=10):
    """
    Verifies the Hoare Triplet {P} C {Q} by:
    1. Parsing P, C, and Q.
    2. Generating test states.
    3. Running the verification loop.
    4. Compiling statistics and counterexamples.
    """
    start_time = time.perf_counter()

    # 1. Parsing
    try:
        pre_ast = parse_expression(pre_text)
    except Exception as e:
        return {
            "success": False,
            "error_type": "Precondition Parsing Error",
            "message": str(e)
        }

    try:
        prog_ast = parse_program(prog_text)
    except Exception as e:
        return {
            "success": False,
            "error_type": "Program Parsing Error",
            "message": str(e)
        }

    try:
        post_ast = parse_expression(post_text)
    except Exception as e:
        return {
            "success": False,
            "error_type": "Postcondition Parsing Error",
            "message": str(e)
        }

    # 2. Generate States
    try:
        initial_states = generate_states(num_tests, min_val, max_val)
    except Exception as e:
        return {
            "success": False,
            "error_type": "Test Generation Error",
            "message": str(e)
        }

    # 3. Verification Loop
    passed_tests = 0
    failed_tests = 0
    ignored_tests = 0
    counterexamples = []

    for state in initial_states:
        # Check Precondition
        try:
            pre_satisfied = evaluate_expression(pre_ast, state)
        except Exception as e:
            # If precondition evaluation fails (e.g. division by zero in precondition),
            # count as ignored or error. Let's record it as a runtime error.
            ignored_tests += 1
            counterexamples.append({
                "initial_state": state,
                "final_state": None,
                "error": f"Precondition evaluation error: {str(e)}",
                "violation": "Precondition Error"
            })
            continue

        if not pre_satisfied:
            ignored_tests += 1
            continue

        # Execute Program
        try:
            # Pass a step limit of 1000 to the interpreter
            final_state = execute_program(prog_ast, state, max_steps=1000)
        except Exception as e:
            failed_tests += 1
            counterexamples.append({
                "initial_state": state,
                "final_state": None,
                "error": f"Execution Error: {str(e)}",
                "violation": "Program Runtime Crash"
            })
            continue

        # Check Postcondition
        try:
            post_satisfied = evaluate_expression(post_ast, final_state)
        except Exception as e:
            failed_tests += 1
            counterexamples.append({
                "initial_state": state,
                "final_state": final_state,
                "error": f"Postcondition evaluation error: {str(e)}",
                "violation": "Postcondition Error"
            })
            continue

        if post_satisfied:
            passed_tests += 1
        else:
            failed_tests += 1
            counterexamples.append({
                "initial_state": state,
                "final_state": final_state,
                "error": None,
                "violation": f"Postcondition {post_text.strip()} holds as False"
            })

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    # Determine validity
    # Valid means: of the tests that satisfied P and executed, 0 failed.
    # Note: If no tests satisfy P, we warn the user in the UI, but logically it's valid.
    valid = (failed_tests == 0)

    return {
        "success": True,
        "valid": valid,
        "total_tests": len(initial_states),
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "ignored_tests": ignored_tests,
        "counterexamples": counterexamples,
        "execution_time": execution_time
    }
