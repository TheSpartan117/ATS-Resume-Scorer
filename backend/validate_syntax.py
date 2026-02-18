#!/usr/bin/env python3
"""
Validate syntax of scorer_v2.py by importing it.
"""

import sys
import ast

def validate_syntax(filepath):
    """Validate Python syntax by parsing AST"""
    try:
        with open(filepath, 'r') as f:
            code = f.read()

        # Try to parse the code
        ast.parse(code)
        print(f"✓ {filepath} - Syntax is valid")
        return True
    except SyntaxError as e:
        print(f"✗ {filepath} - Syntax error: {e}")
        return False
    except Exception as e:
        print(f"✗ {filepath} - Error: {e}")
        return False

if __name__ == "__main__":
    files = [
        "/Users/sabuj.mondal/ats-resume-scorer/backend/services/scorer_v2.py",
        "/Users/sabuj.mondal/ats-resume-scorer/backend/tests/test_scorer_v2.py"
    ]

    all_valid = True
    for filepath in files:
        if not validate_syntax(filepath):
            all_valid = False

    if all_valid:
        print("\n✓ All files have valid syntax")
        sys.exit(0)
    else:
        print("\n✗ Some files have syntax errors")
        sys.exit(1)
