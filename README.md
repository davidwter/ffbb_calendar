# FFBB Calendar

Generates ICS calendar files from FFBB (French Basketball Federation) match schedules.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py <team_url>
```

Example:
```bash
python main.py "https://competitions.ffbb.com/ligues/naq/comites/0033/clubs/naq0033048/equipes/200000005210924"
```

The script will prompt you to create a new calendar or update an existing one.

## Features

- Scrapes match schedules from competitions.ffbb.com
- Fetches correct times from match detail pages
- Generates ICS files with Europe/Paris timezone
- Supports both home and away matches
