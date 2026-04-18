import argparse

from main import compare_heuristics

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare heuristic to standard case")
    parser.add_argument(
        "heuristic_folder",
        help="Path to the heuristic folder to compare"
    )
    parser.add_argument(
        "comparison_folder",
        help="Path to the comparison folder"
    )
    
    args = parser.parse_args()
    
    compare_heuristics(args.heuristic_folder, args.comparison_folder)
    print(f"Comparison complete. Results saved to {args.heuristic_folder}compare_heuristics.json")
