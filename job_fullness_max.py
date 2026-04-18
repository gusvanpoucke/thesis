import os
import sys
from main import check_parameters_max_fullness

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

# Run the function
print(f"Task {array_id}: Processing {dvrp_file}")

alphas = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
for alpha in alphas:
    # Results folder
    FOLDER = f"hpc_jobs/fullness_parameters/max/drive_first/alpha_{str(alpha).replace('.', '_')}/"
    os.makedirs(FOLDER, exist_ok=True)

    check_parameters_max_fullness(dvrp_file, alpha, FOLDER, "drive_first")

print(f"Task {array_id}: Completed {dvrp_file}")
