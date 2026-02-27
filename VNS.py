import time
from Clarke_and_Wright_savings import savings
from shake import shake
from local_search import local_search
from evaluate import evaluate
from repair import repair

def move_or_not(adj_matrix, min_iterations, theta, original_solution, new_solution, last_accepted):
    # always accept improving solution
    if evaluate(adj_matrix, new_solution) < evaluate(adj_matrix, original_solution):
        return True
    if last_accepted >= min_iterations:
        if evaluate(adj_matrix, new_solution) < evaluate(adj_matrix, original_solution) * (1 + theta):
            return True
    return False


def vns(n, capacity, adj_matrix, demands, k_max = 5, termination_time = 600, min_iterations = 500, theta = 0.05):
    # build initial solution using Clarke and Wright savings algorithm
    _, current_solution = savings(n, capacity, adj_matrix, demands)
    best_solution = current_solution

    last_accepted = 0
    # terminate after maximum time used
    start_time = time.process_time()
    while time.process_time() - start_time < termination_time:
        # iterate over neighbourhoods
        k = 1
        while k < k_max:
            # shake solution
            unshaked_routes, shaked_routes = shake(adj_matrix, current_solution, k)
            # optimize solution locally
            local_solution = unshaked_routes + local_search(adj_matrix, shaked_routes)
            # repair incumbent solution
            repaired_solution = repair(capacity, adj_matrix, demands, local_solution)
            # move to new solution if conditions are right
            if move_or_not(adj_matrix, min_iterations, theta, current_solution, repaired_solution, last_accepted):
                current_solution = repaired_solution
                k = 1
                last_accepted = 0
                # update best found solution
                if evaluate(adj_matrix, current_solution) < evaluate(adj_matrix, best_solution):
                    best_solution = current_solution
            # if no better solution found, move to next neighbourhood
            else:
                k += 1
                last_accepted += 1
    
    return evaluate(adj_matrix, best_solution), best_solution
