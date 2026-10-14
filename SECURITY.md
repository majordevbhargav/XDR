# Security Policy

## Scope

This repository is a defensive security engineering and learning project. Please test integrations only in systems and tenants you are authorized to use.

## Reporting a vulnerability

Do not publish credentials, access tokens, customer information, or a weaponizable exploit in a public issue. For a private report, contact the repository owner through the contact method listed on their GitHub profile. Include the affected component, impact, reproduction steps, and any safe mitigation.

## Secrets and configuration

- Never commit AWS access keys, ServiceNow credentials, bearer tokens, private keys, or production data.
- Use least-privilege identities and short-lived credentials where possible.
- Keep local environment files out of version control.
- Rotate any credential that may have been exposed, then remove it from active use. Removing it from the latest commit alone may not remove it from Git history.

## Automated response safety

- Run tests against isolated, non-production environments first.
- Require explicit authorization and strong target validation for disruptive actions.
- Log action decisions and outcomes without recording secrets.
- Provide timeout, retry, and failure handling; retries must not blindly repeat non-idempotent actions.
- Do not enable endpoint containment until approval controls, auditability, and a recovery procedure are tested.
