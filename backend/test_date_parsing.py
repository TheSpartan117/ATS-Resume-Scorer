#!/usr/bin/env python3
"""Test date parsing logic"""

from services.parameters.p5_2_career_recency import CareerRecencyScorer

scorer = CareerRecencyScorer()

test_cases = [
    "2020-01 - Present",
    "2020 - Present",
    "Jan 2020 - Present",
    "January 2020 - Present",
    "2020-01 - 2021-12",
    "Jan 2020 - Dec 2021",
    "2015 - 2018",
]

print("Testing date range extraction:")
print("=" * 60)

for date_range in test_cases:
    start, end = scorer._extract_dates_from_range(date_range)
    print(f"Input:  '{date_range}'")
    print(f"Start:  '{start}'")
    print(f"End:    '{end}'")
    print(f"Parsed start: {scorer._parse_date(start)}")
    print(f"Parsed end:   {scorer._parse_date(end)}")
    print("-" * 60)
