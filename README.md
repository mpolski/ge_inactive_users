# Gemini Enterprise Inactive Users Lister

This script lists users assigned a Gemini Enterprise license who have not been active within a specified window.

## Prerequisites

1.  **Python 3.x**
2.  **Required Libraries** (using `uv`):
    The script requires a virtual environment. Create and activate one using `uv`:
    
    ```bash
    uv venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
    ```
3.  **Google Cloud SDK (gcloud)**: Installed and configured.

## Authentication using Application Default Credentials (ADC)

The script uses Application Default Credentials (ADC) to authenticate with Google Cloud APIs.

To set up ADC on your local machine:

1.  Run the following command in your terminal:
    ```bash
    gcloud auth application-default login
    ```
2.  Follow the prompts to log in with your Google account. This will save a credentials file that the script will automatically use.

## Configuration

Before running the script, ensure you have created a `.env` file (by copying `.env.example` to `.env`) and update the configuration variables there:

*   `PROJECT_ID`: Your Google Cloud Project ID.
*   `LOCATION`: The location for the User Store (e.g., "global").
*   `USER_STORE_ID`: Your User Store ID (You can usually leave the default value `default_user_store`).
*   `DAYS_INACTIVE`: The activity window to check (default is 60 days).

## Running the Script

Once authenticated and configured, you can run the script in two modes:

### 1. Human-Readable Output (Console)
To print the report directly to the console:
```bash
uv run python list_inactive_users.py
```
*(Or `python list_inactive_users.py` if your venv is activated).*

Example output:
```
Fetching licensed users from Project 'genai-whitlstd-rcf', Location 'global', User Store 'default_user_store'...
Fetching from: https://discoveryengine.googleapis.com/v1beta/projects/genai-whitlstd-rcf/locations/global/userStores/default_user_store/userLicenses
-> Found X licensed users.

==================================================
 USERS NEVER LOGGED IN
==================================================
user1@example.com

==================================================
 INACTIVE USERS (No activity in last 20 days)
==================================================
user2@example.com, 2026-03-02T08:00:28.219475924Z
```

### 2. Export to CSV File
To save the report as a standard CSV file (easily importable into Excel or Google Sheets):
```bash
uv run python list_inactive_users.py --output filename.csv
```
*(Note: When using `--output`, the full console report is suppressed for cleaner output).*

Example output:
```
Fetching licensed users from Project 'genai-whitlstd-rcf', Location 'global', User Store 'default_user_store'...
Fetching from: https://discoveryengine.googleapis.com/v1beta/projects/genai-whitlstd-rcf/locations/global/userStores/default_user_store/userLicenses
-> Found X licensed users.

Saving standard CSV report to inactive_users_list.csv...
Report saved successfully.
```

Content of `inactive_users_list.csv`:
```csv
Status,Email,LastLoginTime (UTC)
Never Logged In,user1@example.com,
Inactive,user2@example.com,2026-03-02T08:00:28.219475924Z
```

## Permissions to run the script

The script makes a GET request to the userLicenses endpoint: `.../userStores/default_user_store/userLicenses`.

According to the documentation, the specific permission required to call this method is: `discoveryengine.userStores.listUserLicenses`

This permission is typically included in the following predefined roles:

- Discovery Engine Viewer (`roles/discoveryengine.viewer`)
- Discovery Engine Editor (`roles/discoveryengine.editor`)
- Discovery Engine Admin (`roles/discoveryengine.admin`)

A user would need at least the Discovery Engine Viewer role assigned to run this script successfully.

