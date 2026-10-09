import csv
import time
from pathlib import Path

from app.ai_engine import run_local_ai
from app.evaluator import evaluate_case


ROOT = Path(__file__).resolve().parent
CASES_FILE = ROOT / "data" / "cases.csv"


def load_cases():
    with CASES_FILE.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        return list(csv.DictReader(file))


def save_cases(cases):
    if not cases:
        return

    fieldnames = list(cases[0].keys())

    with CASES_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(cases)


def main():

    cases = load_cases()

    print("=" * 60)
    print("NETSAGE BATCH AI EVALUATION - V2")
    print("=" * 60)
    print()

    print(f"Total cases: {len(cases)}")
    print()

    correct = 0
    incorrect = 0
    review = 0
    errors = 0

    for index, case in enumerate(cases, start=1):

        case_id = case.get("case_id", "")

        print()
        print("-" * 60)
        print(f"[{index}/{len(cases)}] Processing {case_id}")
        print("-" * 60)

        try:

            print("Running Qwen3 8B...")

            ai_response = run_local_ai(case)

            print()
            print("=== AI RESPONSE ===")
            print(ai_response)

            result = evaluate_case(
                case,
                ai_response,
            )

            print()
            print("Expected category:")
            print(result["expected_category"])

            print("AI category:")
            print(result["ai_fault_category"])

            print("Evaluation:")
            print(result["evaluation_status"])

            print("Score:")
            print(result["evaluation_score"])

            # ----------------------------------------------
            # Save structured AI fields
            # ----------------------------------------------

            case["expected_category"] = result[
                "expected_category"
            ]

            case["ai_fault_category"] = result[
                "ai_fault_category"
            ]

            case["ai_root_cause"] = result[
                "ai_root_cause"
            ]

            case["ai_confidence"] = result[
                "ai_confidence"
            ]

            case["ai_evidence"] = result[
                "ai_evidence"
            ]

            case["ai_next_command"] = result[
                "ai_next_command"
            ]

            case["ai_fix_steps"] = result[
                "ai_fix_steps"
            ]

            case["evaluation_score"] = result[
                "evaluation_score"
            ]

            case["evaluation_status"] = result[
                "evaluation_status"
            ]

            # ----------------------------------------------
            # Count
            # ----------------------------------------------

            status = result[
                "evaluation_status"
            ]

            if status == "Correct":
                correct += 1

            elif status == "Incorrect":
                incorrect += 1

            else:
                review += 1

            # Save after every case.
            save_cases(cases)

            print()
            print("Saved.")

            time.sleep(1)

        except KeyboardInterrupt:

            print()
            print("Interrupted.")
            print("Saving progress...")

            save_cases(cases)

            break

        except Exception as error:

            errors += 1

            print()
            print("ERROR:")
            print(type(error).__name__)
            print(error)

            case["evaluation_status"] = "Error"

            save_cases(cases)

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    total_evaluated = (
        correct +
        incorrect +
        review
    )

    print()
    print()
    print("=" * 60)
    print("NETSAGE V2 EVALUATION SUMMARY")
    print("=" * 60)

    print()
    print(f"Total cases:        {len(cases)}")
    print(f"Evaluated:          {total_evaluated}")
    print(f"Correct:            {correct}")
    print(f"Incorrect:          {incorrect}")
    print(f"Needs Review:       {review}")
    print(f"Errors:             {errors}")

    if total_evaluated:
        accuracy = (
            correct /
            total_evaluated
        ) * 100

        print(
            f"Accuracy:           {accuracy:.2f}%"
        )

    print()
    print("Dataset:")
    print(CASES_FILE)


if __name__ == "__main__":
    main()