import os
from multiprocessing import Pool
from main import find_improving_solution

list_of_dvrp_files = [
    "c100.json", "c100b.json", "c120.json", "c150.json", "c199.json",
    "c50.json", "c75.json", "f134.json", "f71.json", "tai100a.json",
    "tai100b.json", "tai100c.json", "tai100d.json", "tai150a.json",
    "tai150b.json", "tai150c.json", "tai150d.json", "tai75a.json",
    "tai75b.json", "tai75c.json", "tai75d.json"
]

FOLDER = "hpc_jobs/parallel_test/"
os.makedirs(FOLDER, exist_ok=True)

def process_file(dvrp_file):
    print(f"Processing {dvrp_file}")
    find_improving_solution(dvrp_file, solution_file=f"{FOLDER}{dvrp_file}")
    return f"Completed {dvrp_file}"

with Pool(processes=int(os.environ.get('PBS_NUM_PPN', 21))) as pool:
    results = pool.map(process_file, list_of_dvrp_files)

for result in results:
    print(result)
