"""
verify_app.py - Automated Unit Tests for Calculator Backend

This script contains automated tests to verify that the mathematical evaluation engine in `app.py` 
works correctly, securely, and behaves as expected under different scenarios.

To run these tests:
    python verify_app.py
"""

from app import evaluate_expression

def run_tests():
    print("==================================================")
    print(" Running Automated Mathematical Engine Tests...   ")
    print("==================================================")

    test_cases = [
        # Format: (test_name, input_expression, expected_output_or_exception)
        
        # 1. Basic Operations
        ("Basic Addition", "15 + 27", 42),
        ("Basic Subtraction", "100 - 45", 55),
        ("Basic Multiplication", "12 * 8", 96),
        ("Basic Division", "81 / 9", 9.0),
        
        # 2. Operator Precedence (Order of Operations: PEMDAS/MDAS)
        ("Operator Precedence 1", "2 + 3 * 4", 14),
        ("Operator Precedence 2", "10 * 5 - 20 / 4", 45),
        
        # 3. Parentheses nesting
        ("Parentheses Override", "(2 + 3) * 4", 20),
        ("Complex Parentheses", "((10 - 2) * (5 + 5)) / 2", 40.0),
        
        # 4. Decimals and Float precision checks
        ("Decimal Addition", "0.1 + 0.2", 0.3),  # Verifies our rounding handles standard binary-float issues
        ("Decimal Multiplication", "2.5 * 1.5", 3.75),
        
        # 5. Unary positive/negative numbers
        ("Unary Minus", "-5 + 15", 10),
        ("Chained Unary Minus", "10 - -5", 15),
        ("Unary Plus", "+8 * 2", 16),
        
        # 6. Large numbers
        ("Large Numbers", "1000000 + 2000000", 3000000),
    ]

    passed_count = 0

    for name, expr, expected in test_cases:
        try:
            result = evaluate_expression(expr)
            if result == expected:
                print(f"[PASS] {name}: '{expr}' evaluated to {result}")
                passed_count += 1
            else:
                print(f"[FAIL] {name}: '{expr}' evaluated to {result}, but expected {expected}")
        except Exception as e:
            print(f"[FAIL] {name}: '{expr}' raised an unexpected exception: {e}")

    # 7. Error Handling Assertions (Expecting specific errors)
    print("\nVerifying Error and Exception Handling...")
    
    # Check Division by Zero
    try:
        evaluate_expression("100 / 0")
        print("[FAIL] Division by Zero: Allowed division by zero without raising an exception.")
    except ZeroDivisionError:
        print("[PASS] Division by Zero: Correctly threw ZeroDivisionError on '100 / 0'")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] Division by Zero: Threw unexpected exception {type(e).__name__} instead of ZeroDivisionError")

    # Check Invalid Input / Script Injection Prevention
    invalid_inputs = [
        "2 + abc",           # Alphabetic characters (Variables)
        "import os",          # Python system injection
        "eval('5+5')",       # Function calling
        "2 + ;",             # Syntax corruption
        "2 ** 3",            # Exponentiation (not supported in our whitelist)
    ]

    for index, bad_input in enumerate(invalid_inputs, start=1):
        try:
            evaluate_expression(bad_input)
            print(f"[FAIL] Security Guard #{index}: Allowed invalid expression '{bad_input}' to evaluate.")
        except ValueError:
            print(f"[PASS] Security Guard #{index}: Correctly blocked invalid input '{bad_input}' with ValueError")
            passed_count += 1
        except Exception as e:
            print(f"[FAIL] Security Guard #{index}: Raised wrong exception '{type(e).__name__}' on '{bad_input}'")

    print("==================================================")
    total_runs = len(test_cases) + 1 + len(invalid_inputs)
    print(f" Test Results: {passed_count}/{total_runs} Tests Passed successfully.")
    print("==================================================")
    
    if passed_count == total_runs:
        print(" All systems operational. Safe to deploy! [SUCCESS]")
        return True
    else:
        print(" Some tests failed. Please inspect the evaluation script. [FAILED]")
        return False

if __name__ == "__main__":
    run_tests()
