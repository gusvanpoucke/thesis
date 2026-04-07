import time
from Clarke_and_Wright_savings import dynamic_savings
from shake import shake
from local_search import local_search
from repair import repair
from evaluate import evaluate, time_constraint_route
from dynamic_route import Route


def deep_copy_routes(routes):
    return [route.copy() for route in routes]


def move_or_not(min_iterations, theta, original_cost, new_cost, last_accepted):
    # always accept improving solution
    if new_cost < original_cost:
        return True
    if last_accepted >= min_iterations:
        if new_cost < original_cost * (1 + theta):
            return True
    return False


def vns(initial_cost, initial_solution, capacity, adj_matrix, demands, working_day, durations,
    k_max, termination_time, min_iterations, theta
):
    # build initial solution using Clarke and Wright savings algorithm
    current_cost, current_solution = initial_cost, initial_solution
    best_cost, best_solution = current_cost, deep_copy_routes(initial_solution)

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
            repaired_cost, repaired_solution = repair(local_cost, capacity, adj_matrix, demands, working_day, durations, unshaked_routes, local_solution)
            # move to new solution if conditions are right
            if move_or_not(min_iterations, theta, current_cost, repaired_cost, last_accepted):
                current_cost, current_solution = repaired_cost, repaired_solution
                k = 1
                last_accepted = 0
                # update best found solution
                if current_cost < best_cost:
                    best_cost, best_solution = current_cost, deep_copy_routes(current_solution)
            # if no better solution found, move to next neighbourhood
            else:
                k += 1
                last_accepted += 1

    return best_cost, best_solution


def cvrp(n, capacity, adj_matrix, demands, working_day, durations, 
    k_max = 5, termination_time = 600, min_iterations = 500, theta = 0.05
):
    # build initial solution using Clarke and Wright savings algorithm
    initial_cost, initial_solution = savings(list(range(1, n)), capacity, adj_matrix, demands, 0.0, working_day, durations)

    # do vns
    return vns(initial_cost, initial_solution,
        capacity, adj_matrix, demands, working_day, durations, k_max, termination_time, min_iterations, theta
    )


def commit_next_time_period(adj_matrix, simulation_time, working_day, durations, time_period_length, current_solution):
    # move all vehicles forward
    for dynamic_route in current_solution:
        # commit customers as long as the time period lasts
        while dynamic_route.processing_time < simulation_time and dynamic_route.route:
            if time_constraint_route(working_day, durations, adj_matrix,
                Route(dynamic_route.covered_route, dynamic_route.route, simulation_time)
            ):
                dynamic_route.processing_time = simulation_time
                break
            committed_customer = dynamic_route.route.pop(0)
            dynamic_route.processing_time += adj_matrix[dynamic_route.start()][committed_customer]
            dynamic_route.processing_time += durations[committed_customer]
            dynamic_route.covered_route.append(committed_customer)
    return current_solution


def event_scheduler(n, capacity, adj_matrix, demands, working_day, durations, availabilities,
    k_max = 5, termination_time = 5, min_iterations = 500, theta = 0.05, cut_off=0.5, time_periods=25
):
    # calculate actual availabilities based on cut off time
    avail = []
    for availability in availabilities:
        if availability >= working_day * cut_off:
            avail.append(0)
        else:
            avail.append(availability)

    simulation_time = 0 # time at end of current time period
    time_period_length = working_day / time_periods
    solution_list = []

    while simulation_time < working_day:
        if simulation_time == 0:
            # find static customers
            static_customers = []
            for customer in range(1, n):
                if avail[customer] == 0:
                    static_customers.append(customer)
            # create initial solution
            current_cost, current_solution = dynamic_savings(
                static_customers,
                capacity, adj_matrix, demands,
                simulation_time, working_day,
                durations
            )
        else:
            # find new customers in previous time period
            new_customers = []
            for customer in range(1, n):
                if (avail[customer] >= simulation_time - (time_period_length * 2)
                    and avail[customer] < simulation_time - time_period_length
                    and avail[customer] != 0
                ):
                    new_customers.append(customer)
            # add customers to current solution
            new_cost, new_routes = dynamic_savings(
                new_customers,
                capacity, adj_matrix, demands,
                simulation_time, working_day,
                durations
            )
            current_cost += new_cost
            current_solution = deep_copy_routes(current_solution) + new_routes
        
        # can't cross with only 1 route
        if len(current_solution) > 1:
            # improve solution using VNS
            current_cost, current_solution = vns(current_cost, current_solution, capacity, adj_matrix, demands,
                working_day, durations, k_max, termination_time, min_iterations, theta
            )

        # commit next time period
        simulation_time += time_period_length
        current_solution = commit_next_time_period(
            adj_matrix,
            simulation_time, working_day,
            durations, time_period_length, current_solution
        )

        solution_list.append(deep_copy_routes(current_solution))
    
    return current_cost, solution_list
