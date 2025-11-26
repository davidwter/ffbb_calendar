import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import sys

# Month mapping for French dates
MONTHS = {
    "janv.": 1, "févr.": 2, "mars": 3, "avr.": 4, "mai": 5, "juin": 6,
    "juil.": 7, "août": 8, "sept.": 9, "oct.": 10, "nov.": 11, "déc.": 12,
    # Full names just in case
    "janvier": 1, "février": 2, "avril": 4, "juillet": 7, "novembre": 11, "décembre": 12
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
}

def parse_french_date(date_str):
    """
    Parses a date string like '8 nov. 19h30' into a datetime object.
    Assumes the current or relevant season year.
    """
    # Clean string
    date_str = date_str.strip()
    
    # Regex to extract parts: Day, Month, Time
    # Example: "8 nov. 19h30" -> 8, nov., 19, 30
    match = re.search(r"(\d+)\s+([a-zéû\.]+)\s+(\d+)h(\d+)", date_str, re.IGNORECASE)
    if not match:
        return None
        
    day, month_str, hour, minute = match.groups()
    
    month = MONTHS.get(month_str.lower())
    if not month:
        print(f"Warning: Unknown month '{month_str}'")
        return None
        
    # Determine year
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    # Basketball season: Sept -> June
    if current_month >= 9:
        season_start_year = current_year
    else:
        season_start_year = current_year - 1
        
    if month >= 9:
        year = season_start_year
    else:
        year = season_start_year + 1
        
    import pytz
    
    try:
        dt = datetime(year, int(month), int(day), int(hour), int(minute))
        # Localize to Paris time (assuming the HTML contains the correct local time, e.g. 18h30)
        paris_tz = pytz.timezone('Europe/Paris')
        localized_dt = paris_tz.localize(dt)
        return localized_dt
    except ValueError as e:
        print(f"Error creating date: {e}")
        return None

def fetch_match_details(match_url):
    """
    Fetches match details from the match detail page:
    - Correct time (team listing page sometimes shows incorrect times)
    - Venue name and address
    """
    details = {'start_time': None, 'location': None}
    try:
        response = requests.get(match_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        html = response.text

        # Extract time
        text = soup.get_text()
        match = re.search(r"(\d+)\s+([a-zéû\.]+)\s+(\d+)h(\d+)", text, re.IGNORECASE)
        if match:
            details['start_time'] = parse_french_date(f"{match.group(1)} {match.group(2)} {match.group(3)}h{match.group(4)}")

        # Extract venue name
        nom_match = re.search(r'Nom</span>.*?whitespace-nowrap"?>([^<]+)</span>', html)
        venue_name = nom_match.group(1).strip() if nom_match else None

        # Extract address
        addr_match = re.search(r'Adresse</span>.*?whitespace-nowrap"?>([^<]+)</span>', html)
        address = addr_match.group(1).strip() if addr_match else None

        # Combine venue name and address
        if venue_name and address:
            details['location'] = f"{venue_name}, {address}"
        elif venue_name:
            details['location'] = venue_name
        elif address:
            details['location'] = address

    except Exception as e:
        print(f"Warning: Could not fetch match details from {match_url}: {e}")
    return details


def fetch_matches(url):
    """
    Fetches and parses matches from the given URL.
    """
    print(f"Fetching data from {url}...")

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return []
        
    soup = BeautifulSoup(response.text, 'html.parser')
    matches = []
    
    # 1. Identify Subject Team
    h1 = soup.find('h1')
    if h1:
        subject_team = h1.get_text(strip=True)
    else:
        print("Warning: Could not find Subject Team (H1). Using 'Unknown Team'.")
        subject_team = "Unknown Team"
        
    print(f"Subject Team: {subject_team}")
    
    # 2. Find matches
    match_links = soup.select("a[href*='/match/']")
    print(f"Found {len(match_links)} potential matches.")
    
    for link in match_links:
        container = link.find_parent('div', class_=lambda c: c and 'bg-white' in c and 'border-b' in c)
        if not container:
            continue
            
        # Extract Date and Location
        # Location is usually "Domicile" or "Extérieur" in the first column
        col1 = container.find('div', class_=lambda c: c and 'w-[260px]' in c)
        if not col1:
            continue
            
        col1_text = col1.get_text(separator=' ', strip=True)
        
        # Parse Date
        start_time = parse_french_date(col1_text)
        if not start_time:
            continue
            
        # Determine Location
        if "Domicile" in col1_text:
            is_home = True
        elif "Extérieur" in col1_text or "Exterieur" in col1_text:
            is_home = False
        else:
            # Default to Home if unknown? Or log warning?
            # Let's assume Home if not specified, but print warning
            print(f"Warning: Could not determine location from '{col1_text}'. Assuming Home.")
            is_home = True
            
        # Extract Opponent
        opponent_div = container.select_one("div[class*='line-clamp-2']")
        if opponent_div:
            opponent_team = opponent_div.get_text(strip=True)
        else:
            print(f"Warning: Could not find opponent for match on {start_time}")
            continue
            
        # Assign Home/Away
        if is_home:
            home_team = subject_team
            away_team = opponent_team
        else:
            home_team = opponent_team
            away_team = subject_team

        match_url = "https://competitions.ffbb.com" + link['href'] if link['href'].startswith('/') else link['href']

        # Fetch details from match detail page (time, venue)
        print(f"  Fetching details for {home_team} vs {away_team}...")
        details = fetch_match_details(match_url)
        if details['start_time']:
            start_time = details['start_time']

        matches.append({
            "home_team": home_team,
            "away_team": away_team,
            "start_time": start_time,
            "location": details.get('location'),
            "url": url,
            "match_url": match_url
        })
        
    # Sort matches by date
    matches.sort(key=lambda x: x['start_time'])
    
    return matches

if __name__ == "__main__":
    # Test with the provided URL
    url = "https://competitions.ffbb.com/ligues/naq/comites/0033/clubs/naq0033048/equipes/200000005210924"
    matches = fetch_matches(url)
    for m in matches:
        print(f"{m['start_time']} - {m['home_team']} vs {m['away_team']}")
