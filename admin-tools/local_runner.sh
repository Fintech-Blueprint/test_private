#!/usr/bin/env bash
# Safe local runner for common admin checks.
# - Does not echo secrets to stdout.
# - Uses generate_installation_token.py to create an installation token and saves to a secure temp file.
# Usage:
#   GITHUB_APP_PRIVATE_KEY=/path/to/key.pem GITHUB_APP_ID=1952259 ./local_runner.sh [INSTALLATION_ID]

set -euo pipefail
IFS=$'\n\t'

KEY_PATH=${GITHUB_APP_PRIVATE_KEY:-/workspaces/test_private/org-fintech-blueprint-token-admin.2025-09-14.private-key.pem}
APP_ID=${GITHUB_APP_ID:-1952259}
INSTALLATION_ID=${1:-${INSTALLATION_ID:-}}
TMP_TOKEN_FILE=$(mktemp /tmp/fintech_install_token.XXXXXX)
trap 'rm -f "$TMP_TOKEN_FILE"' EXIT

if [ ! -f "$KEY_PATH" ]; then
  echo "Private key not found at: $KEY_PATH" >&2
  exit 2
fi

echo "Listing installations (metadata only)..."
python3 "$(dirname "$0")/generate_installation_token.py" "$KEY_PATH" --app-id "$APP_ID" --list-only

if [ -z "$INSTALLATION_ID" ]; then
  echo "\nNo installation id provided. Re-run with INSTALLATION_ID as first arg or set INSTALLATION_ID env var." >&2
  exit 3
fi

echo "Exchanging for installation token and saving to secure temp file..."
python3 "$(dirname "$0")/generate_installation_token.py" "$KEY_PATH" --app-id "$APP_ID" --installation-id "$INSTALLATION_ID" --out-file "$TMP_TOKEN_FILE"
chmod 600 "$TMP_TOKEN_FILE"

# Use the token to query org-level information (public-key and list secrets)
INSTALLATION_TOKEN=$(cat "$TMP_TOKEN_FILE")

echo "Querying org Actions public key (response will be printed)..."
curl -s -H "Authorization: token ${INSTALLATION_TOKEN}" -H "Accept: application/vnd.github+json" \
  https://api.github.com/orgs/Fintech-Blueprint/actions/secrets/public-key | jq .

echo "Listing org Actions secrets (names only)..."
curl -s -H "Authorization: token ${INSTALLATION_TOKEN}" -H "Accept: application/vnd.github+json" \
  https://api.github.com/orgs/Fintech-Blueprint/actions/secrets | jq .

# token file will be removed by trap
echo "Done. Temporary token file removed."