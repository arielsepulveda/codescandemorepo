# Known issues — the scan oracle

This is the deliberate ground truth for what `accenture-codescan` should find
in this repo. Used to:

1. **Validate scanner sensitivity** — anything missing from a scan run is a
   false-negative we should investigate.
2. **Validate triage** — confidence promotion / dedup / suppression on the
   *same* finding across multiple scans.
3. **Demo the PR feedback loop** — fix one of these in a PR, watch CodeScan
   close it; introduce a new one in a PR, watch it open.

CWE numbering is illustrative — the auditor may pick a sibling CWE that's
just as defensible.

---

## Baseline findings (1–6) — every SAST catches these

These are the textbook cases. We deliberately keep a small set so the demo
shows CodeScan covers the SAST baseline rather than only chasing the
exotic stuff. **Every one of these should also be reported by GHAS /
CodeQL / SonarQube** — that's the point of including them.

| # | File | CWE | Sev | Issue |
|---|------|-----|-----|-------|
| 1 | `app/main.py`         | CWE-798  | high | Hardcoded `SECRET_KEY` literal |
| 2 | `app/main.py`         | CWE-89   | crit | SQL injection via f-string in `users_search` |
| 3 | `app/auth.py`         | CWE-327  | high | MD5 used for password hashing |
| 4 | `app/requirements.txt`| CWE-1104 | med  | Outdated dependencies (Flask 1.0.0, PyJWT 1.6.0) |
| 5 | `infra/main.bicep`    | CWE-732  | high | Storage `allowBlobPublicAccess: true` |
| 6 | `infra/main.bicep`    | CWE-284  | crit | NSG inbound rule allows SSH from `*` |

---

## `app/subtle/` (7–14) — the SAST blind-spots

These are the most important findings for the demo. Every other file in
this repo could be substituted for tfsec / Checkov / CodeQL output and a
buyer wouldn't blink. The `subtle/` findings are what CodeScan finds and
they don't.

For each, a successful audit must (a) record the finding, (b) cite the
specific reason no pattern matcher can detect it, (c) propose the right
fix — not just "sanitize input" but the architectural change that
removes the class.

| # | File | CWE | Sev | Why SAST can't find it |
|---|------|-----|-----|------------------------|
| 7  | `app/subtle/auth_logic.py`     | CWE-285 | crit | OR-condition takes a request-body flag as authorization input |
| 8  | `app/subtle/transfer.py`       | CWE-367 | high | Async TOCTOU between balance read and write across an `await` |
| 9  | `app/subtle/id_validation.py`  | CWE-20  | high | `int(...)` is a SAST-recognized sanitizer; the bug is the legal-domain check |
| 10 | `app/subtle/admin_routing.py`  | CWE-863 | crit | Middleware path-prefix disagrees with framework router (case, slashes) |
| 11 | `app/subtle/jwt_confusion.py`  | CWE-347 | crit | Unsafe call (RS256+HS256 list, public-key-as-secret) is identical to safe call |
| 12 | `app/subtle/rate_limit_lie.py` | CWE-770 | high | Decorator name + docstring promise rate limit; impl uses a per-call dict |
| 13 | `app/subtle/prompt_sink.py`    | CWE-94  | crit | LLM tool-calling injection — new attack class, no SAST signature |
| 14 | `app/subtle/cross_lang.py` + `cross_lang.js` | CWE-704 | high | Backend stringifies bool; frontend truthy-checks the string |
| 15 | `app/subtle/iac_link.py`       | CWE-732 (joint) | crit | App auth ✓ but IaC declares the storage account public — only the join is the bug |

Note: 9 distinct *findings* in 8 *files* (`cross_lang` is one logical bug
spanning two files).

A traditional SAST run on this repo will report findings 1–6 and miss
7–15 entirely. CodeScan should report all 15. **The 9-finding delta
between SAST and CodeScan is the entire commercial pitch.**

---

## Total expected: ~14–15 distinct findings

Severity mix: ~5 critical / ~6 high / ~3 medium / ~0 low.

Confidence after the verify stage will collapse some borderline calls.
A successful demo is **12–14** open findings post-verify, **with all 9
`subtle/` findings still standing** — those are the ones a competing SAST
*cannot* find, so they're the ones we most need to keep through verify.

---

## Cross-domain links to validate joint reasoning

CodeScan's `azure_full_stack_audit` taskflow should link findings across
the code/IaC boundary. The expected escalation:

- **#15 (`iac_link.py`)** + **#5 (`infra/main.bicep` public storage)** =
  high-confidence *"user uploads via auth-checked endpoint are publicly
  readable at the storage layer"*. Neither file alone is the bug — only
  the join is.

If the scanner runs all stages and only reports findings independently,
that's a regression in the cross-correlation pipeline.
