#!/usr/bin/env python3
"""
Safe helper to generate a GitHub App installation token and save it to a secure file.
- Does NOT print secrets or tokens to stdout.
- Writes installation token to a file with mode 0o600 if --out-file is given.

Usage:
  python3 generate_installation_token.py /path/to/private-key.pem --app-id 1952259 [--installation-id 12345] --out-file /tmp/installation.token

Notes:
- Requires `PyJWT` and `requests` (see requirements.txt in same folder).
- This helper is intended to be run on a secure admin host where the private key file exists.
"""
import argparse
import json
import os
import stat
import sys
import time
from pathlib import Path

try:
    import jwt
    import requests
except Exception as e:
    print("Missing dependency: please install requirements.txt (PyJWT, requests)")
    sys.exit(2)

GITHUB_API = "https://api.github.com"


def make_jwt(keyfile: str, app_id: int) -> str:
    now = int(time.time())
    payload = {"iat": now, "exp": now + (10 * 60), "iss": int(app_id)}
    key = Path(keyfile).expanduser().read_text()
    token = jwt.encode(payload, key, algorithm="RS256")
    # jwt.encode may return bytes in older versions
    if isinstance(token, bytes):
        token = token.decode()
    return token


def save_token_secure(path: str, token: str):
    p = Path(path)
    p.write_text(token)
    # set 0o600
    p.chmod(0o600)


def do_list_installations(jwt_token: str):
    headers = {"Authorization": f"Bearer {jwt_token}", "Accept": "application/vnd.github+json"}
    r = requests.get(f"{GITHUB_API}/app/installations", headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()


def exchange_for_installation_token(jwt_token: str, installation_id: str):
    headers = {"Authorization": f"Bearer {jwt_token}", "Accept": "application/vnd.github+json"}
    r = requests.post(f"{GITHUB_API}/app/installations/{installation_id}/access_tokens", headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("keyfile", help="Path to GitHub App private key PEM")
    p.add_argument("--app-id", type=int, default=int(os.environ.get("GITHUB_APP_ID", "1952259")), help="GitHub App ID")
    p.add_argument("--installation-id", help="Installation ID to exchange for token (optional)")
    p.add_argument("--out-file", help="If set, write the installation token to this file (mode 600). Do NOT commit the file.")
    p.add_argument("--list-only", action="store_true", help="Only list installations (do not exchange token)")
    args = p.parse_args()

    key_path = Path(args.keyfile).expanduser()
    if not key_path.exists():
        print(f"Key file not found: {key_path}")
        sys.exit(3)

    jwt_token = make_jwt(str(key_path), args.app_id)

    # List installations
    try:
        inst = do_list_installations(jwt_token)
    except Exception as e:
        print("Failed to list installations:", str(e))
        sys.exit(4)

    # Print metadata only: do NOT print tokens
    safe_inst = []
    for it in inst:
        safe_inst.append({
            "id": it.get("id"),
            "account": it.get("account", {}).get("login"),
            "repository_selection": it.get("repository_selection"),
            "app_id": it.get("app_id"),
            "created_at": it.get("created_at")
        })
    print(json.dumps({"installations": safe_inst}, indent=2))

    if args.list_only:
        print("Listed installations (no token exchanged).")
        return

    if not args.installation_id:
        print("No --installation-id provided. Set INSTALLATION_ID env var or pass --installation-id to exchange for a token.")
        return

    try:
        tok_resp = exchange_for_installation_token(jwt_token, args.installation_id)
    except Exception as e:
        print("Failed to exchange for installation token:", str(e))
        sys.exit(5)

    token = tok_resp.get("token")
    expires_at = tok_resp.get("expires_at")

    if not token:
        print("No token returned in response; aborting.")
        sys.exit(6)

    if args.out_file:
        save_token_secure(args.out_file, token)
        print(json.dumps({"status": "saved", "out_file": args.out_file, "expires_at": expires_at}))
    else:
        # For safety, do not print token. Only print expiry metadata.
        print(json.dumps({"status": "token-generated", "expires_at": expires_at}))


if __name__ == "__main__":
    main()
