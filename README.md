# codescandemorepo

> ⚠️ **DELIBERATELY VULNERABLE** — this repository contains insecure code on
> purpose. It is the demo / benchmark target for
> [Accenture CodeScan](https://github.com/arielsepulveda/CodeScan).
> Do **not** deploy any of this. Do **not** copy snippets into real projects.

## Why the code has no explanatory comments anymore

The source files used to carry `# ❌ this is the bug …` annotations and
docstrings that named each planted vulnerability. Those were **removed on
purpose**: a reasoning scanner that reads the comment "finds" the bug by
reading English, which inflates apparent recall and hides whether it can
actually detect **from code**. (We measured this — with the comments, even a
non-reasoning model "found" a TOCTOU because a comment literally said
"TOCTOU".)

The code now states only **legitimate intent** — the kind a real auditor
would have (a rate-limit decorator's promise, an endpoint's "users read only
their own", a guard's "anything under /admin/ requires admin"). The
vulnerability is the **gap between that stated intent and the implementation**.

The **answer key** lives here in the README, which the scanner does **not**
read — so it never leaks into a scan.

## Answer key — what each file should yield

### Baseline (every SAST + any competent LLM should catch these)
| File | Planted vulnerability | CWE |
|---|---|---|
| `app/main.py` | SQL injection via f-string in `/users/search` | CWE-89 |
| `app/main.py` | Hardcoded `SECRET_KEY` | CWE-798 |
| `app/auth.py` | MD5 used for password hashing | CWE-327 |
| `infra/main.bicep` | Storage account `allowBlobPublicAccess: true` | CWE-732 |
| `infra/main.bicep` | NSG allows SSH (port 22) inbound from `*` (Internet) | CWE-284 |

### Subtle — single file, needs semantic reasoning
| File | Planted vulnerability | CWE |
|---|---|---|
| `app/subtle/transfer.py` | Async TOCTOU: balance check → `await notify_user` → debit, no lock → overdraft. Also `float` for money. | CWE-362 / CWE-367 |
| `app/subtle/auth_logic.py` | `as_admin` taken from the **request body**, not the session, in an OR auth check → privilege bypass | CWE-639 / CWE-863 |
| `app/subtle/id_validation.py` | Validator casts to `int` but never enforces `id > 0` → negative-ID ORM bypass | CWE-20 |
| `app/subtle/admin_routing.py` | Guard `request.path.startswith("/admin/")` doesn't normalize case / double-slashes the router collapses → auth skip on `/Admin/…`, `//admin/…` | CWE-863 |
| `app/subtle/jwt_confusion.py` | `algorithms=["RS256","HS256"]` while passing the **public** key as the secret → RS256↔HS256 alg-confusion forgery | CWE-347 |
| `app/subtle/rate_limit_lie.py` | `@rate_limited(5)` promises 5/min but rebuilds `_counters` on every call → limit never enforced | CWE-770 / CWE-799 |
| `app/subtle/prompt_sink.py` | Untrusted user text shares the LLM channel with the system prompt, with privileged tools registered → prompt-injection → tool abuse | CWE-77-class (LLM01) |

### Cross-file — taint / joint reasoning (needs ≥2 files together)
| Files | Planted vulnerability | CWE |
|---|---|---|
| `app/subtle/cross_lang.py` + `cross_lang.js` | Python returns `is_admin` as a **string** (`"false"`); JS `if (data.is_admin)` treats both `"true"`/`"false"` as truthy → admin UI for everyone | CWE-704 / CWE-843 |
| `app/subtle/iac_link.py` + `infra/main.bicep` | App writes per-user blobs into a storage account the bicep makes **public** → the auth-checked endpoint is bypassable directly via the blob URL | CWE-732 / CWE-863 |

> CWE ids are indicative; a scanner may map to a near neighbour. What matters
> for benchmarking is whether it identifies the **issue**, and for the
> cross-file rows, whether it correlates **both** files.

## How to use as a scan target

### Local CLI
```bash
plainsight scan --git-url https://github.com/arielsepulveda/codescandemorepo.git \
  --model-config plainsight.model_configs.byom_opencode_new \
  --max-usd 5 --no-persist
```

### Via webhook + PR comments
Configure the GitHub webhook on this repo to point at your scan API; open a PR
and the scan clones, scans, and posts inline findings on the changed lines.

```bash
git checkout -b demo/fix-sql-injection
# fix the SQLi in app/main.py, push, open a PR → open-finding count should drop by 1
```
