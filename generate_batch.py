"""
Batch-generate a signed Form 1008 for every soldier in the roster
(data/roster.xlsx or data/roster.csv). Useful for generating all forms for
a full course/unit at once instead of one at a time via the web page.

Usage:
    python generate_batch.py
"""
import sys

import config
import generator
import roster


def main():
    df = roster.load_roster()
    if df.empty:
        print(f"No roster found. Put a soldier list at {config.ROSTER_XLSX} or {config.ROSTER_CSV}.")
        sys.exit(1)

    ok, failed = 0, []
    for _, row in df.iterrows():
        try:
            path = f"{config.OUTPUT_DIR}/{generator.safe_filename(row['full_name'], row['personal_number'])}"
            generator.generate_form(row["full_name"], row["personal_number"], row["rank"], output_path=path)
            ok += 1
        except ValueError as e:
            failed.append((row["full_name"], str(e)))

    print(f"Generated {ok}/{len(df)} forms into {config.OUTPUT_DIR}/")
    if failed:
        print(f"Skipped {len(failed)}:")
        for name, err in failed:
            print(f"  - {name}: {err}")


if __name__ == "__main__":
    main()
