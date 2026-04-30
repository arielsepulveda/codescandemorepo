/**
 * Express API — DELIBERATELY VULNERABLE.
 *
 * Endpoints intentionally exhibit common JS/TS web vulnerabilities so the
 * CodeScan auditor has something to find. Do not deploy this.
 */

import express, { Request, Response } from "express";
import jwt from "jsonwebtoken";
import { exec } from "child_process";

const app = express();
app.use(express.json());

// CWE-798: hardcoded JWT secret. Anyone who reads the repo can mint tokens.
const JWT_SECRET = "change-this-but-honestly-we-never-will";

// --- Auth ---------------------------------------------------------------

app.post("/login", (req: Request, res: Response) => {
  const { username, password } = req.body;
  // CWE-89: SQL injection via template literal (representative — real code
  // would call a query builder; here we model the unsafe pattern).
  const sql = `SELECT id FROM users WHERE name='${username}' AND pwd='${password}'`;
  // ... db.execute(sql) ...
  // CWE-347: alg=none accepted because we don't pin algorithms.
  const token = jwt.sign({ user: username }, JWT_SECRET);
  res.json({ token, sql });
});

app.get("/whoami", (req: Request, res: Response) => {
  const tok = req.headers.authorization?.replace(/^Bearer /, "") ?? "";
  // CWE-347: verify with no algorithm whitelist. PyJWT-style "none" attack.
  const claims = jwt.verify(tok, JWT_SECRET);
  res.json(claims);
});

// --- Rendered output ----------------------------------------------------

app.get("/greet", (req: Request, res: Response) => {
  const name = req.query.name as string;
  // CWE-79: reflected XSS — `name` interpolated into HTML without escape.
  res.send(`<h1>Hello ${name}!</h1><p>Welcome back.</p>`);
});

// --- Eval / RCE ---------------------------------------------------------

app.post("/calc", (req: Request, res: Response) => {
  const { expr } = req.body;
  // CWE-95: eval() on attacker-controlled input.
  // tslint:disable-next-line no-eval
  const result = eval(expr);
  res.json({ result });
});

app.post("/sh", (req: Request, res: Response) => {
  const { cmd } = req.body;
  // CWE-78: command injection.
  exec(`sh -c "${cmd}"`, (err, stdout) => res.json({ stdout, err }));
});

// --- Prototype pollution -----------------------------------------------

app.post("/merge", (req: Request, res: Response) => {
  // CWE-1321: a naive recursive merge accepts __proto__ keys, polluting
  // Object.prototype across the whole process.
  const target: any = {};
  function merge(dst: any, src: any) {
    for (const k in src) {
      if (typeof src[k] === "object" && src[k] !== null) {
        if (!dst[k]) dst[k] = {};
        merge(dst[k], src[k]);
      } else {
        dst[k] = src[k];
      }
    }
  }
  merge(target, req.body);
  res.json({ target });
});

// --- SSRF ---------------------------------------------------------------

app.get("/proxy", async (req: Request, res: Response) => {
  const url = req.query.url as string;
  // CWE-918: SSRF — no allowlist, attacker can hit cloud metadata.
  const r = await fetch(url);
  res.send(await r.text());
});

app.listen(3000, "0.0.0.0", () => console.log("listening on 3000"));
