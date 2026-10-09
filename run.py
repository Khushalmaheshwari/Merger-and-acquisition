"""Command-line entry point for the M&A analysis backend."""

import argparse
import json

from dotenv import load_dotenv

from ma_agents import run_analysis


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an academic M&A decision-support report.")
    parser.add_argument("--ticker", default="JINDALSTEL.NS", help="Yahoo Finance ticker for the target")
    parser.add_argument("--acquirer", default="Tata Steel")
    parser.add_argument("--target", default="Jindal Steel")
    parser.add_argument("--output", default="reports/analysis.json", help="JSON output path")
    args = parser.parse_args()
    load_dotenv()
    reports = run_analysis(args.ticker, args.acquirer, args.target)
    with open(args.output, "w", encoding="utf-8") as output_file:
        json.dump(reports, output_file, indent=2, ensure_ascii=False)
    print(f"Saved {len(reports)} reports to {args.output}")


if __name__ == "__main__":
    main()
