import numpy as np
import cProfile
import pstats
import json
import time
import os

from dynamic_programming import vrp as dynamic_programming
from Clarke_and_Wright_savings import savings
from shake import cross, shake
from evaluate import evaluate, check_capacity, check_all_customers_served, time_constraint_route
from local_search import local_search, two_opt_star
from VNS import cvrp, event_scheduler
from repair import repair, split_route


def testOneCVRP():
    #FILEPATH = 'cvrp_data/toy_examples/Toy-n6-k2.json'
    FILEPATH = 'cvrp_data/processed/CMT/CMT4.json'
    #FILEPATH = 'cvrp_data/processed/X/X-n979-k58.json'

    with open(FILEPATH, 'r') as file:
        VRP = json.load(file)

    print(VRP['graph_name'])
    print(VRP['solution'])
    n_customers = VRP['n']
    weights = np.array(VRP['weights'])
    demands = np.array(VRP['demands'])
    capacity = VRP['capacity']

    # Savings algorithm
    t = time.time()
    savings_cost, _ = savings(list(range(1, n_customers)), capacity, weights, demands)
    print("Savings cost: " + str(savings_cost))
    print("Time(s): " + str(time.time() - t))

    # VNS algorithm
    t = time.time()
    cost, routes = cvrp(n_customers, capacity, weights, demands, 1000000000, [0]*n_customers, termination_time=5)
    print("VNS cost: " + str(cost))
    print("Time(s): " + str(time.time() - t))
    non_dynamic_routes = []
    for route in routes:
        non_dynamic_routes.append(route.route)
    print("Capacity Check: " + check_capacity(capacity, weights, demands, non_dynamic_routes))
    print("Customer Check: " + check_all_customers_served(n_customers-1, non_dynamic_routes))
    print("Check Incremental Evaluation: " + str(abs(cost - evaluate(weights, non_dynamic_routes)) < 0.1))

    print()

def testFolderCVRP(test_folder):
    print("Running on folder " + test_folder)
    files = os.listdir(test_folder)
    print("Folder contains " + str(len(files)) + " files")

    for file_name in files:
        with open(test_folder + "/" + file_name, 'r') as file:
            VRP = json.load(file)
        print(VRP['graph_name'])
        print("Best Known: " + str(VRP['solution']['cost']))
        print()
        
        n_customers = VRP['n']
        weights = np.array(VRP['weights'])
        demands = np.array(VRP['demands'])
        capacity = VRP['capacity']

        # Savings algorithm
        t = time.time()
        savings_cost, _ = savings(list(range(1, n_customers)), capacity, weights, demands)
        print("Savings cost: " + str(savings_cost))
        print("Time(s): " + str(time.time() - t))

        # VNS algorithm
        t = time.time()
        cost, routes = cvrp(n_customers, capacity, weights, demands)
        print("VNS cost: " + str(cost))
        print("Time(s): " + str(time.time() - t))
        print("Capacity Check: " + check_capacity(capacity, weights, demands, routes))
        print("Customer Check: " + check_all_customers_served(n_customers-1, routes))
        print("Check Incremental Evaluation: " + str(abs(cost - evaluate(weights, routes)) < 0.1))

        print()

def testOneDVRP():
    #FILEPATH = 'dvrp_data/toy_examples/toy6.json'
    FILEPATH = 'dvrp_data/processed/c120.json'

    with open(FILEPATH, 'r') as file:
        VRP = json.load(file)

    print(VRP['graph_name'])
    n_customers = VRP['n']
    weights = np.array(VRP['weights'])
    demands = np.array(VRP['demands'])
    capacity = VRP['capacity']
    durations = np.array(VRP['durations'])
    working_day = VRP['working_day']
    availabilities = np.array(VRP['availabilities'])

    # VNS algorithm
    t = time.time()
    cost, routes = event_scheduler(n_customers, capacity, weights, demands, working_day, durations, availabilities)
    print("VNS cost: " + str(cost))
    print("Time(s): " + str(time.time() - t))
    non_dynamic_routes = []
    for route in routes:
        print("Check time route: " + str(time_constraint_route(working_day, durations, weights, route)))
        non_dynamic_routes.append(route.full_route())
    print("Routes: " + str(non_dynamic_routes))
    print("Capacity Check: " + check_capacity(capacity, weights, demands, non_dynamic_routes))
    print("Customer Check: " + check_all_customers_served(n_customers-1, non_dynamic_routes))
    print("Check Incremental Evaluation: " + str(abs(cost - evaluate(weights, non_dynamic_routes)) < 0.1))

    print()

def testAllDVRP():
    print("Running on all DVRP")
    files = os.listdir("dvrp_data/processed")
    print("Folder contains " + str(len(files)) + " files")

    for file_name in files:
        with open("dvrp_data/processed/" + file_name, 'r') as file:
            VRP = json.load(file)

        print(VRP['graph_name'])
        n_customers = VRP['n']
        weights = np.array(VRP['weights'])
        demands = np.array(VRP['demands'])
        capacity = VRP['capacity']
        durations = np.array(VRP['durations'])
        working_day = VRP['working_day']
        availabilities = np.array(VRP['availabilities'])

        # VNS algorithm
        t = time.time()
        cost, routes = event_scheduler(n_customers, capacity, weights, demands, working_day, durations, availabilities)
        print("VNS cost: " + str(cost))
        print("Time(s): " + str(time.time() - t))
        non_dynamic_routes = []
        for route in routes:
            print("Check time route: " + str(time_constraint_route(working_day, durations, weights, route)))
            non_dynamic_routes.append(route.full_route())
        print("Routes: " + str(non_dynamic_routes))
        print("Capacity Check: " + check_capacity(capacity, weights, demands, non_dynamic_routes))
        print("Customer Check: " + check_all_customers_served(n_customers-1, non_dynamic_routes))
        print("Check Incremental Evaluation: " + str(abs(cost - evaluate(weights, non_dynamic_routes)) < 0.1))

        print()

def runXTestsOnFile(file_name, number_of_tests=30):
    FILEPATH = "dvrp_data/processed/" + file_name

    with open(FILEPATH, 'r') as file:
        VRP = json.load(file)

    graph_name = VRP['graph_name']
    print(graph_name)
    n_customers = VRP['n']
    weights = np.array(VRP['weights'])
    demands = np.array(VRP['demands'])
    capacity = VRP['capacity']
    durations = np.array(VRP['durations'])
    working_day = VRP['working_day']
    availabilities = np.array(VRP['availabilities'])

    # run 30 tests
    best_cost = 1000000000000.0
    total_cost = 0.0
    for i in range(number_of_tests):
        cost, _ = event_scheduler(n_customers, capacity, weights, demands, working_day, durations, availabilities)
        best_cost = min(best_cost, cost)
        total_cost += cost
    
    # write to file
    data = {
        "graph_name": graph_name,
        "tests_ran": number_of_tests,
        "best_cost": best_cost,
        "average_cost": total_cost/number_of_tests
    }
    json_filename = f"experiment_results/{data['graph_name'].replace(' ', '_')}.json"
    with open(json_filename, "w") as json_file:
        json.dump(data, json_file, indent=4)

if __name__ == "__main__":
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
        "tai385.json",
        "tai75a.json",
        "tai75b.json",
        "tai75c.json",
        "tai75d.json"
    ]
    for dvrp_file in list_of_dvrp_files:
        runXTestsOnFile(dvrp_file)

    #testOneDVRP()
    #testAllDVRP()
    #testOneCVRP()
    #testFolderCVRP("cvrp_data/processed/CMT")
