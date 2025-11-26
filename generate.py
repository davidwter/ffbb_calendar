#!/usr/bin/env python3
"""Non-interactive script for CI - generates ICS from configured URLs."""

from scraper import fetch_matches
from calendar_generator import create_calendar

# Add your team URLs here
TEAM_URLS = [
    "https://competitions.ffbb.com/ligues/naq/comites/0033/clubs/naq0033048/equipes/200000005210924",
]

CALENDAR_NAME = "U15F"
OUTPUT_FILE = "calendar.ics"


def main():
    all_matches = []

    for url in TEAM_URLS:
        matches = fetch_matches(url)
        all_matches.extend(matches)
        print(f"Found {len(matches)} matches from {url}")

    if not all_matches:
        print("No matches found!")
        return

    # Remove duplicates based on start_time and teams
    seen = set()
    unique_matches = []
    for m in all_matches:
        key = (m['start_time'], m['home_team'], m['away_team'])
        if key not in seen:
            seen.add(key)
            unique_matches.append(m)

    # Sort by date
    unique_matches.sort(key=lambda x: x['start_time'])

    ics_content = create_calendar(unique_matches, CALENDAR_NAME)

    with open(OUTPUT_FILE, "w") as f:
        f.write(ics_content)

    print(f"Generated {OUTPUT_FILE} with {len(unique_matches)} matches")


if __name__ == "__main__":
    main()
