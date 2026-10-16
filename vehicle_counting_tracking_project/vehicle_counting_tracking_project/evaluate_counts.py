import argparse
import os
import pandas as pd


def main():
    parser = argparse.ArgumentParser(description="Compare automatic vehicle counts with manual ground truth.")
    parser.add_argument("--input", default="manual_counts.csv")
    parser.add_argument("--output", default="outputs/count_error_report.csv")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        raise FileNotFoundError(
            f"Cannot find {args.input}. Create it using the example columns: "
            "clip,method,direction,count"
        )

    df = pd.read_csv(args.input)
    required = {"clip", "method", "direction", "count"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing columns: {sorted(missing)}")

    df["count"] = pd.to_numeric(df["count"], errors="raise")
    manual = df[df["method"].str.lower() == "manual"][["clip", "direction", "count"]].rename(
        columns={"count": "manual_count"}
    )
    automatic = df[df["method"].str.lower() != "manual"].rename(columns={"count": "automatic_count"})
    report = automatic.merge(manual, on=["clip", "direction"], how="left")
    report["absolute_error"] = (report["automatic_count"] - report["manual_count"]).abs()
    report["percentage_error"] = (
        report["absolute_error"] / report["manual_count"].replace({0: pd.NA}) * 100
    )
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    report.to_csv(args.output, index=False)
    print(report.to_string(index=False))
    print(f"\nSaved report to: {args.output}")


if __name__ == "__main__":
    main()
