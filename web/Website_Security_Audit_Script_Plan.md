# Plan: Website Security Audit Script

*Remote testing and source code examination*

## 1. Goals and boundaries

**Goal:** One orchestrator script that takes a target (URL and/or source repo), runs remote and static checks, and produces a single prioritized report.

**Honest scope note:** No script can test "every" security aspect. Business-logic flaws, authorization design errors, and novel vulnerabilities need human review. The practical aim is to automate everything that can be automated and map coverage to a standard (OWASP WSTG for remote tests, OWASP ASVS for source/controls), so gaps are explicit rather than hidden.

**Authorization gate (built in, not optional):**

- Require a `--i-own-or-am-authorized` flag plus a scope file listing allowed domains/IPs.
- Refuse to scan anything outside the scope file, including redirects to third-party hosts.
- Default to non-destructive, rate-limited checks; active/intrusive modules need an explicit `--intrusive` flag and are meant for staging.

## 2. Architecture

- **Language:** Python as the orchestrator (good subprocess/HTTP/JSON tooling). It wraps proven tools instead of reimplementing them, and does custom checks only where no tool fits.
- **Module interface:** each check is a plugin with `name`, `category`, `requires` (tool/binary), `run(target, config) -> list[Finding]`.
- **Finding schema:** `id, title, severity (info/low/med/high/crit), confidence, category (WSTG/ASVS/CWE ref), evidence, location (URL or file:line), remediation, tool`.
- **Config:** a YAML file with scope, credentials for authenticated scans (test accounts only), rate limits, enabled modules, and timeouts.
- **Execution:** modules run in phases; independent modules run in parallel with per-host rate limiting. Raw tool output is saved to an `artifacts/` directory for audit.
- **Dependency check:** at startup, report which tools are missing and which modules will be skipped, so a partial run is never mistaken for a full one.

## 3. Remote (black-box) testing

### Phase R1: Recon and surface mapping

- DNS records (A/AAAA/MX/TXT, SPF/DKIM/DMARC), zone-transfer attempt, subdomain enumeration (passive: `subfinder`/`amass`), dangling CNAME and subdomain-takeover checks
- Port and service scan (`nmap`), service/version fingerprinting, exposed admin/database ports
- Technology fingerprinting (headers, cookies, JS libraries)
- Crawl and spider (including a headless browser pass for JS-heavy sites) to build an endpoint/parameter inventory; parse `robots.txt`, `sitemap.xml`, `security.txt`, and API specs (OpenAPI/GraphQL introspection)

### Phase R2: Transport and configuration

- TLS: protocol versions, cipher suites, certificate validity/chain/expiry, HSTS (and preload), OCSP stapling (`testssl.sh` or `sslyze`)
- HTTP security headers: CSP (and weakness analysis), X-Frame-Options/frame-ancestors, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, COOP/COEP/CORP
- Cookies: Secure, HttpOnly, SameSite, scope, and prefix usage
- CORS: reflected origins, `null` origin, wildcard with credentials
- HTTP to HTTPS redirect behavior, mixed content, HTTP methods allowed (TRACE, PUT, DELETE)
- Information disclosure: verbose errors, stack traces, server banners, directory listing, exposed `.git`, `.env`, backups, source maps, debug endpoints, default files

### Phase R3: Authentication and session

- Login: account enumeration via responses/timing, lockout and rate limiting, default credentials, password policy, MFA presence
- Password reset and registration flows: token entropy, expiry, reuse, host-header poisoning
- Session: token entropy, fixation, rotation on login, invalidation on logout, timeout, concurrent sessions
- JWT checks: `alg=none`, weak HMAC secrets, missing expiry/audience, key confusion

### Phase R4: Access control

- With two or more test accounts at different privilege levels: IDOR checks (swap object IDs between users), horizontal/vertical privilege escalation, forced browsing to admin routes, unauthenticated access to authenticated endpoints, method-based bypasses

### Phase R5: Input handling and injection (active, rate-limited)

- Reflected/stored/DOM XSS, SQL/NoSQL/command/LDAP/template injection, XXE, SSRF (using an out-of-band callback host you control), open redirects, path traversal/LFI, CRLF/header injection, HTTP request smuggling, deserialization indicators
- Drive these with `OWASP ZAP` (automation framework), `nuclei` templates, and `sqlmap` in a conservative mode, with custom checks for anything they miss

### Phase R6: Application-specific

- File upload: type/size validation, executable upload, path handling
- CSRF: token presence and enforcement, SameSite reliance
- API: mass assignment, excessive data exposure, rate limits, GraphQL depth/batching/introspection, versioned legacy endpoints
- WebSocket: origin checks, auth on connect, message validation
- Client side: third-party scripts without Subresource Integrity, vulnerable JS libraries (Retire.js), exposed secrets in bundles, `postMessage` handling, clickjacking
- Availability (non-destructive only): rate limiting presence, expensive-request amplification indicators; no actual DoS

### Phase R7: Infrastructure and third parties

- Cloud storage buckets (public S3/GCS/Azure blobs), CDN/WAF bypass indicators, email security posture, exposed CI artifacts, leaked credentials in public repos (via `trufflehog` against the org)

## 4. Source code (white-box) examination

### Phase S1: Inventory

- Detect languages, frameworks, build systems, and entry points; build a route/endpoint list from framework conventions to cross-reference with remote findings

### Phase S2: Dependencies and supply chain

- SCA: `osv-scanner`, `pip-audit`, `npm audit`, OWASP Dependency-Check; flag known CVEs, unmaintained packages, typosquatting risk, unpinned versions, and missing lockfiles
- SBOM generation (CycloneDX via `syft`)
- Review CI/CD config for injection risks, over-privileged tokens, and unpinned actions

### Phase S3: Secrets

- `gitleaks`/`trufflehog` over the working tree and full git history; flag keys, tokens, private keys, and connection strings; check committed `.env` files

### Phase S4: Static analysis (SAST)

- `semgrep` with security rule packs (OWASP Top 10, language-specific), plus `CodeQL` where available
- Language-specific tools: `bandit` (Python), `eslint-plugin-security` (JS), `SpotBugs`+`find-sec-bugs` (Java), `gosec` (Go), `brakeman` (Ruby)
- Custom semgrep rules for project-specific patterns: raw SQL string building, unsafe `eval`/`exec`, disabled TLS verification, weak crypto, unsafe deserialization, missing auth decorators, `innerHTML`/`dangerouslySetInnerHTML`, hardcoded CORS wildcards

### Phase S5: Configuration and infrastructure-as-code

- Server/app config: debug mode on, permissive CORS, weak session settings, missing security middleware
- Dockerfiles (`hadolint`, `trivy`), Kubernetes manifests, Terraform/CloudFormation (`checkov`/`tfsec`): root containers, open security groups, public buckets, missing encryption

### Phase S6: Targeted code review aids

- Crypto usage inventory (algorithms, key sizes, randomness sources, password hashing)
- Authz coverage map: every route versus its auth/permission check, flagging unprotected routes
- Data-flow summary from sources (request params) to sinks (DB, shell, file, HTML), with high-risk paths queued for human review
- Logging review: sensitive data in logs, missing audit events

### Phase S7: Cross-correlation

- Match remote findings to code locations (for example, an XSS found at `/search` linked to the template that renders it), and mark findings confirmed by both methods as higher confidence

## 5. Reporting

- Normalize all tool output into the finding schema, then de-duplicate and rank by severity × confidence.
- Outputs: JSON (machine-readable), SARIF (for GitHub code scanning and IDEs), and an HTML/Markdown report with an executive summary, findings grouped by category, evidence and reproduction steps, and remediation guidance.
- A **coverage matrix** maps each WSTG/ASVS item to tested / skipped (and why) / manual-only, so the report never overstates assurance.
- **Baseline and diff mode:** compare against a previous run to show new, fixed, and regressed findings. Support suppressions with justification and expiry.
- **Exit codes** by severity threshold, for CI gating.

## 6. Safety and operational controls

- Global and per-host rate limits, request-count caps, and configurable timeouts
- A kill switch and resume support
- Redact secrets and credentials in logs and reports
- Store scan credentials via environment variables or a secrets manager, never in the repo
- Log every request sent, for accountability
- Recommend running intrusive modules against staging, with a production profile that is passive/safe only

## 7. Build milestones

1. **Skeleton:** CLI, config/scope enforcement, plugin interface, finding schema, report generator
2. **Passive remote:** headers, TLS, cookies, CORS, info-disclosure checks (custom, no external dependencies)
3. **Tool wrappers:** nmap, testssl, nuclei, ZAP, with output parsers
4. **Source phases:** gitleaks, semgrep, SCA, IaC scanners, and the custom rule set
5. **Authenticated testing:** login handling, multi-role IDOR/authz checks
6. **Correlation, coverage matrix, diff mode, SARIF output**
7. **Hardening:** tests against intentionally vulnerable targets (DVWA, OWASP Juice Shop, WebGoat) to measure detection rates and false positives, plus CI integration and documentation

## 8. Validation

- Use deliberately vulnerable apps as ground truth, and track precision and recall per module.
- Keep a regression suite of known-bad and known-good fixtures for each custom check.
- Periodically review tool and rule updates, since coverage decays as new vulnerability classes emerge.
