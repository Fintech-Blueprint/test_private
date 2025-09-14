# GitHub App Private Key Rotation & Incident Runbook

This runbook outlines immediate and follow-up steps to rotate a GitHub App private key and remediate if a private key was accidentally exposed or committed.

Assumptions
- You are an org owner or admin with access to the GitHub organization `Fintech-Blueprint` and the GitHub App configuration.
- The current private key path (local) is `/workspaces/test_private/org-fintech-blueprint-token-admin.2025-09-14.private-key.pem`.

Immediate (first 15-30 minutes)
1. Do NOT share the key. Work from an isolated admin host.
2. Generate a new private key in the GitHub UI:
   - GitHub → Settings → Developer settings → GitHub Apps → select app → "Generate a new private key"
   - Download the new key and place it in a secure location (e.g. a secrets manager or a restricted filesystem path).
   - Set strict permissions: `chmod 600 /secure/path/new-key.pem`.
3. Update any CI or automation that used the old key to use the new key or, better, use installation tokens stored in Actions secrets.
4. If the private key was present in a repo (committed), immediately go to the "If key was committed" steps below.

Verification
- On your admin host, run the local runner to confirm you can list installations and exchange for an installation token (tokens are short lived):
  - `GITHUB_APP_PRIVATE_KEY=/secure/path/new-key.pem GITHUB_APP_ID=1952259 ./admin-tools/local_runner.sh <INSTALLATION_ID>`
- Confirm expected org secrets exist and workflows will continue after CI secret updates.

If the key was committed to git (removal + history rewrite)
1. Mark this an incident: notify stakeholders and pause any automated processes that may use the key.
2. Create a backup clone of the repo before rewriting history:
   - `git clone --mirror git@github.com:Fintech-Blueprint/<repo>.git repo.git`
3. Prefer `git filter-repo` (recommended) or BFG if filter-repo is unavailable.
   - Example (filter-repo):
     - `git filter-repo --invert-paths --path org-fintech-blueprint-token-admin.2025-09-14.private-key.pem`
     - `git push --force --all`
   - Example (BFG):
     - `bfg --delete-files org-fintech-blueprint-token-admin*.pem`
     - `git reflog expire --expire=now --all && git gc --prune=now --aggressive && git push --force`
4. Rotate any secrets that could have been derived from the key.

Follow-up (post-incident)
- Revoke the old private key from the GitHub App UI if present.
- Rotate any organization-level secrets that may have been accessible (e.g., `ORG_TOKEN_CLIENT_SECRET`).
- Update the repo to avoid storing private keys in plaintext. Use a secrets manager or GitHub Actions secrets.
- Run a secrets scan across other repos to confirm no additional leaks.

Notes & Best Practices
- Prefer short-lived installation tokens for automation rather than persistent private keys in CI.
- Store private keys in a secure vault (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, or GitHub Secrets with restricted access).
- Keep an incident log and record the timeline of rotation and pushes for audit.

If you want, I can produce a ready-to-run playbook (scripted) for these steps; I will not run it or store any keys for you.