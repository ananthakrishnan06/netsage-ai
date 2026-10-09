import pandas as pd

from app.ai_engine import run_local_ai
from app.evaluator import evaluate_case


FILE = "data/cases.csv"

df = pd.read_csv(FILE)

# Only evaluate cases that have not been evaluated yet.
remaining = df[df["evaluation_status"].isna()].copy()

print("=" * 60)
print("EVALUATING REMAINING CASES")
print("=" * 60)
print("Cases:", remaining["case_id"].tolist())
print()


# Make all columns writable.
df = df.astype(object)


for index, case in remaining.iterrows():

    case_id = case["case_id"]

    print("=" * 60)
    print(f"PROCESSING {case_id}")
    print("=" * 60)

    try:
        # Run local Qwen3.
        ai_response = run_local_ai(case.to_dict())

        # Evaluate response.
        result = evaluate_case(
            case.to_dict(),
            ai_response,
        )

        # Save result fields.
        for key, value in result.items():

            if key in df.columns:
                df.loc[index, key] = value

        print(
            f"{case_id}: "
            f"AI={result['ai_predicted_category']} | "
            f"Final={result['ai_fault_category']} | "
            f"Expected={result['expected_category']} | "
            f"Status={result['evaluation_status']}"
        )

    except Exception as e:

        print(f"ERROR processing {case_id}: {e}")

        # Do not write a fake evaluation.
        continue


# Save dataset.
df.to_csv(FILE, index=False)

print()
print("=" * 60)
print("REMAINING CASES EVALUATION COMPLETE")
print("=" * 60)