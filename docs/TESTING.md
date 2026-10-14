# Testing Guide

## Local checks

The test suite is designed to run without Cisco XDR credentials or outbound API calls.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python Automation/hello_xdr_api.py test
```

## What is covered

- IPv4 private and public address classification.
- Loopback and link-local addresses are not mislabeled as public.
- IPv6 global and unique-local classification.
- Invalid IP input and blank names are rejected.
- The workflow-start command is disabled unless explicitly enabled.

## What is not yet covered

- Live Cisco XDR authentication and tenant-specific API response schemas.
- ServiceNow ticket creation/update behavior.
- AWS integration behavior.
- Live EDR containment or recovery.

Those checks require mocked HTTP tests and/or a dedicated non-production tenant. Do not use production credentials in CI. The GitHub Actions workflow runs only the local, credential-free tests.
