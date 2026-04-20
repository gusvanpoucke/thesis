import os
import sys
from main import check_parameters_wait_margin

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

wait_margins = [0.0, 0.01, 0.04, 0.1]
for wait_margin in wait_margins:
    # Results folder
    FOLDER = f"hpc_jobs/wait_margin_tests/wait_first/wait_margin_{str(wait_margin).replace('.', '_')}/"
    os.makedirs(FOLDER, exist_ok=True)

    check_parameters_wait_margin(dvrp_file, wait_margin, FOLDER, "wait_first")

print(f"Task {array_id}: Completed {dvrp_file}")
