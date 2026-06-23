#!/usr/bin/env python3
"""
Helper script to obtain a Spotify refresh token via the Authorization Code flow.

Usage:
  1. Create a Spotify app at https://developer.spotify.com/dashboard
  2. Add https://example.com/callback as a redirect URI
  3. Run: python3 get_refresh_token.py <CLIENT_ID> <CLIENT_SECRET>
  4. Open the URL printed in your browser and authorize
  5. You'll be redirected to example.com -- copy the full URL from your browser
  6. Paste it back into the terminal when prompted
"""

import sys
import base64
import urllib.parse
import requests

REDIRECT_URI = "https://example.com/callback"
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
    print("\nAfter authorizing, you'll be redirected to a page that won't load.")
    print("That's expected! Copy the FULL URL from your browser's address bar.\n")

    callback_url = input("Paste the redirect URL here: ").strip()

    # Extract the authorization code from the pasted URL
    parsed = urllib.parse.urlparse(callback_url)
    params = urllib.parse.parse_qs(parsed.query)

    if "code" not in params:
        print("❌ No authorization code found in that URL")
        if "error" in params:
            print(f"   Error: {params['error'][0]}")
        sys.exit(1)

    authorization_code = params["code"][0]
    print("\n✅ Got authorization code, exchanging for tokens...")

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
