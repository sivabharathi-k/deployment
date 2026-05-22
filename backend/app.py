"""
app.py - Calculator Web Application Backend (API Only)

Frontend is deployed on Vercel.
This backend only handles the /calculate API endpoint.
CORS is enabled so Vercel frontend can call this Render backend.
"""

import ast
import operator
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Allow requests from ANY origin (Vercel frontend)
# To restrict: CORS(app, origins=["https://your-app.vercel.app"])
CORS(app)

ALLOWED_OPERATORS = {
    ast.Add:  operator.add,
    ast.Sub:  operator.sub,
    ast.Mult: operator.mul,
    ast.Div:  operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_eval(node):
    if isinstance(node, ast.Expression):
        return safe_eval(node.body)

    elif isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numeric constants are allowed.")

    elif isinstance(node, ast.Num):
        return node.n

    elif isinstance(node, ast.BinOp):
        left_val  = safe_eval(node.left)
        right_val = safe_eval(node.right)
        op_type   = type(node.op)
        if op_type in ALLOWED_OPERATORS:
            if op_type == ast.Div and right_val == 0:
                raise ZeroDivisionError("Cannot divide by zero.")
            return ALLOWED_OPERATORS[op_type](left_val, right_val)
        raise ValueError(f"Operator '{op_type.__name__}' is not supported.")

    elif isinstance(node, ast.UnaryOp):
        operand_val = safe_eval(node.operand)
        op_type     = type(node.op)
        if op_type in ALLOWED_OPERATORS:
            return ALLOWED_OPERATORS[op_type](operand_val)
        raise ValueError(f"Unary operator '{op_type.__name__}' is not supported.")

    else:
        raise ValueError("Invalid mathematical syntax.")


def evaluate_expression(expression_str):
    expr = expression_str.strip()
    if not expr:
        raise ValueError("Expression is empty.")

    if not re.match(r'^[0-9.+\-*/()\s]+$', expr):
        raise ValueError("Expression contains invalid characters.")

    try:
        tree   = ast.parse(expr, mode='eval')
        result = safe_eval(tree)

        if isinstance(result, float):
            result = round(result, 10)
            if result.is_integer():
                result = int(result)

        return result
    except (SyntaxError, TypeError):
        raise ValueError("Malformed expression syntax.")


# --- API ROUTES ---

@app.route('/')
def health():
    """Health check — confirms the backend is running on Render."""
    return jsonify({'status': 'ok', 'message': 'QuantumCalc backend is running.'})


@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()

    if not data or 'expression' not in data:
        return jsonify({'status': 'error', 'message': 'No expression provided.'}), 400

    expression = data['expression']
    print(f"[API] Received: {expression}")

    try:
        result = evaluate_expression(expression)
        print(f"[API] Result: {expression} = {result}")
        return jsonify({'status': 'success', 'result': result})

    except ZeroDivisionError:
        return jsonify({'status': 'error', 'message': 'Error: Division by zero'})

    except ValueError as val_err:
        return jsonify({'status': 'error', 'message': str(val_err)})

    except Exception as e:
        print(f"[API] Unexpected error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Invalid Input'})


if __name__ == '__main__':
    print("--------------------------------------------------")
    print("   QuantumCalc Backend running...                 ")
    print("   Local:  http://127.0.0.1:5000/                 ")
    print("   Routes: GET /  |  POST /calculate              ")
    print("--------------------------------------------------")
    app.run(debug=True)
