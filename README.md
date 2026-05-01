# codescandemorepo

> ⚠️ **DELIBERATELY VULNERABLE** — this repository contains insecure code on
> purpose. It is the demo target for [Accenture CodeScan](https://github.com/arielsepulveda/CodeScan).
> Do **not** deploy any of this. Do **not** copy snippets into real projects.

## What's in here, and why

--- Removed detailed info to avoid giving contexto to the Scanner ---

## How to use as a scan target

### Local CLI

```bash
codescan scan -t accenture_codescan.taskflows.azure_full_stack_audit \
  --tenant demo --repo arielsepulveda/codescandemorepo \
  --git-url https://github.com/arielsepulveda/codescandemorepo.git \
  --max-usd 5 -o ./scan-out
```

### Via webhook + PR comments

Configure the GitHub webhook on this repo to point at your CodeScan API. Push
or open a PR; the scan-Job clones, scans, and posts inline review comments
on the PR for findings inside the changed lines.

```bash
git checkout -b demo/fix-sql-injection
# fix the SQLi in app/main.py, push, open a PR
# CodeScan should reduce its open-finding count by 1 on this branch
```

