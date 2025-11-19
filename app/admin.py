import argparse
import json
import os
from app.services.spotify_manager import SpotifyConnectionManager

TOKENS_FILE = "tokens.json"

def authorize():
    conn = SpotifyConnectionManager.get_instance()
    url = conn.get_authorization_url()
    print(f"Go to this URL to authorize your app:\n{url}")
    print("After authorization, Spotify will redirect to /callback and tokens will be saved.")

def refresh():
    conn = SpotifyConnectionManager.get_instance()
    if not os.path.exists(TOKENS_FILE):
        print("No tokens.json found. Run `admin.py authorize` first.")
        return
    with open(TOKENS_FILE) as f:
        token_info = json.load(f)
    conn.load_token_info(token_info)
    conn.refresh_access_token()
    conn.save_tokens()
    print("Tokens refreshed and saved.")

def status():
    if not os.path.exists(TOKENS_FILE):
        print("No tokens.json found. Run `admin.py authorize` first.")
        return
    with open(TOKENS_FILE) as f:
        token_info = json.load(f)
    print("Current token info:")
    print(json.dumps(token_info, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Spotify Admin CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("authorize", help="Start Spotify authorization flow")
    subparsers.add_parser("refresh", help="Refresh access token using refresh token")
    subparsers.add_parser("status", help="Show current token info")

    args = parser.parse_args()

    if args.command == "authorize":
        authorize()
    elif args.command == "refresh":
        refresh()
    elif args.command == "status":
        status()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()