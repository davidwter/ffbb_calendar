# FFBB Calendar

Generates ICS calendar files from FFBB (French Basketball Federation) match schedules.

## Calendars

Subscribe to these URLs in Google Calendar (Settings → Add calendar → From URL):

| Team | URL |
|------|-----|
| U15F | https://davidwter.github.io/ffbb_calendar/U15F.ics |
| U18F | https://davidwter.github.io/ffbb_calendar/U18F.ics |
| SeniorF1 | https://davidwter.github.io/ffbb_calendar/SeniorF1.ics |
| SeniorF2 | https://davidwter.github.io/ffbb_calendar/SeniorF2.ics |
| SeniorG1 | https://davidwter.github.io/ffbb_calendar/SeniorG1.ics |

Calendars are updated automatically every night at 3 AM UTC via GitHub Actions.

## Features

- Scrapes match schedules from competitions.ffbb.com
- Fetches correct times from match detail pages
- Includes venue name and address as event location
- Events prefixed with team name (e.g., "U15F - Team A vs Team B")
- Europe/Paris timezone

## Local Usage

```bash
pip install -r requirements.txt
python main.py <team_url>
```

## Adding a New Team

Edit `generate.py` and add a new entry to the `TEAMS` list:

```python
TEAMS = [
    ("https://competitions.ffbb.com/.../equipes/...", "TeamName"),
]
```

Push to trigger the GitHub Actions workflow, or wait for the nightly update.
