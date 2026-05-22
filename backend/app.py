"""
app.py - Calculator Web Application Backend

This Python script is the backend of our Calculator Web Application.
It uses the Flask web framework to:
1. Serve the frontend HTML page.
2. Provide a safe API endpoint ('/calculate') that processes arithmetic expressions
   sent from the frontend, evaluates them, and returns a JSON response.

Security Note:
We avoid using Python's built-in `eval()` function because it can execute arbitrary,
potentially harmful code. Instead, we use the `ast` (Abstract Syntax Tree) module
to parse and evaluate only safe mathematical operations.
"""

import ast
import operator
import re
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Build absolute paths to the frontend folders so Flask can locate them
# regardless of which directory the script is run from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # .../web_app/backend
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')  # .../web_app/frontend

app = Flask(
    __name__,
    template_folder=os.path.join(FRONTEND_DIR, 'templates'),
    static_folder=os.path.join(FRONTEND_DIR, 'static')
)
CORS(app)  # Allow requests from separate frontend domain

# Define a mapping of AST operator nodes to actual Python operator functions.
# This strictly defines which operators are allowed in our calculator.
ALLOWED_OPERATORS = {
    ast.Add: operator.add,       # Addition (+)
    ast.Sub: operator.sub,       # Subtraction (-)
    ast.Mult: operator.mul,      # Multiplication (*)
    ast.Div: operator.truediv,   # Division (/)
    ast.USub: operator.neg,      # Unary minus (e.g., -5)
    ast.UAdd: operator.pos,      # Unary plus (e.g., +5)
}

def safe_eval(node):
    """
    Recursively evaluate nodes in the Abstract Syntax Tree (AST).
    Only allowed numeric, binary, and unary operators will be processed.
    """
    # 1. Base Expression: The wrapper node for the parsed expression
    if isinstance(node, ast.Expression):
        return safe_eval(node.body)

    # 2. Constant Values (Python 3.8+): Represents actual numbers (integers or floats)
    elif isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numeric constants are allowed.")

    # 3. Numbers (Older Python compatibility): Fallback for older versions
    elif isinstance(node, ast.Num):
        return node.n

    # 4. Binary Operations: e.g., 5 + 3
    elif isinstance(node, ast.BinOp):
        left_val = safe_eval(node.left)
        right_val = safe_eval(node.right)
        operator_type = type(node.op)

        if operator_type in ALLOWED_OPERATORS:
            if operator_type == ast.Div and right_val == 0:
                raise ZeroDivisionError("Cannot divide by zero.")
            return ALLOWED_OPERATORS[operator_type](left_val, right_val)

        raise ValueError(f"Operator '{operator_type.__name__}' is not supported.")

    # 5. Unary Operations: e.g., -5
    elif isinstance(node, ast.UnaryOp):
        operand_val = safe_eval(node.operand)
        operator_type = type(node.op)

        if operator_type in ALLOWED_OPERATORS:
            return ALLOWED_OPERATORS[operator_type](operand_val)

        raise ValueError(f"Unary operator '{operator_type.__name__}' is not supported.")

    # 6. Reject everything else (variables, function calls, imports, etc.)
    else:
        raise ValueError("Invalid mathematical syntax.")


def evaluate_expression(expression_str):
    """
    Validates the input string and safely evaluates it as a mathematical expression.
    """
    expr = expression_str.strip()
    if not expr:
        raise ValueError("Expression is empty.")

    # Allow only digits, decimal points, operators, parentheses, and spaces
    if not re.match(r'^[0-9.+\-*/()\s]+$', expr):
        raise ValueError("Expression contains invalid characters.")

    try:
        tree = ast.parse(expr, mode='eval')
        result = safe_eval(tree)

        if isinstance(result, float):
            result = round(result, 10)
            if result.is_integer():
                result = int(result)

        return result
    except (SyntaxError, TypeError):
        raise ValueError("Malformed expression syntax.")


# --- FLASK WEB ROUTES ---

@app.route('/')
def home():
    """Renders the main calculator page from frontend/templates/index.html."""
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    """
    API endpoint that receives a JSON payload with an 'expression' key,
    evaluates it securely, and returns a JSON response with the result.
    """
    data = request.get_json()

    if not data or 'expression' not in data:
        return jsonify({'status': 'error', 'message': 'No expression provided.'}), 400

    expression = data['expression']
    print(f"[API] Received calculation request: {expression}")

    try:
        result = evaluate_expression(expression)
        print(f"[API] Calculation Success: {expression} = {result}")
        return jsonify({'status': 'success', 'result': result})

    except ZeroDivisionError:
        print(f"[API] Calculation Error: Division by zero in '{expression}'")
        return jsonify({'status': 'error', 'message': 'Error: Division by zero'})

    except ValueError as val_err:
        print(f"[API] Calculation Error: {val_err} in '{expression}'")
        return jsonify({'status': 'error', 'message': str(val_err)})

    except Exception as e:
        print(f"[API] Unexpected Calculation Error: {str(e)} in '{expression}'")
        return jsonify({'status': 'error', 'message': 'Invalid Input'})


if __name__ == '__main__':
    print("--------------------------------------------------")
    print("   Starting Modern Flask Calculator Backend...    ")
    print("   Access it here: http://127.0.0.1:5000/         ")
    print("--------------------------------------------------")
    app.run(debug=True)
