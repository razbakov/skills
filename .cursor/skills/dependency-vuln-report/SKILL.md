---
name: dependency-vuln-report
description: Runs dependency vulnerability scans and produces a complete report with exact installed versions, reason for risk, and remediation priority for each finding. Use when the user asks for dependency scan, npm audit, bun audit, package vulnerabilities, CVE review, or security status of dependencies.
---

# Dependency Vulnerability Report

## Purpose

Generate a vulnerability report where every finding includes:

- package name
- installed version used
- severity
- reason
- priority
- fix status

Do not group findings in a way that hides individual vulnerable packages.

## Workflow

1. Run audits (production-only):

```bash
npm audit --omit=dev --json > /tmp/audit-prod.json
```

2. Resolve exact installed versions from lockfile:

```bash
node -e 'const lock=require("./package-lock.json");const a=require("/tmp/audit-prod.json");const pkgs=lock.packages||{};for(const [name,v] of Object.entries(a.vulnerabilities||{})){const key=`node_modules/${name}`;console.log(`${name}|${pkgs[key]?.version||"unknown"}|${v.severity}|${v.isDirect?"direct":"transitive"}|${v.fixAvailable?"fix-available":"no-auto-fix"}`)}'
```

## Priority Rules

Assign one priority per finding:

- `P0`: High/Critical in production runtime with no automatic fix, or severe exploitability in real app paths.
- `P1`: High in production with fix available.
- `P2`: Moderate direct production dependency, or high dev-only toolchain risk.
- `P3`: Moderate transitive risk.
- `P4`: Low severity.

When uncertain, prefer the stricter priority and state the assumption.

## Required Output Format

Always include:

1. Summary counts:

- total
- high / moderate / low / critical
- prod-only counts

2. Full finding list (no omissions), sorted by priority then severity:

- `package`
- `version used`
- `severity`
- `direct/transitive`
- `reason`
- `priority`
- `fix availability`

3. Short remediation plan:

- immediate (P0/P1)
- next (P2)
- backlog (P3/P4)

## Reason Writing Rules

Each reason must be one concrete sentence tied to the advisory class, for example:

- open redirect/XSS risk in router navigation handling
- prototype pollution in object mutation helpers
- ReDoS risk in parser/regex path
- dev-server file exposure/bypass in local tooling

Avoid vague reasons like "security issue exists."

## Quality Gates

Before finalizing:

- Verify every listed vulnerable package has an explicit version.
- Verify the number of listed findings equals audit total.
- If earlier you grouped packages, provide an expanded per-package list when asked.
