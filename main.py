import numpy as np
import cProfile
import pstats
import json
import time
import os

from dynamic_programming import vrp as dynamic_programming
from shake import cross, shake
from evaluate import evaluate, check_capacity, check_all_customers_served, time_constraint_route, test_dynamic_solution
from local_search import local_search, two_opt_star
from VNS import cvrp, event_scheduler
from repair import repair, split_route
from dynamic_route import Route


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
    print("Capacity Check: " + check_capacity(capacity, demands, non_dynamic_routes))
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
        print("Capacity Check: " + check_capacity(capacity, demands, routes))
        print("Customer Check: " + check_all_customers_served(n_customers-1, routes))
        print("Check Incremental Evaluation: " + str(abs(cost - evaluate(weights, routes)) < 0.1))

        print()

def testOneDVRP():
    #FILEPATH = 'dvrp_data/toy_examples/toy6.json'
    #FILEPATH = 'dvrp_data/processed/tai75a.json'
    FILEPATH = 'dvrp_data/processed/c100.json'

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
    for route in routes[-1]:
        print("Check time route: " + str(time_constraint_route(working_day, durations, weights, route)))
        non_dynamic_routes.append(route.full_route())
    print("Routes: " + str(non_dynamic_routes))
    print("Capacity Check: " + str(check_capacity(capacity, demands, non_dynamic_routes)))
    print("Customer Check: " + str(check_all_customers_served(n_customers-1, non_dynamic_routes)))
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
        print("Capacity Check: " + check_capacity(capacity, demands, non_dynamic_routes))
        print("Customer Check: " + check_all_customers_served(n_customers-1, non_dynamic_routes))
        print("Check Incremental Evaluation: " + str(abs(cost - evaluate(weights, non_dynamic_routes)) < 0.1))

        print()

def runXTestsOnFile(file_name, number_of_tests=30, results_folder="experiment_results/standard_vns/"):
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
    json_filename = f"{results_folder}{data['graph_name'].replace(' ', '_')}.json"
    with open(json_filename, "w") as json_file:
        json.dump(data, json_file, indent=4)

def find_improving_solution(file_name, score_to_beat, solution_file=""):
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

    # run tests until improving solution is found
    tests_needed = 0
    while True:
        tests_needed += 1
        print("Test nr: " + str(tests_needed))
        cost, all_solutions = event_scheduler(n_customers, capacity, weights, demands, working_day, durations, availabilities)
        if cost < score_to_beat:
            break
    
    # write to file
    data = {
        "graph_name": graph_name,
        "tests_ran": tests_needed,
        "cost_found": cost,
        "supposed_best_cost": score_to_beat,
        "solutions": [
            {
                "routes": [
                    {
                        "covered_route": route.covered_route,
                        "route": route.route,
                        "processing_time": route.processing_time
                    }
                for route in solution]
            }
        for solution in all_solutions]
    }
    json_filename = solution_file if solution_file else f"experiment_results/{data['graph_name'].replace(' ', '_')}_solution.json"
    with open(json_filename, "w") as json_file:
        json.dump(data, json_file, indent=4)

def check_dynamic_solution(data_file, solution_file):
    FILEPATH = "dvrp_data/processed/" + data_file

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

    FILEPATH_SOLUTION = "experiment_results/" + solution_file

    with open(FILEPATH_SOLUTION, 'r') as file:
        SOLUTION = json.load(file)
    
    solutions = [
        [
            Route(
                covered_route=route_data["covered_route"],
                route=route_data["route"],
                processing_time=route_data["processing_time"]
            )
            for route_data in solution["routes"]
        ]
        for solution in SOLUTION["solutions"]
    ]

    print(test_dynamic_solution(capacity, demands, working_day, 25, durations, weights, availabilities, 0.5, solutions))

def total_costs(files, folder="experiment_results/standard_vns/"):
    total_best = 0.0
    total_average = 0.0
    for solution_file in files:
        FILEPATH = folder + solution_file

        with open(FILEPATH, 'r') as file:
            solution = json.load(file)
        
        total_best += solution['best_cost']
        total_average += solution['average_cost']
    
    return total_best, total_average, len(files)

if __name__ == "__main__":
    find_improving_solution("c50.json", 580, "experiment_results/c50_wait_first.json")
    """
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
    for dvrp_file in list_of_dvrp_files:
        runXTestsOnFile(dvrp_file, results_folder="experiment_results/wait_first_vns/")
    """
