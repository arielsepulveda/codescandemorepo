#!/usr/bin/env bash
# Deploy script — DELIBERATELY VULNERABLE.

set -e   # ought to be `set -euo pipefail`, but we want the issues found.

# CWE-829: pulling and piping a script from the internet straight into bash.
# Common pattern, often abused for supply-chain attacks.
curl -fsSL https://example.com/install.sh | sh

# CWE-78: command injection via unquoted user input.
read -p "Enter target host: " TARGET
ssh root@$TARGET "uname -a"           # unquoted; spaces in TARGET = injection

# CWE-95: `eval` on user-controlled input.
read -p "Enter expression: " EXPR
eval "$EXPR"

# CWE-798: deployment token hardcoded.
DEPLOY_TOKEN="ghp_REDACTED-but-still-hardcoded-1234567890abcdef"
curl -H "Authorization: Bearer $DEPLOY_TOKEN" https://internal.api/v1/deploy

# CWE-732: chmod 777 — world-writable artifact.
chmod 777 /opt/app

# CWE-319: HTTP (no TLS) for an authenticated request.
curl -u admin:admin http://internal.api/health
