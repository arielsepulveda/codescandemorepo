# codescandemorepo

> ⚠️ **DELIBERATELY VULNERABLE** — this repository contains insecure code on
> purpose. It is the demo target for [Accenture CodeScan](https://github.com/arielsepulveda/CodeScan).
> Do **not** deploy any of this. Do **not** copy snippets into real projects.

## Why this exists

When we run CodeScan against this repo we should see findings across:

| Stack | Files | Classes of issue |
|---|---|---|
| Python (Flask) | [`app/`](./app/) | SQLi, command injection, SSRF, path traversal, unsafe deserialization, hardcoded secrets, weak crypto |
| Node / TypeScript (Express) | [`api/`](./api/) | XSS, eval injection, JWT misuse, prototype pollution, hardcoded secrets |
| Azure Bicep | [`infra/main.bicep`](./infra/main.bicep) | Public storage, weak TLS, KV without RBAC, SQL public access, NSG 0.0.0.0/0, plaintext admin password |
| Terraform | [`infra/network.tf`](./infra/network.tf) | NSG SSH from anywhere, public blob, AWS-style key literal |
| ARM template | [`infra/arm-deployment.json`](./infra/arm-deployment.json) | NSG inbound `*`, no disk encryption |
| Shell | [`scripts/deploy.sh`](./scripts/deploy.sh) | `curl \| sh`, unquoted variables, eval of input |

The expected findings (severity + class + file + line) are pinned in
[`docs/known-issues.md`](./docs/known-issues.md). When the scanner runs on
this tree, that file is the oracle — anything missing is a false-negative,
anything extra is worth reviewing as a possible real find.

## How to use as a scan target

### Local CLI

```bash
codescan scan -t accenture_codescan.taskflows.azure_full_stack_audit \
  --tenant demo --repo arielsepulveda/codescandemorepo \
  --git-url https://github.com/arielsepulveda/codescandemorepo.git \
  --max-usd 5 -o ./scan-out
```

### Via webhook

Configure the GitHub webhook on this repo to point at your CodeScan API. Push
or open a PR; the scan-Job clones, scans, and (for PRs) posts inline review
comments.

### Triggering a PR-feedback round

```bash
git checkout -b demo/sql-injection
# edit app/main.py, push, open a PR, watch CodeScan comment on it
```

## Counts

- ~25 expected findings, mixed severity
- 6 stacks, 8 source files
- Two distinct CWEs at the same line (CWE-89 + CWE-22 in `app/upload.py`) so
  we can validate dedup_key collision behaviour.

## License

MIT — see [LICENSE](./LICENSE). The vulnerabilities are deliberate; you may
study them, post-mortem them, or use them in your own training material.
