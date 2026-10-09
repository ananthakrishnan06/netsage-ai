import json
import os
import time
from typing import Dict

from dotenv import load_dotenv
import requests


load_dotenv()

# Override this with GROQ_MODEL if your account uses a different Groq model.
MODEL_NAME = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"

VALID_CATEGORIES = {
    "VLAN_ASSIGNMENT",
    "TRUNK_VLAN",
    "SUBNET_MASK",
    "DEFAULT_GATEWAY",
    "INTERFACE_SHUTDOWN",
    "STATIC_ROUTE",
    "ACL",
    "NAT",
    "IP_ADDRESS",
    "DUPLEX_SPEED",
    "STP",
    "DHCP",
    "DNS",
    "PORT_SECURITY",
    "OTHER",
}


def build_prompt(case: Dict[str, str]) -> str:
    """Build a structured JSON NetSage diagnostic prompt."""

    return f"""
You are NetSage, an expert Cisco network troubleshooting assistant.

Diagnose the following case using ONLY the supplied evidence.

CASE ID:
{case.get("case_id", "")}

SYMPTOM:
{case.get("symptom", "")}

TOPOLOGY:
{case.get("topology_note", "")}

DIAGNOSTIC COMMAND:
{case.get("show_command", "")}

OBSERVED EVIDENCE:
{case.get("show_command_output", "")}

SEVERITY:
{case.get("severity", "")}

Choose exactly ONE fault_category from:

VLAN_ASSIGNMENT
TRUNK_VLAN
SUBNET_MASK
DEFAULT_GATEWAY
INTERFACE_SHUTDOWN
STATIC_ROUTE
ACL
NAT
IP_ADDRESS
DUPLEX_SPEED
STP
DHCP
DNS
PORT_SECURITY
OTHER

CATEGORY RULES:

- SUBNET_MASK: subnet mask or prefix length is incorrect.
- DEFAULT_GATEWAY: default gateway is incorrect.
- IP_ADDRESS: the IP address itself is incorrect.
- If evidence explicitly identifies an incorrect subnet mask, choose SUBNET_MASK, not IP_ADDRESS.
- VLAN_ASSIGNMENT: switch/access/wireless port is assigned to the wrong VLAN.
- TRUNK_VLAN: VLAN is missing or incorrectly configured on a trunk.
- DHCP: DHCP service or DHCP pool configuration is faulty.
- DNS: DNS server configuration/service is faulty.
- ACL: an ACL incorrectly permits or blocks required traffic.
- NAT: NAT is missing or incorrectly matched.
- INTERFACE_SHUTDOWN: interface is administratively disabled.
- STATIC_ROUTE: required static route is missing or incorrect.
- OTHER: none of the categories apply or evidence is insufficient.

Return ONLY valid JSON.

Do NOT use Markdown.
Do NOT use code fences.
Do NOT add explanations before or after the JSON.

The JSON must contain exactly these fields:

{{
  "fault_category": "ONE VALID CATEGORY",
  "root_cause": "specific technical fault",
  "osi_layer": "specific OSI layer",
  "networking_concept": "specific networking concept",
  "confidence": 0.0,
  "evidence": "specific evidence supporting the diagnosis",
  "next_command": "one Cisco diagnostic command",
  "fix_steps": "safe corrective action"
}}

Rules:

- Use only the supplied evidence.
- Do not invent command output.
- Do not invent devices, IP addresses, VLANs, or configurations.
- Do not use the expected fault.
- Do not leave fields empty.
- Confidence must be a number between 0 and 1.
- If evidence is insufficient, use fault_category "OTHER" and evidence "Insufficient evidence".
- Do not provide internal reasoning.

WORKED EXAMPLE 1:

Input evidence:
PC1 is connected to an access port configured for VLAN 20, but PC1 is supposed to be in VLAN 10.

Output:
{{
  "fault_category": "VLAN_ASSIGNMENT",
  "root_cause": "The access port is assigned to VLAN 20 instead of VLAN 10.",
  "osi_layer": "Data Link",
  "networking_concept": "VLAN assignment",
  "confidence": 0.98,
  "evidence": "The supplied configuration identifies the access port as belonging to VLAN 20 while PC1 requires VLAN 10.",
  "next_command": "show vlan brief",
  "fix_steps": "After human review, assign the access port to the correct VLAN."
}}

WORKED EXAMPLE 2:

Input evidence:
The routing table does not contain a route to 192.168.40.0/24.

Output:
{{
  "fault_category": "STATIC_ROUTE",
  "root_cause": "The required static route to 192.168.40.0/24 is missing.",
  "osi_layer": "Network",
  "networking_concept": "Static routing",
  "confidence": 1.0,
  "evidence": "The supplied routing evidence shows no route for 192.168.40.0/24.",
  "next_command": "show ip route 192.168.40.0",
  "fix_steps": "After human review, add the required static route using the appropriate next hop or exit interface."
}}

WORKED EXAMPLE 3:

Input evidence:
An ACL denies traffic from 192.168.10.10 to 192.168.20.10.

Output:
{{
  "fault_category": "ACL",
  "root_cause": "The ACL blocks required traffic from PC1 to the server.",
  "osi_layer": "Network",
  "networking_concept": "Access Control List",
  "confidence": 1.0,
  "evidence": "The supplied ACL contains a deny rule for 192.168.10.10 to 192.168.20.10.",
  "next_command": "show access-lists",
  "fix_steps": "After human review, modify or remove the blocking ACL rule so the required traffic is permitted."
}}
"""


def ai_available() -> bool:
    """Return whether a Groq API key has been configured."""
    return bool(os.getenv("GROQ_API_KEY"))


def run_groq_ai(case: Dict[str, str]) -> str:

    if not ai_available():
        raise RuntimeError(
            "Groq is not configured. Set the GROQ_API_KEY environment variable."
        )

    prompt = build_prompt(case)

    print("Calling Groq model:", MODEL_NAME)

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are NetSage. Return ONLY valid JSON matching the requested "
                    "schema. Do not expose internal reasoning."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
        "max_completion_tokens": 400,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
        "Content-Type": "application/json",
    }

    # A 503 is a temporary provider-capacity error. Retry twice with a short
    # exponential backoff before returning the error to the UI.
    for attempt in range(3):
        response = requests.post(
            GROQ_CHAT_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )
        if response.status_code != 503 or attempt == 2:
            try:
                response.raise_for_status()
            except requests.HTTPError as error:
                raise RuntimeError(
                    f"Groq API request failed ({response.status_code}): {response.text}"
                ) from error
            break
        wait_seconds = 2 ** (attempt + 1)
        print(
            f"Groq is busy (503). Retrying in {wait_seconds} seconds "
            f"({attempt + 1}/2)..."
        )
        time.sleep(wait_seconds)

    try:
        content = response.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError, ValueError) as error:
        raise RuntimeError(f"Groq returned an unexpected response: {response.text}") from error

    if not content or not content.strip():
        raise RuntimeError(
            "Groq returned an empty final answer."
        )

    # Validate JSON before returning it.
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"Groq returned invalid JSON: {error}"
        )

    required_fields = {
        "fault_category",
        "root_cause",
        "osi_layer",
        "networking_concept",
        "confidence",
        "evidence",
        "next_command",
        "fix_steps",
    }

    missing = required_fields - set(parsed.keys())

    if missing:
        raise RuntimeError(
            f"Groq JSON is missing fields: {sorted(missing)}"
        )

    category = str(parsed["fault_category"]).upper().strip()

    if category not in VALID_CATEGORIES:
        raise RuntimeError(
            f"Invalid fault category returned by Groq: {category}"
        )

    try:
        confidence = float(parsed["confidence"])
    except (TypeError, ValueError):
        raise RuntimeError(
            "Groq confidence is not numeric."
        )

    if not 0 <= confidence <= 1:
        raise RuntimeError(
            "Groq confidence must be between 0 and 1."
        )

    parsed["fault_category"] = category
    parsed["confidence"] = confidence

    return json.dumps(parsed, ensure_ascii=False)


# Kept for compatibility with callers of the previous function name.
run_local_ai = run_groq_ai
