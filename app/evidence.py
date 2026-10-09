from typing import Dict, List


def collect_evidence(case: Dict[str, str]) -> List[str]:
    """
    Extract the important evidence fields from a troubleshooting case.
    """

    evidence = []

    if case.get("symptom"):
        evidence.append(f"Symptom: {case['symptom']}")

    if case.get("topology_note"):
        evidence.append(f"Topology: {case['topology_note']}")

    if case.get("show_command"):
        evidence.append(f"Commands: {case['show_command']}")

    if case.get("show_command_output"):
        evidence.append(
            f"Observed output: {case['show_command_output']}"
        )

    if case.get("verification_result"):
        evidence.append(
            f"Verification: {case['verification_result']}"
        )

    return evidence


def find_keywords(case: Dict[str, str], keywords: List[str]) -> List[str]:
    """
    Find which diagnostic keywords appear in the case evidence.
    """

    text = " ".join(
        [
            case.get("symptom", ""),
            case.get("topology_note", ""),
            case.get("show_command", ""),
            case.get("show_command_output", ""),
        ]
    ).lower()

    return [keyword for keyword in keywords if keyword.lower() in text]