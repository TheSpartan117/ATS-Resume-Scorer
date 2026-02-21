#!/usr/bin/env python3
"""Update registry.py with optimal weights."""
import json
import re

# Load optimal weights
with open('/Users/sabuj.mondal/ats-resume-scorer/optimal_weights.json', 'r') as f:
    optimal_weights = json.load(f)

# Read registry file
with open('/Users/sabuj.mondal/ats-resume-scorer/backend/services/parameters/registry.py', 'r') as f:
    content = f.read()

# Update each parameter's max_score
for param_code, new_weight in optimal_weights.items():
    # Find the parameter block
    pattern = rf"'{param_code}':\s*{{\s*'code':\s*'{param_code}'.*?'max_score':\s*\d+(?:\.\d+)?"

    def replace_score(match):
        text = match.group(0)
        # Replace the max_score value
        updated = re.sub(r"'max_score':\s*\d+(?:\.\d+)?",
                        f"'max_score': {int(new_weight) if new_weight == int(new_weight) else new_weight}",
                        text)
        return updated

    content = re.sub(pattern, replace_score, content, flags=re.DOTALL)

# Write back
with open('/Users/sabuj.mondal/ats-resume-scorer/backend/services/parameters/registry.py', 'w') as f:
    f.write(content)

print("✓ Registry updated with optimal weights")
print("\nUpdated weights:")
for param_code, weight in sorted(optimal_weights.items()):
    print(f"  {param_code}: {weight}")
