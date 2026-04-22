import os
import sys
from main import check_parameters_reduce_capacity

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

wait_margin = 0.08
starting_capacities = [0.8, 0.85, 0.9, 0.95]
full_capacity_times = [0.4, 0.5, 0.6]
for starting_capacity in starting_capacities:
    for full_capacity_time in full_capacity_times:
        # Results folder
        FOLDER = f"hpc_jobs/reduce_capacity_parameters/wait_margin_{str(wait_margin).replace('.', '_')}/starting_capacity_{str(starting_capacity).replace('.', '_')}_full_capacity_time_{str(full_capacity_time).replace('.', '_')}/"
        os.makedirs(FOLDER, exist_ok=True)

        check_parameters_reduce_capacity(dvrp_file, starting_capacity, full_capacity_time, FOLDER, "wait_first", wait_margin=wait_margin)

print(f"Task {array_id}: Completed {dvrp_file}")
