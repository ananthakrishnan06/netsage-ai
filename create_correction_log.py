import pandas as pd

INPUT_FILE = "data/cases.csv"
OUTPUT_FILE = "data/responsible_ai_corrections.csv"

df = pd.read_csv(INPUT_FILE)

# Select every case that was actually reviewed and edited.
corrections = df[
    df["human_decision"].astype(str).str.strip().str.lower() == "edited"
].copy()

# Build a clean Responsible AI correction log.
columns = [
    "case_id",
    "symptom",
    "expected_fault",
    "expected_category",
    "ai_predicted_category",
    "human_decision",
    "human_correction",
    "correction_reason",
    "ai_root_cause",
    "ai_evidence",
    "ai_next_command",
    "ai_fix_steps",
    "evaluation_score",
    "evaluation_status",
]

# Create correction reason for each edited case.
def make_reason(row):
    return (
        f"Qwen3 predicted {row['ai_predicted_category']}, "
        f"but human review determined the correct category was "
        f"{row['human_correction']} based on the diagnostic evidence."
    )


corrections["correction_reason"] = corrections.apply(
    make_reason,
    axis=1,
)

# Make sure every requested column exists.
for column in columns:
    if column not in corrections.columns:
        corrections[column] = ""

corrections = corrections[columns]

corrections.to_csv(
    OUTPUT_FILE,
    index=False,
)

print("=" * 60)
print("RESPONSIBLE AI CORRECTION LOG CREATED")
print("=" * 60)

print("Cases:", len(corrections))
print("Output:", OUTPUT_FILE)
print()

print(
    corrections[
        [
            "case_id",
            "ai_predicted_category",
            "human_correction",
            "human_decision",
        ]
    ].to_string(index=False)
)