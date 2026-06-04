# `app/subtle/`

Each file here contains **one real, exploitable vulnerability** that
traditional pattern-matching SAST can't see — it needs semantic and/or
cross-file reasoning.

The `# ❌ this is the bug …` annotations and the docstrings that named each
vulnerability were **removed on purpose** so a scan measures detection *from
code*, not from reading English comments. The code now states only legitimate
intent (e.g. a guard's "this requires admin", a decorator's "5/min"); the
vulnerability is the gap between that intent and the implementation.

The **answer key** — what each file should yield — lives in the repository's
root `README.md` (the scanner doesn't read `.md`, so it doesn't leak).
