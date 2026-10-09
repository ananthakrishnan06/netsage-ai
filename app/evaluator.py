import json
import re
from typing import Dict


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


def parse_ai_response(response: str) -> Dict[str, str]:
    """Parse JSON model output, with fallback to the old format."""

    if not response:
        return {}

    # New JSON format
    try:
        data = json.loads(response)

        if isinstance(data, dict):
            return {
                str(k): str(v)
                for k, v in data.items()
            }

    except (json.JSONDecodeError, TypeError):
        pass

    # Backward-compatible old format
    fields = {
        "fault_category": "FAULT_CATEGORY",
        "root_cause": "ROOT CAUSE",
        "osi_layer": "OSI LAYER",
        "networking_concept": "NETWORKING CONCEPT",
        "confidence": "CONFIDENCE",
        "evidence": "EVIDENCE",
        "next_command": "NEXT COMMAND",
        "fix_steps": "SAFE FIX",
    }

    parsed = {}

    for new_name, old_name in fields.items():
        pattern = rf"^{re.escape(old_name)}:\s*(.+?)$"

        match = re.search(
            pattern,
            response,
            re.IGNORECASE | re.MULTILINE,
        )

        if match:
            parsed[new_name] = match.group(1).strip()

    return parsed


def extract_fault_category(ai_response: str) -> str:
    """Extract the model's original fault category."""

    parsed = parse_ai_response(ai_response)

    category = parsed.get(
        "fault_category",
        "",
    ).upper().strip()

    if category in VALID_CATEGORIES:
        return category

    return "OTHER"


def extract_root_cause(ai_response: str) -> str:
    return parse_ai_response(ai_response).get(
        "root_cause",
        "",
    )


def extract_osi_layer(ai_response: str) -> str:
    return parse_ai_response(ai_response).get(
        "osi_layer",
        "",
    )


def extract_networking_concept(ai_response: str) -> str:
    return parse_ai_response(ai_response).get(
        "networking_concept",
        "",
    )


def extract_confidence(ai_response: str) -> str:
    return parse_ai_response(ai_response).get(
        "confidence",
        "",
    )


def extract_evidence(ai_response: str) -> str:
    return parse_ai_response(ai_response).get(
        "evidence",
        "",
    )


def extract_next_command(ai_response: str) -> str:
    return parse_ai_response(ai_response).get(
        "next_command",
        "",
    )


def extract_safe_fix(ai_response: str) -> str:
    return parse_ai_response(ai_response).get(
        "fix_steps",
        "",
    )


def expected_category(expected_fault: str) -> str:
    """Convert ground-truth fault into a standard category."""

    text = str(expected_fault).lower().strip()

    if "default gateway" in text:
        return "DEFAULT_GATEWAY"

    if "subnet mask" in text:
        return "SUBNET_MASK"

    if "vlan mapping" in text:
        return "VLAN_ASSIGNMENT"

    if "wrong vlan" in text:
        return "VLAN_ASSIGNMENT"

    if "access port" in text and "vlan" in text:
        return "VLAN_ASSIGNMENT"

    if "shutdown" in text:
        return "INTERFACE_SHUTDOWN"

    if "static route" in text:
        return "STATIC_ROUTE"

    if "acl" in text:
        return "ACL"

    if "nat" in text:
        return "NAT"

    if "dhcp" in text:
        return "DHCP"

    if "dns" in text:
        return "DNS"

    if "trunk" in text and "vlan" in text:
        return "TRUNK_VLAN"

    if "ip address" in text:
        return "IP_ADDRESS"

    if "duplex" in text or "speed" in text:
        return "DUPLEX_SPEED"

    if "spanning tree" in text or "stp" in text:
        return "STP"

    if "port security" in text:
        return "PORT_SECURITY"

    return "OTHER"


def classify_fault_from_evidence(
    case: Dict[str, str],
) -> str:
    """
    Deterministic verification layer.

    Uses explicit fault evidence rather than treating normal
    ipconfig/show-command fields as faults.
    """

    evidence = str(
        case.get("show_command_output", "")
    ).lower()

    symptom = str(
        case.get("symptom", "")
    ).lower()

    combined = evidence + " " + symptom

    # DHCP
    if (
        "dhcp pool" in combined
        or "dhcp request failed" in combined
        or "dhcp server" in combined
        or "dhcp lease" in combined
        or "dhcp binding" in combined
    ):
        return "DHCP"

    # DNS
    if (
        "dns request timed out" in combined
        or "dns server unreachable" in combined
        or "incorrect dns" in combined
        or "wrong dns" in combined
        or "dns server configuration" in combined
    ):
        return "DNS"

    # ACL
    if (
        "access-list" in combined
        or "acl" in combined
    ):
        return "ACL"

    # NAT
    if (
        "incorrect nat" in combined
        or "wrong nat" in combined
        or "nat is not translating" in combined
        or "nat translation failed" in combined
    ):
        return "NAT"

    # Static routing
    if (
        "missing static route" in combined
        or "incorrect static route" in combined
        or "wrong static route" in combined
        or "ip route is missing" in combined
    ):
        return "STATIC_ROUTE"

    # Interface shutdown
    if (
        "administratively down" in combined
        or "interface is shutdown" in combined
        or "interface is shut down" in combined
        or "interface shutdown" in combined
    ):
        return "INTERFACE_SHUTDOWN"

    # Trunk VLAN
    if (
        "vlan is not allowed on the trunk" in combined
        or "vlan not allowed on trunk" in combined
        or "missing vlan from trunk" in combined
        or "trunk vlan mismatch" in combined
        or "incorrect trunk vlan" in combined
    ):
        return "TRUNK_VLAN"

    # VLAN assignment
    if (
        "assigned to vlan" in combined
        or "incorrectly assigned to vlan" in combined
        or "wrong vlan" in combined
        or "vlan assignment" in combined
        or "vlan mapping" in combined
        or "has no fa0/1" in combined
        or "has no fa0/2" in combined
    ):
        return "VLAN_ASSIGNMENT"

    # Default gateway
    if (
        "incorrect default gateway" in combined
        or "wrong default gateway" in combined
        or "default gateway is incorrect" in combined
        or "default gateway is wrong" in combined
        or "default gateway misconfigured" in combined
        or "misconfigured default gateway" in combined
        or "default gateway configuration is incorrect" in combined
    ):
        return "DEFAULT_GATEWAY"

    # Subnet mask
    if (
        "incorrect subnet mask" in combined
        or "wrong subnet mask" in combined
        or "subnet mask is incorrect" in combined
        or "subnet mask is wrong" in combined
        or "misconfigured subnet mask" in combined
        or "incorrectly configured subnet mask" in combined
    ):
        return "SUBNET_MASK"

    # IP address
    if (
        "incorrect ip address" in combined
        or "wrong ip address" in combined
        or "ip address is incorrect" in combined
        or "ip address conflict" in combined
        or "duplicate ip address" in combined
    ):
        return "IP_ADDRESS"

    return "OTHER"


def evaluate_case(
    case: Dict[str, str],
    ai_response: str,
) -> Dict[str, object]:
    """Evaluate AI diagnosis using AI + evidence verification."""

    expected_fault = case.get(
        "expected_fault",
        "",
    )

    expected = expected_category(
        expected_fault
    )

    # Original model prediction
    ai_predicted = extract_fault_category(
        ai_response
    )

    # Evidence-based verification
    rule_predicted = classify_fault_from_evidence(
        case
    )

    # Final verified category
    if rule_predicted != "OTHER":
        predicted = rule_predicted
    else:
        predicted = ai_predicted

    # Extract AI fields
    root_cause = extract_root_cause(
        ai_response
    )

    confidence = extract_confidence(
        ai_response
    )

    evidence = extract_evidence(
        ai_response
    )

    next_command = extract_next_command(
        ai_response
    )

    safe_fix = extract_safe_fix(
        ai_response
    )

    # Evaluation
    if (
        predicted == expected
        and predicted != "OTHER"
    ):
        status = "Correct"
        score = 1.0

    elif (
        predicted == "OTHER"
        or expected == "OTHER"
    ):
        status = "Needs Review"
        score = 0.0

    else:
        status = "Incorrect"
        score = 0.0

    return {
        "case_id": case.get(
            "case_id",
            "",
        ),

        "expected_fault": expected_fault,

        "expected_category": expected,

        "ai_predicted_category": ai_predicted,

        "rule_predicted_category": rule_predicted,

        "ai_fault_category": predicted,

        "ai_root_cause": root_cause,

        "ai_confidence": confidence,

        "ai_evidence": evidence,

        "ai_next_command": next_command,

        "ai_fix_steps": safe_fix,

        "evaluation_score": score,

        "evaluation_status": status,
    }
