import argparse
import json

# Your 21 files in order
list_of_dvrp_files = [
    "c100.json", "c100b.json", "c120.json", "c150.json", "c199.json",
    "c50.json", "c75.json", "f134.json", "f71.json", "tai100a.json",
    "tai100b.json", "tai100c.json", "tai100d.json", "tai150a.json",
    "tai150b.json", "tai150c.json", "tai150d.json", "tai75a.json",
    "tai75b.json", "tai75c.json", "tai75d.json"
]

def compare_heuristics(heuristic_folder, comparison_folder):
    count_improved = 0
    total_relative_improvement = 0.0
    for dvrp_file in list_of_dvrp_files:
        heuristic_file = heuristic_folder + dvrp_file
        comparison_file = comparison_folder + dvrp_file

        with open(heuristic_file, 'r') as file:
            heuristic_average = json.load(file)['average_cost']
        with open(comparison_file, 'r') as file:
            comparison_average = json.load(file)['average_cost']

        if heuristic_average < comparison_average:
            count_improved += 1
        total_relative_improvement += heuristic_average / comparison_average
    average_relative_improvement = total_relative_improvement / len(list_of_dvrp_files)

    # write to file
    data = {
        "heuristic": heuristic_folder,
        "comparison": comparison_folder,
        "count_improved": count_improved,
        "average_relative_improvement": average_relative_improvement
    }
    json_filename = f"{heuristic_folder}_compare_heuristics.json"
    with open(json_filename, "w") as json_file:
        json.dump(data, json_file, indent=4)

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
