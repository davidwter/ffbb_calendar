#!/usr/bin/env python3
"""Non-interactive script for CI - generates ICS from configured URLs."""

from scraper import fetch_matches
from calendar_generator import create_calendar

# Teams configuration: (URL, calendar_name)
TEAMS = [
    ("https://competitions.ffbb.com/ligues/naq/comites/0033/clubs/naq0033048/equipes/200000005210924", "U15F"),
    ("https://competitions.ffbb.com/ligues/naq/comites/0033/clubs/naq0033048/equipes/200000005145377", "SeniorF1"),
    ("https://competitions.ffbb.com/ligues/naq/comites/0033/clubs/naq0033048/equipes/200000005179764", "SeniorF2"),
    ("https://competitions.ffbb.com/ligues/naq/comites/0033/clubs/naq0033048/equipes/200000005209182", "U18F"),
    ("https://competitions.ffbb.com/ligues/naq/comites/0033/clubs/naq0033048/equipes/200000005145508", "SeniorG1"),
]


def generate_calendar(url, name):
    """Generate a single calendar file."""
    print(f"\n=== Generating {name} ===")
    matches = fetch_matches(url)

    if not matches:
        print(f"No matches found for {name}!")
        return

    matches.sort(key=lambda x: x['start_time'])
    ics_content = create_calendar(matches, name)

    output_file = f"{name}.ics"
    with open(output_file, "w") as f:
        f.write(ics_content)

    print(f"Generated {output_file} with {len(matches)} matches")


def main():
    for url, name in TEAMS:
        generate_calendar(url, name)


if __name__ == "__main__":
    main()
