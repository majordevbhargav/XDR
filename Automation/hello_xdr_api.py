"""
Hello-XDR: local workflow logic and Cisco XDR Automation API example.

Usage:
  python Automation/hello_xdr_api.py test
  python Automation/hello_xdr_api.py list
  python Automation/hello_xdr_api.py run "Asha" 10.1.2.3

Required for API commands:
  XDR_ID, XDR_PW, XDR_TOKEN_URL
Optional:
  XDR_REGION=us|eu|apjc (default: apjc)
  XDR_ALLOW_WORKFLOW_START=true (required to enable the experimental start request)

The workflow-start request body is tenant/API-version dependent and remains a
placeholder until verified against the OpenAPI spec for your Cisco XDR tenant.
Workflow execution is therefore disabled by default.
"""
from __future__ import annotations

import ipaddress
import os
import sys
from typing import Any

import requests

HOSTS = {
    "us": "https://automate.us.security.cisco.com",
    "eu": "https://automate.eu.security.cisco.com",
    "apjc": "https://automate.apjc.security.cisco.com",
}
PRIVATE_NETWORKS = tuple(
    ipaddress.ip_network(cidr)
    for cidr in (
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
        "fc00::/7",
    )
)


def classify_ip(ip: str) -> str:
    """Return private, public, or non-public/reserved without mislabelling special IPs."""
    address = ipaddress.ip_address(ip)
    if any(address.version == network.version and address in network for network in PRIVATE_NETWORKS):
        return "private"
    if address.is_global:
        return "public"
    return "non-public/reserved"


def hello_xdr(name: str, ip: str) -> str:
    """Local example workflow logic; invalid IP addresses raise ValueError."""
    clean_name = name.strip()
    if not clean_name:
        raise ValueError("name must not be empty")
    kind = classify_ip(ip)
    return f"Hello {clean_name}, {ip} is a {kind} address"


TESTS = [
    ("8.8.8.8", "public"),
    ("10.1.2.3", "private"),
    ("192.168.1.5", "private"),
    ("172.16.5.5", "private"),
    ("172.31.255.1", "private"),
    ("172.32.0.1", "public"),
    ("172.15.0.1", "public"),
    ("127.0.0.1", "non-public/reserved"),
    ("169.254.1.2", "non-public/reserved"),
    ("2001:4860:4860::8888", "public"),
    ("fd00::1", "private"),
]


def run_tests() -> bool:
    """Run dependency-light local checks without contacting Cisco XDR."""
    failures = 0
    for ip, expected in TESTS:
        try:
            result = classify_ip(ip)
            passed = result == expected
        except ValueError as exc:
            result = f"invalid IP: {exc}"
            passed = False
        print(f'{"PASS" if passed else "FAIL"}  {ip:<24} expected={expected:<20} actual={result}')
        failures += not passed

    try:
        hello_xdr("   ", "10.0.0.1")
        print("FAIL  empty name should be rejected")
        failures += 1
    except ValueError:
        print("PASS  empty name is rejected")

    print(f"\n{len(TESTS) + 1 - failures}/{len(TESTS) + 1} checks passed")
    return failures == 0


def get_config() -> tuple[str, str, str, str]:
    """Validate required API configuration before making a network request."""
    region = os.getenv("XDR_REGION", "apjc").strip().lower()
    if region not in HOSTS:
        raise ValueError(f"XDR_REGION must be one of: {', '.join(HOSTS)}")

    required = ("XDR_ID", "XDR_PW", "XDR_TOKEN_URL")
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise ValueError("Missing required environment variables: " + ", ".join(missing))

    return os.environ["XDR_ID"], os.environ["XDR_PW"], os.environ["XDR_TOKEN_URL"], region


def get_token() -> str:
    client_id, client_secret, token_url, _ = get_config()
    response = requests.post(
        token_url,
        auth=(client_id, client_secret),
        data={"grant_type": "client_credentials"},
        timeout=30,
    )
    response.raise_for_status()
    token = response.json().get("access_token")
    if not token:
        raise RuntimeError("Token response did not contain access_token")
    return token


def api_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {get_token()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def api_base() -> str:
    _, _, _, region = get_config()
    return HOSTS[region]


def list_workflows() -> list[dict[str, Any]]:
    response = requests.get(
        f"{api_base()}/api/v1/workflows",
        headers=api_headers(),
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()

    # APIs commonly return either a raw list or a list wrapped in a named field.
    if isinstance(payload, list):
        workflows = payload
    elif isinstance(payload, dict):
        workflows = payload.get("workflows") or payload.get("data")
    else:
        workflows = None

    if not isinstance(workflows, list):
        raise RuntimeError("Unexpected workflow-list response; expected a list or a workflows/data field")
    return [item for item in workflows if isinstance(item, dict)]


def run_workflow(name: str, ip: str) -> None:
    # Validate inputs locally before any API call.
    hello_xdr(name, ip)

    if os.getenv("XDR_ALLOW_WORKFLOW_START", "").strip().lower() != "true":
        raise RuntimeError(
            "Workflow start is disabled. Verify the request schema against your tenant's "
            "Cisco XDR Automation OpenAPI spec, then explicitly set XDR_ALLOW_WORKFLOW_START=true."
        )

    workflows = list_workflows()
    workflow = next((item for item in workflows if item.get("name") == "Hello-XDR"), None)
    if workflow is None:
        available = ", ".join(str(item.get("name", "<unnamed>")) for item in workflows)
        raise RuntimeError(f"Hello-XDR workflow was not found. Available workflows: {available or 'none'}")

    # IMPORTANT: Confirm the endpoint and body fields against your tenant's current
    # Automation OpenAPI spec before enabling this request. This body is illustrative.
    body = {"workflow_id": workflow.get("id"), "inputs": {"name": name, "ip": ip}}
    if not body["workflow_id"]:
        raise RuntimeError("Workflow metadata did not include an id; refusing to start it")

    response = requests.post(
        f"{api_base()}/api/v1.1/workflows/start",
        headers=api_headers(),
        json=body,
        timeout=30,
    )
    response.raise_for_status()
    print(f"Workflow start request accepted (HTTP {response.status_code}).")
    if response.text:
        print(response.text)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    command = args[0].lower() if args else "test"

    try:
        if command == "test":
            return 0 if run_tests() else 1
        if command == "list":
            for workflow in list_workflows():
                print(workflow.get("id", "<no id>"), workflow.get("name", "<unnamed>"), workflow.get("type", ""))
            return 0
        if command == "run":
            if len(args) != 3:
                print('Usage: python Automation/hello_xdr_api.py run "Name" IP_ADDRESS', file=sys.stderr)
                return 2
            run_workflow(args[1], args[2])
            return 0

        print("Unknown command. Choose: test, list, run", file=sys.stderr)
        return 2
    except (ValueError, RuntimeError, requests.RequestException, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
