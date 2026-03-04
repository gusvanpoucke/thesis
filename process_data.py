import re
import math
import json
import os
from pathlib import Path
import numpy as np

RAW_CVRP_DATA = "cvrp_data/raw"
PROCESSED_CVRP_DATA = "cvrp_data/processed"

RAW_DVRP_DATA = "dvrp_data/raw"
PROCESSED_DVRP_DATA = "dvrp_data/processed"

def process_vrp(data_set):
    os.makedirs(f"{PROCESSED_CVRP_DATA}/{data_set}", exist_ok=True)
    vrp_files = Path(RAW_CVRP_DATA, data_set).rglob("*.vrp")
    for vrp_file_path in vrp_files:
        vrp_file = str(vrp_file_path)

        print(f"Processing: {vrp_file}")

        data = parse_vrp(vrp_file)
        sol_file = vrp_file.replace(".vrp", ".sol")
        solution = parse_sol(sol_file)

        if not solution:
            print(f"Error when parsing solution for {data['graph_name']}")
            continue

        data['k'] = len(solution['routes'])
        data['solution'] = solution

        json_filename = f"{PROCESSED_CVRP_DATA}/{data_set}/{data['graph_name'].replace(' ', '_')}.json"
        with open(json_filename, "w") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data saved to {json_filename}")
        print("--------------------------------------")
               

def process_dvrp():
    dat_files = Path(RAW_DVRP_DATA).rglob("*.dat")
    for dat_file_path in dat_files:
        dat_file = str(dat_file_path)

        print(f"Processing: {dat_file}")

        data = parse_dat(dat_file)

        json_filename = f"{PROCESSED_DVRP_DATA}/{data['graph_name'].replace(' ', '_')}.json"
        with open(json_filename, "w") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data saved to {json_filename}")
        print("--------------------------------------")


def parse_vrp(filepath):
    with open(filepath, 'r') as f:
        text = f.read()

    match = re.search(r"NAME\s*:\s*(\S.*)", text)
    graph_name = re.sub(r"\s+", " ", match.group(1)).strip() if match else None

    match = re.search(r"DIMENSION\s*:\s*(\S.*)", text)
    n = int(match.group(1)) if match else None

    match = re.search(r"CAPACITY\s*:\s*(\S.*)", text)
    capacity = int(match.group(1)) if match else None

    match = re.search(r"EDGE_WEIGHT_TYPE\s*:\s*(\S.*)", text)
    edge_weight_type = match.group(1) if match else None
    
    if not graph_name or not n or not capacity or not edge_weight_type:
        print(f"Some important values were not found for graph: {graph_name}, Skipping...")
        return
    
    print(f"Processing {graph_name}...")

    if edge_weight_type.strip() == "EXPLICIT":
        match = re.search(r"EDGE_WEIGHT_FORMAT\s*:\s*(\S.*)", text)
        edge_weight_format = match.group(1) if match else None
        
        if edge_weight_format.strip() != "LOWER_ROW":
            print(f"Non supported edge weight format for {graph_name}")
            return

        match = re.search(r"EDGE_WEIGHT_SECTION\s+([\d\s]+)\s+DEMAND_SECTION", text, re.DOTALL)
        if not match:
            print(f"Error for EDGE_WEIGHT_SECTION in graph {graph_name}")
            return
        lower_row = [int(num) for num in match.group(1).split()]
        
        distance_matrix = np.zeros((n, n))
        indices = np.tril_indices(n, k=-1)
        distance_matrix[indices] = lower_row
        distance_matrix += distance_matrix.T

    elif edge_weight_type.strip() == "EUC_2D":
        match = re.search(r"NODE_COORD_SECTION\s+([\d\s\.\-]+)\s+DEMAND_SECTION", text, re.DOTALL)
        if not match:
            print(f"Error for NODE_COORD_SECTION in graph {graph_name}")
            return
        
        coords = []
        for line in match.group(1).strip().split("\n"):
            parts = line.split()
            coords.append(tuple(map(float, parts[1:])))

        coords = np.array(coords)
        diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]
        distance_matrix = np.sqrt(np.sum(diff**2, axis=-1))

    else:
        print(f"Non supported EDGE_WEIGHT_TYPE: {edge_weight_type} for {graph_name}")
        return
    
    match = re.search(r"DEMAND_SECTION\s+([\d\s]+)\s+DEPOT_SECTION", text, re.DOTALL)
    if not match:
        print(f"Error for DEMAND_SECTION in graph {graph_name}")
        return
    
    demands = [int(getallen.strip().split()[1]) for getallen in match.group(1).split('\n')]

    data = {
        "graph_name": graph_name,
        "n": n,
        "capacity": capacity,
        "demands": demands,
        "weights": distance_matrix.tolist()
    }

    return data


def parse_sol(filepath):
    with open(filepath, 'r') as f:
        text = f.read()
    
    route_pattern = re.findall(r"Route #\d+: ([\d\s]+)", text)  # Extract routes
    cost_pattern = re.search(r"Cost ([\d.]+)", text)

    routes = [list(map(int, route.split())) for route in route_pattern]

    cost = float(cost_pattern.group(1)) if cost_pattern else None

    if not cost:
        return None
    
    return {'routes': routes, 'cost': cost}


def parse_dat(filepath):
    with open(filepath, 'r') as f:
        text = f.read()

    match = re.search(r"NAME\s*:\s*(\S.*)", text)
    graph_name = re.sub(r"\s+", " ", match.group(1)).strip() if match else None

    match = re.search(r"NUM_LOCATIONS\s*:\s*(\S.*)", text)
    n = int(match.group(1)) if match else None

    match = re.search(r"^[ \t]*CAPACITIES\s*:\s*(\S.*)", text, re.MULTILINE)
    capacity = int(match.group(1)) if match else None

    if not graph_name or not n or not capacity:
        print(f"Some important values were not found for graph: {graph_name}, Skipping...")
        return
    
    print(f"Processing {graph_name}...")

    # Parse demands - they are negative in the file, convert to positive
    match = re.search(r"DEMAND_SECTION\s+([\d\s\-]+)\s+LOCATION_COORD_SECTION", text, re.DOTALL)
    if not match:
        print(f"Error for DEMAND_SECTION in graph {graph_name}")
        return
    
    demands = [0] * n  # Index 0 is depot with demand 0
    for line in match.group(1).strip().split('\n'):
        parts = line.strip().split()
        if parts:
            node_id = int(parts[0])
            demand = abs(int(parts[1]))  # Convert negative to positive
            demands[node_id] = demand

    # Parse coordinates
    match = re.search(r"LOCATION_COORD_SECTION\s+([\d\s\.\-]+)\s+DEPOT_LOCATION_SECTION", text, re.DOTALL)
    if not match:
        print(f"Error for LOCATION_COORD_SECTION in graph {graph_name}")
        return
    
    coords = [None] * n
    for line in match.group(1).strip().split('\n'):
        parts = line.strip().split()
        if parts:
            node_id = int(parts[0])
            x = float(parts[1])
            y = float(parts[2])
            coords[node_id] = (x, y)

    coords = np.array(coords)
    diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]
    distance_matrix = np.sqrt(np.sum(diff**2, axis=-1))

    # Parse visit durations
    match = re.search(r"DURATION_SECTION\s+([\d\s\.]+)\s+DEPOT_TIME_WINDOW_SECTION", text, re.DOTALL)
    if not match:
        print(f"Error for DURATION_SECTION in graph {graph_name}")
        return
    
    durations = [0] * n  # Index 0 is depot with duration 0
    for line in match.group(1).strip().split('\n'):
        parts = line.strip().split()
        if parts:
            node_id = int(parts[0])
            duration = int(parts[1])
            durations[node_id] = duration

    # Parse working day length
    match = re.search(r"DEPOT_TIME_WINDOW_SECTION\s+([\d\s\.]+)\s+COMMENT", text, re.DOTALL)
    if not match:
        print(f"Error for DEPOT_TIME_WINDOW_SECTION in graph {graph_name}")
        return
    
    for line in match.group(1).strip().split('\n'):
        parts = line.strip().split()
        if parts:
            working_day = int(parts[2])

    # Parse availability times
    match = re.search(r"TIME_AVAIL_SECTION\s+([\d\s\.]+)\s+EOF", text, re.DOTALL)
    if not match:
        print(f"Error for TIME_AVAIL_SECTION in graph {graph_name}")
        return
    
    availabilities = [0] * n  # Index 0 is depot with availability 0
    for line in match.group(1).strip().split('\n'):
        parts = line.strip().split()
        if parts:
            node_id = int(parts[0])
            availability = int(parts[1])
            availabilities[node_id] = availability

    data = {
        "graph_name": graph_name,
        "n": n,
        "capacity": capacity,
        "demands": demands,
        "weights": distance_matrix.tolist(),
        "durations": durations,
        "working_day": working_day,
        "availabilities": availabilities
    }

    return data


if __name__ == "__main__":
    process_dvrp()
