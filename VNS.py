import time
from Clarke_and_Wright_savings import savings
from shake import shake
from local_search import local_search
from repair import repair
from evaluate import evaluate

def move_or_not(min_iterations, theta, original_cost, new_cost, last_accepted):
    # always accept improving solution
    if new_cost < original_cost:
        return True
    if last_accepted >= min_iterations:
        if new_cost < original_cost * (1 + theta):
            return True
    return False


def vns(n, capacity, adj_matrix, demands, k_max = 5, termination_time = 600, min_iterations = 500, theta = 0.05):
    # build initial solution using Clarke and Wright savings algorithm
    current_cost, current_solution = savings(list(range(1, n)), capacity, adj_matrix, demands)
    best_cost, best_solution = current_cost, current_solution

    last_accepted = 0
    # terminate after maximum time used
    start_time = time.process_time()
    while time.process_time() - start_time < termination_time:
        # iterate over neighbourhoods
        k = 1
        while k < k_max:
            # shake solution
            shaked_cost, unshaked_routes, shaked_routes = shake(current_cost, adj_matrix, current_solution, k)
            # optimize crossed routes locally
            local_cost, local_solution = local_search(shaked_cost, adj_matrix, shaked_routes)
            # repair incumbent solution
            repaired_cost, repaired_solution = repair(local_cost, capacity, adj_matrix, demands, unshaked_routes, local_solution)
            # move to new solution if conditions are right
            if move_or_not(min_iterations, theta, current_cost, repaired_cost, last_accepted):
                current_cost, current_solution = repaired_cost, repaired_solution
                k = 1
                last_accepted = 0
                # update best found solution
                if current_cost < best_cost:
                    best_cost, best_solution = current_cost, current_solution
            # if no better solution found, move to next neighbourhood
            else:
                k += 1
                last_accepted += 1

    return best_cost, best_solution
