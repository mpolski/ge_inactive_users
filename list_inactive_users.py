import os
from dotenv import load_dotenv
import google.auth
from google.auth.transport.requests import AuthorizedSession
from datetime import datetime, timedelta, timezone
import argparse
import csv

# Load environment variables from .env file
load_dotenv()

# --- CONFIGURATION ---
PROJECT_ID = os.getenv("PROJECT_ID", "your-project-id")
LOCATION = os.getenv("LOCATION", "global")
USER_STORE_ID = os.getenv("USER_STORE_ID", "default_user_store")
DAYS_INACTIVE = int(os.getenv("DAYS_INACTIVE", 60))
# ---------------------

def get_licensed_users(project_id, location, user_store_id):
    """Fetches the list of users assigned a Discovery Engine license and their last login time."""
    credentials, _ = google.auth.default()
    authed_session = AuthorizedSession(credentials)
    
    url = f"https://discoveryengine.googleapis.com/v1beta/projects/{project_id}/locations/{location}/userStores/{user_store_id}/userLicenses"
    
    users_data = [] # List of dicts: {'user': ..., 'last_login_dt': ..., 'last_login_str': ...}
    page_token = None
    
    while True:
        params = {}
        if page_token:
            params['pageToken'] = page_token
            
        print(f"Fetching from: {url}")
        response = authed_session.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        user_licenses = data.get('userLicenses', [])
        
        for license_obj in user_licenses:
            user_principal = license_obj.get('userPrincipal')
            last_login_str = license_obj.get('lastLoginTime')
            
            last_login_dt = None
            if last_login_str:
                try:
                    dt_str = last_login_str.rstrip('Z')
                    if '.' in dt_str:
                        parts = dt_str.split('.')
                        frac = parts[1][:6]
                        dt_str = f"{parts[0]}.{frac}"
                    
                    last_login_dt = datetime.fromisoformat(dt_str).replace(tzinfo=timezone.utc)
                except ValueError as e:
                    print(f"Warning: Could not parse timestamp '{last_login_str}': {e}")
            
            if user_principal:
                users_data.append({
                    'user': user_principal,
                    'last_login_dt': last_login_dt,
                    'last_login_str': last_login_str
                })
            
        page_token = data.get('nextPageToken')
        if not page_token:
            break
            
    return users_data

def main():
    parser = argparse.ArgumentParser(description="List inactive Gemini Enterprise users.")
    parser.add_argument("--output", help="Path to save the output report file.")
    parser.add_argument("--dump-all", action="store_true", help="Dump all users sorted by last login time.")
    args = parser.parse_args()

    print(f"Fetching licensed users from Project '{PROJECT_ID}', Location '{LOCATION}', User Store '{USER_STORE_ID}'...")
    try:
        users_data = get_licensed_users(PROJECT_ID, LOCATION, USER_STORE_ID)
        print(f"-> Found {len(users_data)} licensed users.\n")
    except Exception as e:
        print(f"Error fetching licenses: {e}")
        return

    now = datetime.now(timezone.utc)
    
    if args.dump_all:
        # Sort users by last login time, most recent first. Handle None (never logged in) by putting them last.
        sorted_users = sorted(
            users_data, 
            key=lambda x: x['last_login_dt'] or datetime.min.replace(tzinfo=timezone.utc), 
            reverse=True
        )
        
        if args.output:
            print(f"Saving all users to CSV report: {args.output}...")
            try:
                with open(args.output, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Email', 'LastLoginTime (UTC)'])
                    for item in sorted_users:
                        writer.writerow([item['user'], item['last_login_str'] or 'Never Logged In'])
                print("Report saved successfully.")
            except Exception as e:
                print(f"Error saving report: {e}")
        else:
            print("==================================================")
            print(" ALL USERS (Sorted by last login)")
            print("==================================================")
            for item in sorted_users:
                print(f"{item['user']}, {item['last_login_str'] or 'Never Logged In'}")
    else:
        # Legacy/Default logic for inactive users
        inactive_users = []
        never_logged_in = []

        for item in users_data:
            user = item['user']
            last_login_dt = item['last_login_dt']
            last_login_str = item['last_login_str']
            
            if last_login_dt is None:
                never_logged_in.append(user)
            else:
                delta = now - last_login_dt
                if delta.days >= DAYS_INACTIVE:
                    inactive_users.append((user, last_login_str))

        if args.output:
            print(f"Saving standard CSV report to {args.output}...")
            try:
                with open(args.output, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Status', 'Email', 'LastLoginTime (UTC)'])
                    for user in sorted(never_logged_in):
                        writer.writerow(['Never Logged In', user, ''])
                    for user, last_login in sorted(inactive_users, key=lambda x: x[0]):
                        writer.writerow(['Inactive', user, last_login])
                print("Report saved successfully.")
            except Exception as e:
                print(f"Error saving report: {e}")
        else:
            report_content = []
            report_content.append("==================================================")
            report_content.append(" USERS NEVER LOGGED IN")
            report_content.append("==================================================")
            if not never_logged_in:
                report_content.append("None.")
            else:
                for user in sorted(never_logged_in):
                    report_content.append(user)
                    
            report_content.append(f"\n==================================================")
            report_content.append(f" INACTIVE USERS (No activity in last {DAYS_INACTIVE} days)")
            report_content.append("==================================================")
            
            if not inactive_users:
                report_content.append("No users match this criteria.")
            else:
                for user, last_login in sorted(inactive_users, key=lambda x: x[0]):
                    report_content.append(f"{user}, {last_login}")

            for line in report_content:
                print(line)


if __name__ == "__main__":
    main()
