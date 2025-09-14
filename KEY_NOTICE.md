Kept credential

- Retained private key (org-level, highest credential):
  - /workspaces/test_private/org-fintech-blueprint-token-admin.2025-09-14.private-key.pem

Actions performed in this workspace (summary):

1. Read and summarized `test/fintech_Blueprint_concept.md`.
2. Verified OAuth client_id/client_secret (device flow) and validated a user token (earlier check).
3. Added helper scripts: `test/scripts/generate_installation_token.py`, `test/webhook/handler.py`, and `test/scripts/set_org_secret.sh`.
4. Created and uploaded org Actions secret `ORG_TOKEN_CLIENT_SECRET` to the Fintech-Blueprint organization (stored value moved from `test/README.md`).
5. Installed GitHub App for Fintech-Blueprint and generated installation token to verify org-level API access.
6. Sanitized `test/README.md` to remove plaintext client secret and added AI usage instructions referencing `ORG_TOKEN_CLIENT_SECRET`.
7. Removed an embedded `test/` nested repo from the outer index and then incorporated its contents into the main repository (so `test/` is tracked directly).
8. Pushed changes to `origin/main`.

Files removed from repo now:
- /workspaces/test_private/org-token-super-admin.2025-09-14.private-key.pem (removed per request)

Notes and recommendations:
- The org-level private key listed above remains on disk and in the repo as requested. If you later decide to remove it from the repo for security, I can remove it from history safely.
- The installation tokens used during verification are short-lived and were not stored in the repository.

If you want a more detailed audit log (API call timestamps, installation IDs, token expiry), I can produce one.
