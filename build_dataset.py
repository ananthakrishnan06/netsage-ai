import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_FILE = DATA_DIR / "cases.csv"

fields = [
    "case_id",
    "issue_type",
    "symptom",
    "topology_note",
    "show_command",
    "show_command_output",
    "expected_fault",
    "osi_layer",
    "concept",
    "severity",
    "packet_tracer_file",
    "verification_command",
    "verification_result",
    "ai_root_cause",
    "ai_confidence",
    "ai_evidence",
    "ai_next_command",
    "ai_fix_steps",
    "human_decision",
    "human_correction",
    "verification_status",
]

c001 = {
    "case_id": "C001",
    "issue_type": "VLAN / Trunk",
    "symptom": (
        "PC1 can reach its own gateway at 192.168.10.1 "
        "and the VLAN 20 gateway at 192.168.20.1, "
        "but cannot reach PC2 at 192.168.20.10."
    ),
    "topology_note": (
        "R1 router-on-a-stick connected to SW1 through Gi0/0-Gi0/1. "
        "PC1 is in VLAN 10 (192.168.10.10/24). "
        "PC2 is in VLAN 20 (192.168.20.10/24). "
        "R1 Gi0/0.10 is 192.168.10.1/24 and "
        "Gi0/0.20 is 192.168.20.1/24."
    ),
    "show_command": (
        "show interfaces trunk; "
        "show vlan brief; "
        "show interfaces gigabitEthernet 0/1 switchport"
    ),
    "show_command_output": (
        "show interfaces trunk: Gi0/1 is trunking using 802.1Q; "
        "Vlans allowed on trunk: 10; "
        "Vlans allowed and active: 10; "
        "Vlans forwarding and not pruned: 10. "
        "show vlan brief: VLAN 20 SERVERS is active on Fa0/2. "
        "show interfaces Gi0/1 switchport: Administrative Mode trunk; "
        "Operational Mode trunk; dot1q; Trunking VLANs Enabled: 10."
    ),
    "expected_fault": (
        "VLAN 20 is excluded from the allowed VLAN list on the "
        "SW1 Gi0/1 trunk."
    ),
    "osi_layer": "Layer 2 — Data Link",
    "concept": "802.1Q trunk VLAN propagation",
    "severity": "High",
    "packet_tracer_file": "NetSage_C001_VLAN20_TrunkFault.pkt",
    "verification_command": "ping 192.168.20.10",
    "verification_result": (
        "After correction: Sent=4, Received=4, Lost=0%, "
        "Average=0ms."
    ),
    "ai_root_cause": "",
    "ai_confidence": "",
    "ai_evidence": "",
    "ai_next_command": "",
    "ai_fix_steps": "",
    "human_decision": "",
    "human_correction": "",
    "verification_status": "VERIFIED",
}

DATA_DIR.mkdir(parents=True, exist_ok=True)

with OUTPUT_FILE.open(
    "w",
    newline="",
    encoding="utf-8"
) as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    writer.writerow(c001)

print(f"Created: {OUTPUT_FILE}")
print(f"Cases written: 1")
print(f"Columns: {len(fields)}")