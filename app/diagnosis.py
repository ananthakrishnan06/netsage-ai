from typing import Dict

from app.evidence import collect_evidence, find_keywords
from app.models import Diagnosis


def diagnose_case(case: Dict[str, str]) -> Diagnosis:
    """
    Produce a first-pass evidence-based diagnosis.

    This version uses explicit evidence rules.
    It does not pretend to be an LLM.
    """

    case_id = case.get("case_id", "UNKNOWN")
    evidence = collect_evidence(case)

    text = " ".join(evidence).lower()

    # C001-style VLAN trunk problem
    vlan_trunk_clues = find_keywords(
        case,
        ["vlan", "trunk", "allowed", "fa0/2", "gi0/1"]
    )

    if (
        "vlan 20" in text
        and "allowed" in text
        and "10" in text
        and "20" in text
        and "trunk" in text
    ):
        return Diagnosis(
            case_id=case_id,
            root_cause=(
                "VLAN 20 is missing from the allowed VLAN list "
                "on the SW1 Gi0/1 trunk."
            ),
            osi_layer="Layer 2 — Data Link",
            concept="802.1Q trunk VLAN propagation",
            confidence=0.95,
            evidence_used=[
                item for item in evidence
                if "trunk" in item.lower()
                or "vlan" in item.lower()
            ],
            next_command="show interfaces gigabitEthernet 0/1 switchport",
            fix_steps=[
                "Enter configuration mode on SW1.",
                "Select Gi0/1.",
                "Allow VLAN 20 on the trunk.",
                "Verify with show interfaces trunk.",
                "Repeat the connectivity test."
            ],
        )

    # Generic gateway problem
    if (
        "gateway" in text
        and "cannot" in text
    ):
        return Diagnosis(
            case_id=case_id,
            root_cause="Possible default-gateway configuration problem.",
            osi_layer="Layer 3 — Network",
            concept="Default gateway",
            confidence=0.70,
            evidence_used=[
                item for item in evidence
                if "gateway" in item.lower()
            ],
            next_command="ipconfig /all",
            fix_steps=[
                "Check the client's IPv4 address.",
                "Check the configured default gateway.",
                "Compare it with the gateway for the client's subnet.",
            ],
        )

    # No sufficiently strong rule
    return Diagnosis(
        case_id=case_id,
        root_cause="Insufficient evidence for a high-confidence diagnosis.",
        osi_layer=case.get("osi_layer", "Unknown"),
        concept=case.get("concept", "Unknown"),
        confidence=0.30,
        evidence_used=evidence,
        next_command=case.get("show_command", ""),
        fix_steps=[
            "Collect additional diagnostic evidence.",
            "Do not apply a configuration change until the fault is confirmed.",
        ],
    )