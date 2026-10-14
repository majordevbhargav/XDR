"""
Hello-XDR via code.

  python hello_xdr_api.py test                 -> run the logic locally against test cases
  python hello_xdr_api.py list                 -> list workflows (Automation API, read-only)
  python hello_xdr_api.py run Asha 10.1.2.3    -> start the Hello-XDR workflow through the API

Environment variables:
  XDR_ID, XDR_PW      API client id and password (client needs the 'ao' scope for Automation)
  XDR_TOKEN_URL       token endpoint for your region (copy it from the Authentication page)
  XDR_REGION          us | eu | apjc   (default: apjc, matching your tenant URL)
"""
import ipaddress
import os
import re
import sys

import requests

# ---------- 1. The workflow logic, in code ----------
PRIVATE = re.compile(r"^(10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)")


def hello_xdr(name: str, ip: str) -> str:
    ipaddress.ip_address(ip)  # raises ValueError if it is not a valid IP
    kind = "private" if PRIVATE.match(ip) else "public"
    return f"Hello {name}, {ip} is a {kind} address"


TESTS = [
    ("8.8.8.8", "public"), ("10.1.2.3", "private"), ("192.168.1.5", "private"),
    ("172.16.5.5", "private"), ("172.31.255.1", "private"),
    ("172.32.0.1", "public"), ("172.15.0.1", "public"),
]


def run_tests():
    for ip, expected in TESTS:
        msg = hello_xdr("Asha", ip)
        status = "PASS" if f"a {expected} address" in msg else "FAIL"
        print(f"{status}  {ip:<14} {msg}")


# ---------- 2. Calling the Automation API ----------
HOSTS = {  # verify non-US hosts in the Cisco XDR API base URL list
    "us": "https://automate.us.security.cisco.com",
    "eu": "https://automate.eu.security.cisco.com",
    "apjc": "https://automate.apjc.security.cisco.com",
}
BASE = HOSTS[os.environ.get("XDR_REGION", "apjc")]


def get_token() -> str:
    r = requests.post(
        os.environ["XDR_TOKEN_URL"],
        auth=(os.environ["XDR_ID"], os.environ["XDR_PW"]),
        data={"grant_type": "client_credentials"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def headers():
    return {"Authorization": f"Bearer {get_token()}",
            "Content-Type": "application/json", "Accept": "application/json"}


def list_workflows():
    r = requests.get(f"{BASE}/api/v1/workflows", headers=headers(), timeout=30)
    r.raise_for_status()
    return r.json()


def run_workflow(name: str, ip: str):
    wf = next(w for w in list_workflows() if w["name"] == "Hello-XDR")
    # The run endpoint is listed in Cisco's rate-limit page as /v1.1/workflows/start.
    # The REQUEST BODY below is a placeholder: open the Automation OpenAPI spec
    # (developer.cisco.com > Cisco XDR APIs > Automation > Download OpenAPI) and
    # match the exact field names for the workflow id and the input variables.
    body = {"workflow_id": wf["id"], "inputs": {"name": name, "ip": ip}}
    r = requests.post(f"{BASE}/api/v1.1/workflows/start", headers=headers(),
                      json=body, timeout=30)
    print(r.status_code, r.text)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "test"
    if cmd == "test":
        run_tests()
    elif cmd == "list":
        for w in list_workflows():
            print(w["id"], w["name"], w.get("type"))
    elif cmd == "run":
        run_workflow(sys.argv[2], sys.argv[3])
