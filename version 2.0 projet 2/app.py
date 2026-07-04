# app.py

import os
from flask import Flask, render_template, request, jsonify
from verifier.verifier import verify
from verifier.utils import format_state, format_time

app = Flask(__name__)

# Route to serve the main dashboard page
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to run verification
@app.route('/verify', methods=['POST'])
def run_verification():
    try:
        data = request.get_json() or {}
        
        precondition = data.get('precondition', '').strip()
        program = data.get('program', '').strip()
        postcondition = data.get('postcondition', '').strip()
        
        # Parse control panel parameters
        try:
            num_tests = int(data.get('num_tests', 100))
        except (ValueError, TypeError):
            num_tests = 100

        try:
            min_val = int(data.get('min_val', -10))
        except (ValueError, TypeError):
            min_val = -10

        try:
            max_val = int(data.get('max_val', 10))
        except (ValueError, TypeError):
            max_val = 10

        # Validate basic parameters
        if not precondition:
            return jsonify({
                "success": False,
                "error_type": "Validation Error",
                "message": "Precondition cannot be empty."
            }), 400

        if not program:
            return jsonify({
                "success": False,
                "error_type": "Validation Error",
                "message": "Program cannot be empty."
            }), 400

        if not postcondition:
            return jsonify({
                "success": False,
                "error_type": "Validation Error",
                "message": "Postcondition cannot be empty."
            }), 400

        if min_val > max_val:
            return jsonify({
                "success": False,
                "error_type": "Validation Error",
                "message": "Minimum value cannot be greater than maximum value."
            }), 400

        if num_tests <= 0 or num_tests > 10000:
            return jsonify({
                "success": False,
                "error_type": "Validation Error",
                "message": "Number of tests must be between 1 and 10,000."
            }), 400

        # Execute verification
        result = verify(
            precondition, 
            program, 
            postcondition, 
            num_tests=num_tests, 
            min_val=min_val, 
            max_val=max_val
        )

        if not result.get('success', False):
            # Parsing or configuration errors on backend
            return jsonify(result), 200

        # Format raw states for easy displaying on front-end
        formatted_counterexamples = []
        for ce in result.get('counterexamples', []):
            formatted_counterexamples.append({
                "initial_state": format_state(ce["initial_state"]),
                "final_state": format_state(ce["final_state"]) if ce["final_state"] is not None else None,
                "error": ce["error"],
                "violation": ce["violation"]
            })

        response_data = {
            "success": True,
            "valid": result["valid"],
            "total_tests": result["total_tests"],
            "passed_tests": result["passed_tests"],
            "failed_tests": result["failed_tests"],
            "ignored_tests": result["ignored_tests"],
            "counterexamples": formatted_counterexamples,
            "execution_time_raw": result["execution_time"],
            "execution_time_str": format_time(result["execution_time"])
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error_type": "Internal Server Error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
