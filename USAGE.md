USAGE.md — Quick bootstrap for AI sessions

Purpose
- This file shows the minimal steps an automated AI session needs to act as the Fintech-Blueprint GitHub App and operate on org-level resources.

Preconditions (must exist in workspace)
- Private key (org-level): /workspaces/test_private/org-fintech-blueprint-token-admin.2025-09-14.private-key.pem
- App ID: 1952259
- Org secret name: ORG_TOKEN_CLIENT_SECRET
- KEY_NOTICE.md and test/README.md (context and notes)

High level steps (short)
1) Generate a JWT signed by the org private key
2) Call GET /app/installations with the JWT to find the installation id for Fintech-Blueprint
3) POST /app/installations/:installation_id/access_tokens with the JWT to get the installation token
4) Use the installation token for org-level API calls (actions secrets, repo administration)
5) For CI: rely on `ORG_TOKEN_CLIENT_SECRET` available in organization Actions secrets

Example commands (do not echo secrets)

# 1) Create JWT (python helper available in repo)
export GITHUB_APP_ID=1952259
# get INSTALLATION_ID by listing installations
python3 test/scripts/generate_installation_token.py /workspaces/test_private/org-fintech-blueprint-token-admin.2025-09-14.private-key.pem

# The script expects INSTALLATION_ID env var; first generate JWT and list installations if needed

# 2) Exchange JWT for installation token (the helper script performs this once INSTALLATION_ID is set)
# 3) Verify org Actions public key (example)
curl -H "Authorization: token <INSTALLATION_TOKEN>" -H "Accept: application/vnd.github+json" \
  https://api.github.com/orgs/Fintech-Blueprint/actions/secrets/public-key

# 4) Use ORG_TOKEN_CLIENT_SECRET in workflows:
# env:
#   ORG_TOKEN_CLIENT_SECRET: ${{ secrets.ORG_TOKEN_CLIENT_SECRET }}

Security and safety notes
- Do NOT print or store JWTs, installation tokens, or secrets in logs.
- Installation tokens are short-lived; request new ones when needed.
- The authoritative key for org-level actions is the private key at the path above.
- If you need me to rotate or remove keys from repo history, I can prepare the steps.

If you want, I will commit and push this file to the repo now.
