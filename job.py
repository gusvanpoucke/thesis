import os
import sys
from main import find_improving_solution

# Your 21 files in order
list_of_dvrp_files = [
    "c100.json", "c100b.json", "c120.json", "c150.json", "c199.json",
    "c50.json", "c75.json", "f134.json", "f71.json", "tai100a.json",
    "tai100b.json", "tai100c.json", "tai100d.json", "tai150a.json",
    "tai150b.json", "tai150c.json", "tai150d.json", "tai75a.json",
    "tai75b.json", "tai75c.json", "tai75d.json"
]

# Get array ID from command line argument
array_id = int(sys.argv[1])

# Get the file for this task
dvrp_file = list_of_dvrp_files[array_id]

# Results folder
FOLDER = "hpc_jobs/parallel_test/"
os.makedirs(FOLDER, exist_ok=True)

# Run the function
print(f"Task {array_id}: Processing {dvrp_file}")
find_improving_solution(dvrp_file, solution_file=f"{FOLDER}{dvrp_file}")
print(f"Task {array_id}: Completed {dvrp_file}")
