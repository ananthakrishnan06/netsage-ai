import pandas as pd

from app.evaluator import expected_category


FILE = "data/cases.csv"


def main():

    df = pd.read_csv(FILE)

    correct = 0
    incorrect = 0
    review = 0

    for index, row in df.iterrows():

        expected = expected_category(
            str(row["expected_fault"])
        )

        predicted = str(
            row["ai_fault_category"]
        ).strip().upper()

        # Store the corrected expected category.
        df.at[index, "expected_category"] = expected

        # Compare categories directly.
        if (
            expected != "OTHER"
            and predicted == expected
        ):
            status = "Correct"
            score = 1.0
            correct += 1

        elif (
            expected == "OTHER"
            or predicted == "OTHER"
            or not predicted
        ):
            status = "Needs Review"
            score = 0.0
            review += 1

        else:
            status = "Incorrect"
            score = 0.0
            incorrect += 1

        df.at[index, "evaluation_score"] = score
        df.at[index, "evaluation_status"] = status

    df.to_csv(
        FILE,
        index=False
    )

    total = correct + incorrect + review

    print("=" * 60)
    print("NETSAGE V2 RE-EVALUATION")
    print("=" * 60)

    print(f"Total:          {total}")
    print(f"Correct:        {correct}")
    print(f"Incorrect:      {incorrect}")
    print(f"Needs Review:   {review}")

    if total:
        print(
            f"Accuracy:       {(correct / total) * 100:.2f}%"
        )

    print()
    print("Updated:", FILE)


if __name__ == "__main__":
    main()