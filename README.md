# codescandemorepo

> ⚠️ **DELIBERATELY VULNERABLE** — this repository contains insecure code on
> purpose. It is the demo target for [Accenture CodeScan](https://github.com/arielsepulveda/CodeScan).
> Do **not** deploy any of this. Do **not** copy snippets into real projects.

## What's in here, and why

The repo is split into two halves:

### Half 1 — *baseline* findings (the SAST-detectable cases)

A handful of textbook vulnerabilities every SAST tool catches. They exist
so the demo proves CodeScan **doesn't miss the obvious stuff** that GHAS /
CodeQL / SonarQube find for free.

| File | CWE | Class | Why it's here |
|---|---|---|---|
| [`app/main.py`](./app/main.py)         | CWE-89  | SQL injection (f-string) | textbook taint flow |
| [`app/main.py`](./app/main.py)         | CWE-798 | Hardcoded `SECRET_KEY`   | textbook secret scan |
| [`app/auth.py`](./app/auth.py)         | CWE-327 | MD5 for password hashing | textbook weak-crypto rule |
| [`app/requirements.txt`](./app/requirements.txt) | CWE-1104 | Outdated deps with public CVEs | textbook SCA case |
| [`infra/main.bicep`](./infra/main.bicep)         | CWE-732 | Storage `allowBlobPublicAccess: true` | textbook IaC posture |
| [`infra/main.bicep`](./infra/main.bicep)         | CWE-284 | NSG SSH from `*`            | textbook IaC posture |

**6 findings.** Anything claiming to do code security catches all 6.

### Half 2 — *the differentiator*: [`app/subtle/`](./app/subtle/)

Eight vulnerabilities that **CodeQL, Snyk Code, SonarQube, and GitHub
Advanced Security cannot find**, because each one requires *semantic
reasoning* a regex engine doesn't do.

| File | Why pattern SAST can't see it |
|---|---|
| `auth_logic.py`     | OR-condition is structurally valid; you have to *know* what the function intends |
| `transfer.py`       | Async TOCTOU — race lives in I/O ordering, not in a missing `Lock` |
| `id_validation.py`  | The `int(...)` cast looks like a sanitizer to taint analysis; the bug is the *legal domain* |
| `admin_routing.py`  | Two libraries (router + middleware) disagree on path normalization |
| `jwt_confusion.py`  | Unsafe call is structurally identical to the safe one |
| `rate_limit_lie.py` | The decorator's docstring promises rate limiting; the body doesn't deliver |
| `prompt_sink.py`    | New attack class (LLM tool-calling injection) — no signatures |
| `cross_lang.py` + `cross_lang.js` | Bug is in the *contract* between languages; SAST scans them in isolation |
| `iac_link.py`       | App auth ✓ but `infra/main.bicep` makes the storage public — only the *join* is the bug |

**8 findings.** A traditional SAST sees zero of these. CodeScan finds all of them.

Read [`app/subtle/README.md`](./app/subtle/README.md) for the per-file
explanation of *why* each one is invisible to pattern-based SAST.

## The number that matters

```
              GHAS / CodeQL / Snyk      CodeScan
baseline      6                         6
subtle        0                         8
─────────────────────────────────────────────
total         6                         14
```

The **8-finding delta** is the entire commercial pitch. It's what justifies
adding CodeScan to a stack that already has GHAS — it doesn't replace, it
*finds the bugs the incumbent can't*.

## Total expected: ~14 distinct findings

Severity mix targets ~5 critical / ~6 high / ~3 medium. Numbers may vary
slightly depending on how the verify stage rules — see
[`docs/known-issues.md`](./docs/known-issues.md) for the per-finding oracle.

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

## License

MIT — see [LICENSE](./LICENSE). The vulnerabilities are deliberate; you may
study them, post-mortem them, or use them in your own training material.
