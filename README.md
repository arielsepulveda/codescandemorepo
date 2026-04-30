# codescandemorepo

> ⚠️ **DELIBERATELY VULNERABLE** — this repository contains insecure code on
> purpose. It is the demo target for [Accenture CodeScan](https://github.com/arielsepulveda/CodeScan).
> Do **not** deploy any of this. Do **not** copy snippets into real projects.

## Why this exists

When we run CodeScan against this repo we should see findings across:

| Stack | Files | Classes of issue |
|---|---|---|
| Python (Flask) | [`app/`](./app/) | SQLi, command injection, SSRF, path traversal, unsafe deserialization, hardcoded secrets, weak crypto |
| **Subtle / semantic** | [`app/subtle/`](./app/subtle/) | **Things SAST + GHAS + CodeQL structurally cannot find** — see below |
| Node / TypeScript (Express) | [`api/`](./api/) | XSS, eval injection, JWT misuse, prototype pollution, hardcoded secrets |
| Azure Bicep | [`infra/main.bicep`](./infra/main.bicep) | Public storage, weak TLS, KV without RBAC, SQL public access, NSG 0.0.0.0/0, plaintext admin password |
| Terraform | [`infra/network.tf`](./infra/network.tf) | NSG SSH from anywhere, public blob, AWS-style key literal |
| ARM template | [`infra/arm-deployment.json`](./infra/arm-deployment.json) | NSG inbound `*`, no disk encryption |
| Shell | [`scripts/deploy.sh`](./scripts/deploy.sh) | `curl \| sh`, unquoted variables, eval of input |

## The differentiator — `app/subtle/`

The pattern-class findings above (SQLi, XSS, hardcoded secrets) any commercial
SAST will detect. The interesting part is `app/subtle/` — eight vulnerabilities
that **CodeQL, Snyk Code, SonarQube, and GitHub Advanced Security cannot find**,
because each one requires *semantic reasoning* a regex engine doesn't do:

| File | Why pattern SAST can't see it |
|---|---|
| `auth_logic.py`     | OR-condition is structurally valid; you have to *know* what the function intends |
| `transfer.py`       | Async TOCTOU — race lives in I/O ordering, not in a missing `Lock` |
| `id_validation.py`  | The `int(...)` cast looks like a sanitizer to taint analysis; the bug is the *legal domain* |
| `admin_routing.py`  | Two libraries (router + middleware) disagree on path normalization |
| `jwt_confusion.py`  | Unsafe call is structurally identical to safe one |
| `rate_limit_lie.py` | The decorator's docstring promises rate limiting; the body doesn't deliver |
| `prompt_sink.py`    | New attack class (LLM tool-calling injection) — no existing signatures |
| `cross_lang.py` + `cross_lang.js` | Bug is in the *contract* between languages; SAST scans them in isolation |
| `iac_link.py`       | Code looks fine, IaC looks flagged-but-isolated; only the join is exploitable |

Read [`app/subtle/README.md`](./app/subtle/README.md) for the per-vulnerability
explanation of why CodeQL et al. miss it. This is the slide where Accenture
says *"your existing SAST and CodeScan are not redundant — they look for
different classes of bugs."*

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
