# Known issues — the scan oracle

This is the deliberate ground truth for what `accenture-codescan` should find
in this repo. We use it to:

1. **Validate scanner sensitivity** — anything missing from a scan run is a
   false-negative we should investigate.
2. **Validate triage** — confidence promotion / dedup / suppression on the
   *same* finding across multiple scans.
3. **Demo the PR feedback loop** — fix one of these in a PR, watch CodeScan
   close it; introduce a new one in a PR, watch it open.

Findings are grouped by file. CWE numbering is illustrative — the real
auditor may pick a sibling CWE that's just as defensible.

---

## `app/main.py` (Flask, Python)

| # | CWE | Sev | Line | Issue |
|---|-----|-----|------|-------|
| 1 | CWE-798 | high | ~22 | Hardcoded `SECRET_KEY` |
| 2 | CWE-89  | crit | ~33 | SQL injection via f-string in `users_search` |
| 3 | CWE-78  | crit | ~44 | Command injection via `shell=True` in `ping` |
| 4 | CWE-918 | high | ~55 | SSRF in `/fetch` — no host allowlist |
| 5 | CWE-601 | med  | ~66 | Open redirect in `/redirect` |
| 6 | CWE-94  | crit | ~75 | Server-side template injection in `/render` |
| 7 | CWE-95  | crit | ~84 | `eval()` on attacker input in `/exec` |
| 8 | CWE-489 | med  | ~90 | Werkzeug debug mode enabled in `app.run` |
| 9 | CWE-668 | low  | ~90 | Listening on `0.0.0.0` for a debug app |

## `app/auth.py`

| # | CWE | Sev | Line | Issue |
|---|-----|-----|------|-------|
| 10 | CWE-798 | high | ~12 | Hardcoded JWT signing secret |
| 11 | CWE-327 | high | ~19 | MD5 used for password hashing |
| 12 | CWE-916 | med  | ~19 | Password hash without salt |
| 13 | CWE-208 | med  | ~25 | Non-constant-time string compare in `verify_password` |
| 14 | CWE-347 | high | ~38 | `jwt.decode` accepts `alg=none` |

## `app/upload.py`

| # | CWE | Sev | Line | Issue |
|---|-----|-----|------|-------|
| 15 | CWE-22  | high | ~20 | Path traversal in `upload_file` |
| 16 | CWE-434 | med  | ~20 | No file-type / MIME validation |
| 17 | CWE-22  | high | ~30 | Path traversal in `download_file` |
| 18 | CWE-502 | crit | ~40 | `pickle.loads` on untrusted bytes |
| 19 | CWE-22  | high | ~52 | `tarfile.extractall` without member sanitization (zip-slip) |

## `app/requirements.txt`

| # | CWE | Sev | Note |
|---|-----|-----|------|
| 20 | CWE-1104 | med | Outdated dependencies with public CVEs (Flask 1.0.0, PyJWT 1.6.0, requests 2.20.0, Jinja2 2.10, Werkzeug 0.15.0) |

## `api/server.ts` (Express, TypeScript)

| # | CWE | Sev | Line | Issue |
|---|-----|-----|------|-------|
| 21 | CWE-798 | high | ~14 | Hardcoded JWT secret |
| 22 | CWE-89  | crit | ~22 | SQL injection via template literal |
| 23 | CWE-347 | high | ~30 | `jwt.verify` without algorithm pinning |
| 24 | CWE-79  | high | ~38 | Reflected XSS in `/greet` |
| 25 | CWE-95  | crit | ~46 | `eval()` on attacker input in `/calc` |
| 26 | CWE-78  | crit | ~52 | Shell injection in `/sh` |
| 27 | CWE-1321| high | ~62 | Prototype pollution in `/merge` |
| 28 | CWE-918 | high | ~80 | SSRF in `/proxy` |

## `infra/main.bicep` (Azure)

| # | CWE | Sev | Issue |
|---|-----|-----|-------|
| 29 | CWE-798 | high | Default literal `adminPassword` |
| 30 | CWE-732 | high | Storage `allowBlobPublicAccess: true` |
| 31 | CWE-326 | med  | Storage `minimumTlsVersion: TLS1_0` |
| 32 | CWE-319 | med  | Storage `supportsHttpsTrafficOnly: false` |
| 33 | CWE-732 | high | Key Vault `enableRbacAuthorization: false` |
| 34 | CWE-693 | med  | Key Vault `enableSoftDelete: false` |
| 35 | CWE-1021| crit | SQL Server `publicNetworkAccess: Enabled` + firewall 0.0.0.0/0 |
| 36 | CWE-284 | crit | NSG inbound 22 / 3389 from `*` / `Internet` |
| 37 | CWE-798 | high | VM `adminPassword` literal |
| 38 | CWE-311 | high | VM OS disk `encryptionSettings.enabled: false` |
| 39 | CWE-1104| med  | VM `enableAutomaticUpdates: false` |
| 40 | CWE-272 | crit | Subscription-scope Owner role assignment |

## `infra/network.tf` (Terraform)

| # | CWE | Sev | Issue |
|---|-----|-----|-------|
| 41 | CWE-284 | crit | NSG SSH from `0.0.0.0/0` |
| 42 | CWE-732 | high | Storage `allow_nested_items_to_be_public: true` |
| 43 | CWE-326 | med  | Storage `min_tls_version: TLS1_0` |
| 44 | CWE-319 | med  | Storage `enable_https_traffic_only: false` |
| 45 | CWE-798 | high | Hardcoded `db_password` literal |
| 46 | CWE-798 | med  | Hardcoded `github_secret` literal |
| 47 | CWE-272 | crit | Subscription-scope Owner role assignment |

## `infra/arm-deployment.json`

| # | CWE | Sev | Issue |
|---|-----|-----|-------|
| 48 | CWE-798 | high | Default literal `adminPassword` |
| 49 | CWE-732 | high | Storage public access + weak TLS |
| 50 | CWE-311 | high | OS disk `encryptionSettings.enabled: false` |
| 51 | CWE-284 | crit | NSG `OpenAllInbound` (`*` / `*` / `*`) |
| 52 | CWE-308 | med  | Linux VM `disablePasswordAuthentication: false` |

## `scripts/deploy.sh`

| # | CWE | Sev | Issue |
|---|-----|-----|-------|
| 53 | CWE-829 | high | `curl \| sh` install pattern |
| 54 | CWE-78  | crit | Command injection via unquoted `$TARGET` |
| 55 | CWE-95  | crit | `eval` on user input |
| 56 | CWE-798 | high | Hardcoded `DEPLOY_TOKEN` |
| 57 | CWE-732 | med  | `chmod 777 /opt/app` |
| 58 | CWE-319 | med  | HTTP (no TLS) for authenticated call |

---

---

## `app/subtle/` — the SAST-blind spots

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
| 59 | `app/subtle/auth_logic.py`     | CWE-285 | crit | OR-condition takes a request-body flag as authorization input |
| 60 | `app/subtle/transfer.py`       | CWE-367 | high | Async TOCTOU between balance read and write across an `await` |
| 61 | `app/subtle/id_validation.py`  | CWE-20  | high | `int(...)` is a SAST-recognized sanitizer; the bug is the legal-domain check |
| 62 | `app/subtle/admin_routing.py`  | CWE-863 | crit | Middleware path-prefix disagrees with framework router (case, slashes) |
| 63 | `app/subtle/jwt_confusion.py`  | CWE-347 | crit | Unsafe call (RS256+HS256 list, public-key-as-secret) is identical to safe call |
| 64 | `app/subtle/rate_limit_lie.py` | CWE-770 | high | Decorator name + docstring promise rate limit; impl uses a per-call dict |
| 65 | `app/subtle/prompt_sink.py`    | CWE-94 / LLM-01 | crit | LLM tool-calling injection — new attack class, no SAST signature |
| 66 | `app/subtle/cross_lang.py` + `cross_lang.js` | CWE-704 | high | Backend stringifies bool; frontend truthy-checks the string |
| 67 | `app/subtle/iac_link.py`       | CWE-732 (joint) | crit | App auth ✓ but IaC declares the storage account public — only the join is the bug |

A traditional SAST run on this repo will report findings 1-58 and miss
59-67 entirely. CodeScan should report all 67. **The 9-finding delta
between SAST and CodeScan is the entire commercial pitch.**

---

## Cross-domain links to validate joint reasoning

CodeScan's `azure_full_stack_audit` taskflow should link findings across the
code/IaC/cloud boundary. The expected escalation chains:

- **#4 (SSRF in `/fetch`)** + **#35 (SQL public)** = high-confidence
  *"data exfiltration route from app to public DB"* once the live snapshot
  confirms reachability.
- **#15 / #17 (path traversal)** + **#30 (storage public)** = high-confidence
  *"attacker can read arbitrary blobs via the upload service"*.
- **#10 / #21 (hardcoded JWT secrets)** + **#33 (KV no-RBAC)** = the secret
  *should* be in KV but isn't; KV would also fail audit if it were there.
- **#36 / #41 / #51 (NSG wide open)** + **#37 / #48 (VM hardcoded admin)** =
  *"Internet → SSH → known-password auth"* — exploit-ready chain.

If the scanner runs all stages and only reports findings independently, that's
a regression in the cross-correlation pipeline.

---

## Total expected: ~67 distinct findings (58 patternable + 9 subtle)

Severity mix: ~17 critical / ~26 high / ~17 medium / ~7 low.

Confidence after the verify stage will collapse some of these (the auditor
should refute its own borderline calls). A successful demo is **40-55** open
findings post-verify, with critical/high preserved and **all 9 `subtle/`
findings still standing** — those are the ones a competing SAST tool
*cannot* find, so they're the ones we most need to keep through verify.
