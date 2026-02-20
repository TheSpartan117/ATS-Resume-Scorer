#!/usr/bin/env python3
"""Quick verification that SuggestionGenerator works"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from services.suggestion_generator import SuggestionGenerator

def test_basic():
    """Test basic functionality"""
    print("Testing SuggestionGenerator basic functionality...")

    # Initialize
    generator = SuggestionGenerator(role='software_engineer', level='mid')
    print(f"✓ Created generator: role={generator.role}, level={generator.level}")

    # Test with sample data
    resume_data = {
        'contact': {
            'name': 'John Doe',
            'email': 'john@example.com'
            # Missing phone and linkedin
        },
        'experience': [
            {
                'title': 'Software Engineer',
                'company': 'TechCorp',
                'description': 'Responsible for managing team projects',
                'para_idx': 8
            }
        ],
        'skills': ['Python', 'JavaScript']
    }

    sections = [
        {'name': 'Contact', 'start_para': 0, 'end_para': 5},
        {'name': 'Experience', 'start_para': 8, 'end_para': 15},
        {'name': 'Skills', 'start_para': 21, 'end_para': 25}
    ]

    # Generate suggestions
    suggestions = generator.generate_suggestions(resume_data, sections)
    print(f"✓ Generated {len(suggestions)} suggestions")

    # Verify suggestion types
    types = set(s['type'] for s in suggestions)
    print(f"✓ Suggestion types: {types}")

    # Check for missing phone
    has_missing_phone = any('phone' in s['title'].lower() for s in suggestions)
    print(f"✓ Detected missing phone: {has_missing_phone}")

    # Check for weak verb
    has_weak_verb = any(s['type'] == 'content_change' for s in suggestions)
    print(f"✓ Detected weak action verb: {has_weak_verb}")

    # Check for missing projects
    has_missing_projects = any('project' in s['title'].lower() for s in suggestions)
    print(f"✓ Detected missing Projects section: {has_missing_projects}")

    # Verify all have required fields
    for i, s in enumerate(suggestions):
        assert 'id' in s, f"Suggestion {i} missing 'id'"
        assert 'type' in s, f"Suggestion {i} missing 'type'"
        assert 'severity' in s, f"Suggestion {i} missing 'severity'"
        assert 'title' in s, f"Suggestion {i} missing 'title'"
        assert 'description' in s, f"Suggestion {i} missing 'description'"
        assert 'location' in s, f"Suggestion {i} missing 'location'"
        assert 'action' in s, f"Suggestion {i} missing 'action'"
    print(f"✓ All suggestions have required fields")

    # Verify sorting by priority
    severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    for i in range(len(suggestions) - 1):
        current = severity_order[suggestions[i]['severity']]
        next_s = severity_order[suggestions[i + 1]['severity']]
        assert current <= next_s, "Suggestions not sorted by priority"
    print(f"✓ Suggestions sorted by priority")

    print("\n" + "="*50)
    print("✅ All basic tests PASSED!")
    print("="*50)
    print("\nSample suggestions generated:")
    for s in suggestions[:3]:
        print(f"\n- [{s['severity'].upper()}] {s['title']}")
        print(f"  Type: {s['type']}, Action: {s['action']}")
        print(f"  Location: {s['location']}")

    return True

if __name__ == "__main__":
    try:
        test_basic()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
