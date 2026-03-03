import numpy as np
import cProfile
import pstats
import json
import time
import os

from dynamic_programming import vrp as dynamic_programming
from Clarke_and_Wright_savings import savings
from shake import cross, shake
from evaluate import evaluate, check_capacity, check_all_customers_served
from local_search import local_search, two_opt_star
from VNS import vns
from repair import repair, split_route


def testOne():
    #FILEPATH = 'cvrp_data/toy_examples/Toy-n6-k2.json'
    FILEPATH = 'cvrp_data/processed/CMT/CMT4.json'
    #FILEPATH = 'cvrp_data/processed/X/X-n979-k58.json'

    with open(FILEPATH, 'r') as file:
        VRP = json.load(file)

    print(VRP['graph_name'])
    print(VRP['solution'])
    n_vehicles = VRP['k']
    n_customers = VRP['n']
    weights = np.array(VRP['weights'])
    demands = np.array(VRP['demands'])
    capacity = VRP['capacity']

    # Savings algorithm
    t = time.time()
    savings_cost, _ = savings(n_customers, capacity, weights, demands)
    print("Savings cost: " + str(savings_cost))
    print("Time(s): " + str(time.time() - t))

    # VNS algorithm
    t = time.time()
    cost, routes = vns(n_customers, capacity, weights, demands)
    print("VNS cost: " + str(cost))
    print("Time(s): " + str(time.time() - t))
    print("Capacity Check: " + check_capacity(capacity, weights, demands, routes))
    print("Customer Check: " + check_all_customers_served(n_customers-1, routes))
    print("Check Incremental Evaluation: " + str(abs(cost - evaluate(weights, routes)) < 0.1))

    print()


def testFolder(test_folder):
    print("Running on folder " + test_folder)
    files = os.listdir(test_folder)
    print("Folder contains " + str(len(files)) + " files")

    for file_name in files:
        with open(test_folder + "/" + file_name, 'r') as file:
            VRP = json.load(file)
        print(VRP['graph_name'])
        print("Best Known: " + str(VRP['solution']['cost']))
        print()
        
        n_vehicles = VRP['k']
        n_customers = VRP['n']
        weights = np.array(VRP['weights'])
        demands = np.array(VRP['demands'])
        capacity = VRP['capacity']

        # Savings algorithm
        t = time.time()
        savings_cost, _ = savings(n_customers, capacity, weights, demands)
        print("Savings cost: " + str(savings_cost))
        print("Time(s): " + str(time.time() - t))

        # VNS algorithm
        t = time.time()
        cost, routes = vns(n_customers, capacity, weights, demands)
        print("VNS cost: " + str(cost))
        print("Time(s): " + str(time.time() - t))
        print("Capacity Check: " + check_capacity(capacity, weights, demands, routes))
        print("Customer Check: " + check_all_customers_served(n_customers-1, routes))
        print("Check Incremental Evaluation: " + str(abs(cost - evaluate(weights, routes)) < 0.1))

        print()


if __name__ == "__main__":
    #testOne()
    testFolder("cvrp_data/processed/CMT")
