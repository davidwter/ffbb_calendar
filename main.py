import argparse
import sys
import os
from scraper import fetch_matches
from calendar_generator import create_calendar

def main():
    parser = argparse.ArgumentParser(description="Generate ICS calendar from basketball match schedule.")
    parser.add_argument("url", help="URL of the match schedule")
    
    args = parser.parse_args()
    
    try:
        # 1. Fetch matches
        matches = fetch_matches(args.url)
        
        if not matches:
            print("No matches found. Please check the URL and try again.")
            sys.exit(1)
            
        print(f"Successfully scraped {len(matches)} matches.")
        
        # 2. Interactive Mode: New or Update
        while True:
            choice = input("\nDo you want to create a (n)ew calendar or (u)pdate an existing one? [n/u]: ").lower().strip()
            if choice in ['n', 'u']:
                break
            print("Invalid choice. Please enter 'n' or 'u'.")
            
        if choice == 'n':
            filename = input("Enter filename for the new calendar [default: matches.ics]: ").strip()
            if not filename:
                filename = "matches.ics"
            if not filename.endswith(".ics"):
                filename += ".ics"
                
            # Check if file exists to avoid accidental overwrite
            if os.path.exists(filename):
                overwrite = input(f"File '{filename}' already exists. Overwrite? [y/N]: ").lower().strip()
                if overwrite != 'y':
                    print("Operation cancelled.")
                    sys.exit(0)
                    
        else: # Update
            filename = input("Enter filename of the existing calendar to update: ").strip()
            if not filename:
                print("Filename is required for update.")
                sys.exit(1)
            if not filename.endswith(".ics"):
                filename += ".ics"
                
            if not os.path.exists(filename):
                print(f"Error: File '{filename}' does not exist.")
                create_new = input("Do you want to create it instead? [y/N]: ").lower().strip()
                if create_new == 'y':
                    pass # Proceed to create
                else:
                    sys.exit(1)
        
        # 3. Generate Calendar
        # Note: For "Update", we currently overwrite the file with the new schedule.
        # This assumes the user wants the file to reflect the *current* schedule from the URL.
        # If the user wanted to *merge* multiple teams, we would need more complex logic.
        # Given "update existing one for the same team", overwriting is the correct behavior 
        # to ensure cancelled/moved matches are updated (by replacement).
        
        ics_content = create_calendar(matches)
        
        with open(filename, "w") as f:
            f.write(ics_content)
            
        print(f"\nSuccessfully wrote calendar to: {filename}")
        print("You can now import this file into Google Calendar or Apple Calendar.")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
