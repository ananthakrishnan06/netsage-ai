import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
CASES_FILE = DATA / "cases.csv"
EVIDENCE_DIR = DATA / "case_evidence"

FIELDS = [
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
    "evidence_source",
]

cases = [
    {
        "case_id": "C002",
        "issue_type": "Gateway",
        "symptom": "PC2 has an IP address but cannot reach its default gateway.",
        "topology_note": "PC2 is in VLAN 20 with address 192.168.20.10/24.",
        "show_command": "show ip interface brief",
        "show_command_output": "R1 Gi0/0.20 is up/up with 192.168.20.1.",
        "expected_fault": "PC2 has an incorrect default gateway.",
        "osi_layer": "Layer 3 — Network",
        "concept": "Default gateway",
        "severity": "High",
        "verification_command": "ping 192.168.20.1",
        "verification_result": "Expected successful replies after correcting gateway.",
    },
    {
        "case_id": "C003",
        "issue_type": "IP Addressing",
        "symptom": "PC1 cannot communicate with hosts in its local subnet.",
        "topology_note": "PC1 is connected to SW1 Fa0/1 in VLAN 10.",
        "show_command": "show vlan brief",
        "show_command_output": "Fa0/1 is assigned to VLAN 10.",
        "expected_fault": "PC1 has an incorrect subnet mask.",
        "osi_layer": "Layer 3 — Network",
        "concept": "IPv4 subnet mask",
        "severity": "Medium",
        "verification_command": "ping 192.168.10.1",
        "verification_result": "Expected successful gateway ping after correcting mask.",
    },
    {
        "case_id": "C004",
        "issue_type": "VLAN",
        "symptom": "A workstation cannot reach other hosts in its expected VLAN.",
        "topology_note": "PC1 is connected to SW1 Fa0/1 and should belong to VLAN 10.",
        "show_command": "show vlan brief",
        "show_command_output": "Fa0/1 is assigned to VLAN 20 instead of VLAN 10.",
        "expected_fault": "Access port is assigned to the wrong VLAN.",
        "osi_layer": "Layer 2 — Data Link",
        "concept": "Access VLAN assignment",
        "severity": "High",
        "verification_command": "ping 192.168.10.1",
        "verification_result": "Expected successful connectivity after moving Fa0/1 to VLAN 10.",
    },
    {
        "case_id": "C005",
        "issue_type": "Interface",
        "symptom": "A connected PC cannot communicate with the network.",
        "topology_note": "PC1 connects to SW1 Fa0/1.",
        "show_command": "show interfaces status",
        "show_command_output": "Fa0/1 is administratively down.",
        "expected_fault": "The switch access interface is shutdown.",
        "osi_layer": "Layer 1 — Physical",
        "concept": "Interface administrative state",
        "severity": "High",
        "verification_command": "show interfaces status",
        "verification_result": "Expected Fa0/1 connected after enabling the interface.",
    },
    {
        "case_id": "C006",
        "issue_type": "Trunk",
        "symptom": "Hosts in one VLAN cannot reach the router while another VLAN works.",
        "topology_note": "SW1 Gi0/1 connects to R1 Gi0/0 using router-on-a-stick.",
        "show_command": "show interfaces trunk",
        "show_command_output": "Gi0/1 is trunking but VLAN 20 is absent from allowed VLANs.",
        "expected_fault": "Required VLAN is missing from the trunk allowed list.",
        "osi_layer": "Layer 2 — Data Link",
        "concept": "802.1Q trunking",
        "severity": "High",
        "verification_command": "ping 192.168.20.10",
        "verification_result": "Expected successful connectivity after allowing VLAN 20.",
    },
    {
        "case_id": "C007",
        "issue_type": "Routing",
        "symptom": "A remote network is unreachable although local connectivity works.",
        "topology_note": "R1 has a directly connected LAN and a remote routed network.",
        "show_command": "show ip route",
        "show_command_output": "No route exists for the remote destination network.",
        "expected_fault": "Required static route is missing.",
        "osi_layer": "Layer 3 — Network",
        "concept": "Static routing",
        "severity": "High",
        "verification_command": "show ip route",
        "verification_result": "Expected remote route to appear after configuration.",
    },
    {
        "case_id": "C008",
        "issue_type": "DHCP",
        "symptom": "A client receives no usable IPv4 address from DHCP.",
        "topology_note": "Client is connected to a LAN served by a Cisco DHCP pool.",
        "show_command": "show ip dhcp pool",
        "show_command_output": "DHCP pool exists but the configured network does not match the client LAN.",
        "expected_fault": "DHCP pool network is incorrectly configured.",
        "osi_layer": "Layer 3 — Network",
        "concept": "DHCP addressing",
        "severity": "High",
        "verification_command": "show ip dhcp binding",
        "verification_result": "Expected client lease after correcting the pool.",
    },
    {
        "case_id": "C009",
        "issue_type": "DNS",
        "symptom": "A client can ping an IP address but cannot resolve a hostname.",
        "topology_note": "Client has network connectivity to the DNS server.",
        "show_command": "ipconfig /all",
        "show_command_output": "DNS server address is missing or incorrect.",
        "expected_fault": "Incorrect DNS server configuration on the client.",
        "osi_layer": "Layer 7 — Application",
        "concept": "DNS resolution",
        "severity": "Medium",
        "verification_command": "nslookup server.example",
        "verification_result": "Expected successful name resolution after correcting DNS.",
    },
    {
        "case_id": "C010",
        "issue_type": "ACL",
        "symptom": "A host can reach the gateway but traffic to a permitted server is blocked.",
        "topology_note": "R1 routes traffic between the client and server networks.",
        "show_command": "show access-lists",
        "show_command_output": "ACL contains a deny entry matching the server traffic.",
        "expected_fault": "ACL rule incorrectly blocks required traffic.",
        "osi_layer": "Layer 3/4",
        "concept": "Access control lists",
        "severity": "High",
        "verification_command": "show access-lists",
        "verification_result": "Expected permitted traffic after correcting ACL.",
    },
    {
        "case_id": "C011",
        "issue_type": "NAT",
        "symptom": "Inside hosts can reach the gateway but cannot reach an external network.",
        "topology_note": "R1 connects an inside LAN to an outside interface.",
        "show_command": "show ip nat translations",
        "show_command_output": "No translations are created for inside hosts.",
        "expected_fault": "NAT configuration is missing or incorrectly matched.",
        "osi_layer": "Layer 3 — Network",
        "concept": "Network address translation",
        "severity": "High",
        "verification_command": "show ip nat translations",
        "verification_result": "Expected translations after correcting NAT.",
    },
    {
        "case_id": "C012",
        "issue_type": "Wireless",
        "symptom": "Wireless client associates with the AP but cannot reach the internal network.",
        "topology_note": "Wireless client connects through an access point to the LAN.",
        "show_command": "show vlan brief",
        "show_command_output": "Wireless-facing VLAN mapping does not match the intended client VLAN.",
        "expected_fault": "Wireless VLAN mapping is incorrect.",
        "osi_layer": "Layer 2 — Data Link",
        "concept": "Wireless VLAN mapping",
        "severity": "High",
        "verification_command": "ping 192.168.30.1",
        "verification_result": "Expected successful gateway connectivity after correcting VLAN mapping.",
    },
]

# Expand the library with controlled variants.
base = list(cases)

for original in base:
    number = int(original["case_id"][1:])
    if number <= 12:
        for variant in range(1, 3):
            new_number = number + 12 * variant
            if new_number <= 32:
                copy = original.copy()
                copy["case_id"] = f"C{new_number:03d}"
                copy["symptom"] = (
                    original["symptom"]
                    + f" Variant {variant}: the affected service is intermittent."
                )
                copy["severity"] = (
                    "Medium" if original["severity"] == "High" else "Low"
                )
                cases.append(copy)

# Ensure unique IDs and exactly C002-C032.
unique = {}
for case in cases:
    unique[case["case_id"]] = case

cases = [
    unique[f"C{i:03d}"]
    for i in range(2, 33)
    if f"C{i:03d}" in unique
]

# Add generator-specific metadata.
for case in cases:
    case["packet_tracer_file"] = ""
    case["ai_root_cause"] = ""
    case["ai_confidence"] = ""
    case["ai_evidence"] = ""
    case["ai_next_command"] = ""
    case["ai_fix_steps"] = ""
    case["human_decision"] = ""
    case["human_correction"] = ""
    case["verification_status"] = "NOT_REVIEWED"
    case["evidence_source"] = "synthetic_lab_scenario"

# Preserve C001 if it already exists.
existing = []

if CASES_FILE.exists():
    with CASES_FILE.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        existing = list(reader)

existing_by_id = {row["case_id"]: row for row in existing}

for case in cases:
    existing_by_id[case["case_id"]] = case

rows = list(existing_by_id.values())

with CASES_FILE.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS)
    writer.writeheader()

    for row in rows:
        writer.writerow({field: row.get(field, "") for field in FIELDS})

EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

print(f"Dataset written to: {CASES_FILE}")
print(f"Total cases: {len(rows)}")
print("Synthetic cases added: C002-C032")