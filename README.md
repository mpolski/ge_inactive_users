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

### 2. Export to CSV File
To save the report as a standard CSV file (easily importable into Excel or Google Sheets):
```bash
uv run python list_inactive_users.py --output filename.csv
```
*(Note: When using `--output`, the full console report is suppressed for cleaner output).*
