import argparse
import json
import os

# Your 21 files in order
list_of_dvrp_files = [
    "c100.json", "c100b.json", "c120.json", "c150.json", "c199.json",
    "c50.json", "c75.json", "f134.json", "f71.json", "tai100a.json",
    "tai100b.json", "tai100c.json", "tai100d.json", "tai150a.json",
    "tai150b.json", "tai150c.json", "tai150d.json", "tai75a.json",
    "tai75b.json", "tai75c.json", "tai75d.json"
]
VNS_best_cost = [
    943.87,
    883.91,
    1219.73,
    1253.66,
    1538.87,
    592.60,
    940.25,
    14559.58,
    273.08,
    2134.95,
    2126.68,
    1517.57,
    1807.86,
    3274.78,
    2819.46,
    2491.58,
    2927.21,
    1833.18,
    1460.65,
    1558.05,
    1428.74
]
VNS_average_cost = [
    985.94,
    910.67,
    1319.39,
    1323.40,
    1608.40,
    618.44,
    994.89,
    15423.87,
    291.21,
    2246.88,
    2204.05,
    1650.93,
    1950.62,
    3408.89,
    2902.42,
    2643.11,
    3006.04,
    1913.51,
    1496.77,
    1616.87,
    1452.73
]

def vns_folder():
    for i, dvrp_file in enumerate(list_of_dvrp_files):
        FILEPATH = "dvrp_data/processed/" + dvrp_file

        with open(FILEPATH, 'r') as file:
            VRP = json.load(file)

        graph_name = VRP['graph_name']
        # write to file
        data = {
            "graph_name": graph_name,
            "tests_ran": 30,
            "best_cost": VNS_best_cost[i],
            "average_cost": VNS_average_cost[i]
        }
        json_filename = f"hpc_jobs/sarasola_vns/{dvrp_file}"
        with open(json_filename, "w") as json_file:
            json.dump(data, json_file, indent=4)

if __name__ == "__main__":
    vns_folder()