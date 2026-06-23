#!/usr/bin/env python3
"""
Helper script to obtain a Spotify refresh token via the Authorization Code flow.

Usage:
  1. Create a Spotify app at https://developer.spotify.com/dashboard
  2. Set the redirect URI to http://localhost:8888/callback
  3. Run: python3 get_refresh_token.py <CLIENT_ID> <CLIENT_SECRET>
  4. Open the URL printed in your browser and authorize
  5. Copy the refresh token from the output
"""

import sys
import base64
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

REDIRECT_URI = "http://localhost:8888/callback"
SCOPE = "user-read-recently-played"


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <CLIENT_ID> <CLIENT_SECRET>")
        sys.exit(1)

    client_id = sys.argv[1]
    client_secret = sys.argv[2]

    auth_url = (
        "https://accounts.spotify.com/authorize?"
        + urllib.parse.urlencode(
            {
                "client_id": client_id,
                "response_type": "code",
                "redirect_uri": REDIRECT_URI,
                "scope": SCOPE,
            }
        )
    )

    print("\n🔗 Open this URL in your browser:\n")
    print(auth_url)
    print("\n⏳ Waiting for callback on http://localhost:8888/callback ...\n")

    # Start a local server to capture the callback
    authorization_code = None

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal authorization_code
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)

            if "code" in params:
                authorization_code = params["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<h1>Success!</h1><p>You can close this tab and return to the terminal.</p>"
                )
            else:
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                error = params.get("error", ["unknown"])[0]
                self.wfile.write(f"<h1>Error: {error}</h1>".encode())

        def log_message(self, format, *args):
            pass  # Suppress request logs

    server = HTTPServer(("localhost", 8888), CallbackHandler)
    server.handle_request()

    if not authorization_code:
        print("❌ Failed to get authorization code")
        sys.exit(1)

    print("✅ Got authorization code, exchanging for tokens...")

    # Exchange code for tokens
    auth_header = base64.b64encode(
        f"{client_id}:{client_secret}".encode()
    ).decode()

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": REDIRECT_URI,
        },
    )

    if response.status_code != 200:
        print(f"❌ Token exchange failed: {response.text}")
        sys.exit(1)

    data = response.json()
    print("\n" + "=" * 60)
    print("🎉 Success! Here's your refresh token:\n")
    print(data["refresh_token"])
    print("\n" + "=" * 60)
    print("\nAdd this as SPOTIFY_REFRESH_TOKEN in your repo secrets:")
    print("  Settings → Secrets and variables → Actions → New repository secret")
    print()


if __name__ == "__main__":
    main()
