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

def check_parameters(file_name, alpha, epsilon, results_folder="experiment_results/fullness_parameters/",
    number_of_tests=30, waiting_strategy="wait_first", termination_time=5
):
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
    angles = np.array(VRP['angles'])

    tests = []

    # run X tests
    best_cost = 1000000000000.0
    total_cost = 0.0
    for i in range(number_of_tests):
        cost, _ = event_scheduler(n_customers, capacity, weights, demands, working_day, durations, availabilities, angles,
            waiting_strategy=waiting_strategy,
            termination_time=termination_time,
            alpha=alpha, epsilon=epsilon
        )
        best_cost = min(best_cost, cost)
        total_cost += cost

    # record results
    data = {
        "graph_name": graph_name,
        "number_of_tests": number_of_tests,
        "waiting_strategy": waiting_strategy,
        "termination_time": termination_time,
        "alpha": alpha,
        "epsilon": epsilon,
        "best_cost": best_cost,
        "average_cost": total_cost/number_of_tests
    }
    json_filename = results_folder + waiting_strategy + "/alpha_" + str(alpha).replace('.', '_') + "_epsilon_" + str(epsilon).replace('.', '_') + ".json"
    with open(json_filename, "w") as json_file:
        json.dump(data, json_file, indent=4)


def tune_parameters(file_name, list_of_alphas, list_of_epsilons, results_folder="experiment_results/fullness_parameters/",
    number_of_tests=30, waiting_strategy="wait_first", termination_time=5
):
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
    angles = np.array(VRP['angles'])

    tests = []

    # run a test for every combination of alpha and epsilon
    for alpha in list_of_alphas:
        for epsilon in list_of_epsilons:
            # run X tests
            best_cost = 1000000000000.0
            total_cost = 0.0
            for i in range(number_of_tests):
                cost, _ = event_scheduler(n_customers, capacity, weights, demands, working_day, durations, availabilities, angles,
                    waiting_strategy=waiting_strategy,
                    termination_time=termination_time,
                    alpha=alpha, epsilon=epsilon
                )
                best_cost = min(best_cost, cost)
                total_cost += cost

            # record results
            tests.append({
                "alpha": alpha,
                "epsilon": epsilon,
                "best_cost": best_cost,
                "average_cost": total_cost/number_of_tests
            })
    
    # write to file
    data = {
        "graph_name": graph_name,
        "number_of_tests": number_of_tests,
        "waiting_strategy": waiting_strategy,
        "termination_time": termination_time,
        "tests": tests
    }
    json_filename = results_folder + waiting_strategy + "/" + data['graph_name'].replace(' ', '_') + ".json"
    with open(json_filename, "w") as json_file:
        json.dump(data, json_file, indent=4)

def runXTestsOnFile(file_name, number_of_tests=30, results_folder="experiment_results/", results_file="",
    waiting_strategy="drive_first", route_orientation_strategy="random", capacity_strategy="normal", time_strategy="uniform"
):
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
    angles = np.array(VRP['angles'])

    # run 30 tests
    best_cost = 1000000000000.0
    total_cost = 0.0
    for i in range(number_of_tests):
        cost, _ = event_scheduler(n_customers, capacity, weights, demands, working_day, durations, availabilities, angles,
            waiting_strategy=waiting_strategy,
            route_orientation_strategy=route_orientation_strategy,
            capacity_strategy=capacity_strategy,
            time_strategy=time_strategy
        )
        best_cost = min(best_cost, cost)
        total_cost += cost
    
    # write to file
    data = {
        "graph_name": graph_name,
        "tests_ran": number_of_tests,
        "best_cost": best_cost,
        "average_cost": total_cost/number_of_tests
    }
    if results_file:
        json_filename = results_folder + results_file
    else:
        json_filename = results_folder + data['graph_name'].replace(' ', '_') + ".json"
    with open(json_filename, "w") as json_file:
        json.dump(data, json_file, indent=4)

def find_improving_solution(file_name, score_to_beat=100000000000000000000, solution_file="",
    waiting_strategy="drive_first", route_orientation_strategy="random", capacity_strategy="normal", time_strategy="uniform",
    alpha=0.0, epsilon=0.0
):
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
    angles = np.array(VRP['angles'])

    # run tests until improving solution is found
    tests_needed = 0
    while True:
        tests_needed += 1
        print("Test nr: " + str(tests_needed))
        cost, all_solutions = event_scheduler(n_customers, capacity, weights, demands, working_day, durations, availabilities, angles,
            waiting_strategy=waiting_strategy,
            route_orientation_strategy=route_orientation_strategy,
            capacity_strategy=capacity_strategy,
            time_strategy=time_strategy,
            alpha=alpha, epsilon=epsilon
        )
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
    json_filename = solution_file if solution_file else "experiment_results/" + data['graph_name'].replace(' ', '_') + "_solution.json"
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
    alphas = [2.0, 4.0, 6.0, 8.0, 10.0]
    epsilons = [0.0, 1.0, 2.0, 3.0, 4.0]
    for alpha in alphas:
        for epsilon in epsilons:
            if alpha <= 6.0 or alpha == 8.0 and epsilon <= 1.0:
                continue
            print(alpha, epsilon)
            check_parameters("c150.json", alpha, epsilon)
            print()
