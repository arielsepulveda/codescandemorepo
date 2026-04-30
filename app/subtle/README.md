# `app/subtle/` — what pattern-matching SAST can't see

Every file in this directory contains a **real, exploitable vulnerability**
that a traditional SAST (CodeQL, SonarQube, Snyk Code, GitHub Advanced
Security) is structurally unable to detect, because each one requires:

- **Semantic understanding** of what the code is *trying* to do
- **Cross-function / cross-file reasoning** beyond a single AST walk
- **Reading docstrings, comments, and variable names** as part of the
  spec — not just the code
- **Joint reasoning** across stacks (code ↔ IaC, frontend ↔ backend, sync
  ↔ async, code ↔ runtime)
- **Business-logic invariants** that vary per customer

Each file has a header explaining (a) the vulnerability, (b) why it's
exploitable, and (c) why a pattern-matcher will miss it.

This is the slide where Accenture says *"CodeScan finds vulnerabilities your
existing SAST cannot, because it reasons about your code the way an attacker
does — not the way a regex does."*

| File | Vulnerability class | Why pattern SAST misses it |
|---|---|---|
| `auth_logic.py` | OR-condition auth bypass | The OR is structurally valid; you'd need to know the *intent* of the function |
| `transfer.py` | Business-logic TOCTOU | No `threading.Lock` pattern; the race lives in async I/O |
| `id_validation.py` | Negative-ID ORM bypass | The validator returns an int; "negative ints aren't sanitizable" is not a pattern |
| `admin_routing.py` | Path-prefix vs router mismatch | Two correct-looking checks, with a semantic gap between them |
| `jwt_confusion.py` | RS256/HS256 algorithm confusion | The unsafe call is structurally identical to the safe one |
| `rate_limit_lie.py` | Comment promises rate limit; code doesn't enforce | A regex doesn't read English |
| `prompt_sink.py` | LLM tool-calling sink | New attack class; no signatures yet |
| `cross_lang.py` (+ `cross_lang.js`) | String/boolean confusion across languages | One file is Python, the other is JS; SAST scans them in isolation |
| `iac_link.py` | Code uploads to a blob the IaC makes public | Code SAST never reads `infra/main.bicep` |
