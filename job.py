import os

from main import runXTestsOnFile

# 21 files
list_of_dvrp_files = [
    "c100.json",
    "c100b.json", 
    "c120.json",
    "c150.json",
    "c199.json",
    "c50.json",
    "c75.json",
    "f134.json",
    "f71.json",
    "tai100a.json",
    "tai100b.json",
    "tai100c.json",
    "tai100d.json",
    "tai150a.json",
    "tai150b.json",
    "tai150c.json",
    "tai150d.json",
    "tai75a.json",
    "tai75b.json",
    "tai75c.json",
    "tai75d.json"
]

FOLDER = "hpc_jobs/wait_first_vns/"
os.makedirs(FOLDER, exist_ok=True)
for dvrp_file in list_of_dvrp_files:
    runXTestsOnFile(dvrp_file, results_folder=FOLDER, waiting_strategy="wait_first")
