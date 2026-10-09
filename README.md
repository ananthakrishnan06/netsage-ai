# NetSage AI — Applied AI + Network Troubleshooting

## 1. Project Overview

NetSage AI is an AI-assisted Cisco network troubleshooting helper for Packet Tracer and lab scenarios.

The project takes a networking symptom together with topology notes and `show`-command output, then produces a likely fault category, root cause, OSI layer, evidence, next diagnostic command, and safe fix.

A human reviewer remains responsible for accepting or correcting every diagnosis before a fix is accepted.

The project follows the problem statement requirements for:
- A troubleshooting case dataset
- Evidence-backed AI diagnosis
- Structured prompt templates
- A deterministic Python rule checker
- Human review
- Responsible AI correction logging
- A dashboard and demonstration

## 2. Project Status

Final dataset:
- Total cases: **42**
- Unique case IDs: **42**
- Duplicate case IDs: **0**
- Final correct cases: **40**
- Final incorrect cases: **2**
- Final verified accuracy: **95.24%**
- Human-corrected AI cases: **5**

The dashboard also records the raw Qwen3 results available for 15 cases:
- Raw Qwen3 correct: **10**
- Raw Qwen3 accuracy: **66.67%**

The five documented human corrections are:

| Case | AI prediction | Human correction |
|---|---|---|
| C003 | IP_ADDRESS | SUBNET_MASK |
| C015 | IP_ADDRESS | SUBNET_MASK |
| C027 | DEFAULT_GATEWAY | SUBNET_MASK |
| C036 | VLAN_ASSIGNMENT | ACL |
| C044 | ACL | SUBNET_MASK |

## 3. Problem Scope

The cases cover Cisco-style troubleshooting categories including:
- VLAN assignment
- Default gateway
- Subnet mask
- Interface shutdown
- 802.1Q trunk VLAN propagation
- Static routing
- DHCP
- DNS
- ACL
- NAT
- Wireless/VLAN scenarios

The case records contain symptoms, topology notes, diagnostic command output, expected faults, OSI layer, networking concept, severity, verification information, AI output, and human-review information.

## 4. Architecture

```text
                    +----------------------+
                    |   Troubleshooting    |
                    |       Case           |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Structured Prompt    |
                    | diagnose_prompt.md   |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Groq API              |
                    | Cloud AI Diagnosis    |
                    +----------+-----------+
                               |
                 +-------------+-------------+
                 |                           |
                 v                           v
       +------------------+        +------------------+
       | AI Diagnosis     |        | Python Rule      |
       | root cause       |        | Checker         |
       | evidence         |        | deterministic   |
       | next command     |        | checks          |
       | safe fix         |        +------------------+
       +--------+---------+
                |
                v
       +----------------------+
       | Human Review         |
       | Accepted / Edited / |
       | Rejected             |
       +----------+-----------+
                  |
                  v
       +----------------------+
       | Fix + Verification   |
       +----------+-----------+
                  |
                  v
       +----------------------+
       | cases.csv +          |
       | correction log +     |
       | dashboard            |
       +----------------------+
```

## 5. Repository Structure

```text
D:\cisco project│
├── app│   ├── ai_engine.py
│   ├── evaluator.py
│   └── ...
│
├── data│   ├── cases.csv
│   ├── cases_final.csv
│   ├── responsible_ai_corrections.csv
│   ├── responsible_ai_corrections_final.csv
│   └── NetSage_Final_Dashboard.xlsx
│
├── prompts│   ├── diagnose_prompt.md
│   └── human_review_template.md
│
├── README.md
└── project scripts
```

## 6. AI Model

The AI workflow uses the Groq API with:

```text
qwen/qwen3.8-27b
```

Set `GROQ_API_KEY` in your environment (or create `.env` from `.env.example`).
Set `GROQ_MODEL` only if you want to override the default model. The model is
used for diagnosis rather than autonomous network configuration.

The AI response contains:
- Fault category
- Root cause
- OSI layer
- Networking concept
- Confidence
- Evidence
- Next diagnostic command
- Safe fix

## 7. Prompt Library

The main prompt is:

```text
prompts/diagnose_prompt.md
```

It defines:
- Input fields
- Diagnostic reasoning rules
- Fault-category taxonomy
- Confidence guidance
- Evidence requirements
- Next-command requirements
- Safe-fix requirements
- Human-review requirements
- Worked examples

The human-review template is:

```text
prompts/human_review_template.md
```

It records the AI diagnosis, human decision, correction, reason, evidence, and verification.

## 8. Case Dataset

The final dataset is:

```text
data/cases_final.csv
```

Each case includes fields for:
- Case ID
- Issue type
- Symptom
- Topology note
- Show command
- Show command output
- Expected fault
- OSI layer
- Concept
- Severity
- Packet Tracer file/reference
- Verification command
- Verification result
- AI root cause
- AI confidence
- AI evidence
- AI next command
- AI fix steps
- Human decision
- Human correction
- Verification status
- Evidence source
- Evaluation score
- Evaluation status
- Expected category
- AI category
- Rule category

## 9. AI Diagnosis Workflow

A typical workflow is:

1. Load a case from the dataset.
2. Provide the symptom, topology notes, and diagnostic evidence to Qwen3.
3. Parse the AI diagnosis.
4. Compare the AI result against the known expected category.
5. Compare with deterministic rule-based checks where available.
6. Present the diagnosis for human review.
7. Record `Accepted`, `Edited`, or `Rejected`.
8. If edited, record the human correction and supporting reason.
9. Apply a safe fix only after review.
10. Verify the result using the appropriate command or test.
11. Save the evaluation result.

## 10. Human-in-the-Loop Safety

NetSage AI is a decision-support system, not an autonomous network configuration system.

The model does not have authority to directly change the network.

Human review is required before accepting a diagnosis or fix.

Review decisions are:

```text
Accepted
Edited
Rejected
```

For an edited diagnosis, the project records:
- Original AI prediction
- Human correction
- Correction reason
- Supporting evidence
- Final verification

## 11. Real Packet Tracer Demonstrations

Two important real Packet Tracer cases were manually created from the baseline:

### C043 — ACL fault

PC1 could reach its VLAN 10 gateway but could not reach the VLAN 20 server.

The router configuration contained an ACL denying:

```text
192.168.10.10 -> 192.168.20.10
```

Qwen3 correctly diagnosed the case as:

```text
ACL
```

### C044 — Subnet-mask fault

PC1 was configured with:

```text
IP Address: 192.168.10.10
Subnet Mask: 255.255.0.0
Default Gateway: 192.168.10.1
```

PC1 could reach the gateway but could not reach another host in VLAN 10.

The actual fault was:

```text
SUBNET_MASK
```

Qwen3 predicted:

```text
ACL
```

A human reviewer corrected it to:

```text
SUBNET_MASK
```

This became the fifth documented human correction.

## 12. Responsible AI Evaluation

The project deliberately records model mistakes rather than hiding them.

Five cases required human correction:

```text
C003  IP_ADDRESS      -> SUBNET_MASK
C015  IP_ADDRESS      -> SUBNET_MASK
C027  DEFAULT_GATEWAY -> SUBNET_MASK
C036  VLAN_ASSIGNMENT -> ACL
C044  ACL             -> SUBNET_MASK
```

The correction log is:

```text
data/responsible_ai_corrections_final.csv
```

This provides evidence that the AI is used with human oversight.

## 13. Dashboard

The final dashboard is:

```text
data/NetSage_Final_Dashboard.xlsx
```

It contains:
- Total cases
- Correct/incorrect cases
- Final verified accuracy
- Human corrections
- Fault-category distribution
- Severity distribution
- Raw Qwen3 evaluation summary
- Responsible AI correction summary
- Full case results
- Full correction records

## 14. Final Results

```text
Total cases              42
Unique cases             42
Duplicates                0

Final correct             40
Final incorrect            2
Final accuracy        95.24%

Human corrections         5
```

The two final incorrect AI diagnoses are preserved as model errors rather than being overwritten:

```text
C036: VLAN_ASSIGNMENT -> ACL
C044: ACL -> SUBNET_MASK
```

## 15. Running the Project

Create/activate the Python virtual environment and configure a Groq API key:

```powershell
Copy-Item .env.example .env
```

Then set `GROQ_API_KEY` in `.env`. The default model is:

```text
qwen/qwen3.8-27b
```

Start the NetSage web interface from the project directory:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.web:app --reload
```

Open `http://127.0.0.1:8000` in your browser. The web console serves the case
diagnosis and operational analytics screens. Human review submissions are
appended to `data/human_reviews.jsonl`; the finalized case CSV is left intact.

Run project scripts from:

```text
D:\cisco project
```

Example AI evaluation:

```powershell
python -c "import pandas as pd; from app.ai_engine import run_groq_ai; from app.evaluator import evaluate_case; df=pd.read_csv('data/cases.csv'); c=df[df.case_id=='C043'].iloc[0].to_dict(); r=run_groq_ai(c); print(r); print(evaluate_case(c,r))"
```

Do not run scripts that regenerate all AI evaluations against the frozen final dataset unless a new evaluation is intentionally being performed. The final reviewed results should remain preserved.

## 16. Final Files for Submission

The important final artifacts are:

```text
data/cases_final.csv
data/responsible_ai_corrections_final.csv
data/NetSage_Final_Dashboard.xlsx
prompts/diagnose_prompt.md
prompts/human_review_template.md
README.md
```

Packet Tracer demonstration files should also be included when available, especially:

```text
NetSage_Lab01_Baseline.pkt
NetSage_Lab01_C043_ACL_Fault.pkt
NetSage_Lab01_C044_SubnetMask_Fault.pkt
```

## 17. Limitations

- Qwen3 can produce plausible but incorrect diagnoses.
- The deterministic rule checker does not cover every possible networking fault.
- Some cases are lab/synthetic scenarios rather than live production networks.
- Packet Tracer behavior and supported IOS commands can differ from physical Cisco devices.
- Human review remains necessary before accepting remediation.
- The final accuracy is based on the evaluated dataset and should not be interpreted as production-network accuracy.

## 18. Project Principle

The central design principle is:

```text
AI suggests.
Evidence supports.
Rules verify where possible.
Humans decide.
Verification confirms.
```

NetSage AI is therefore designed as an AI-assisted troubleshooting tool with human oversight rather than an autonomous network-change system.
