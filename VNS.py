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


def calculate_fullness(capacity, demands, dynamic_routes, alpha, epsilon):
    absolute_fullness = 0.0
    for dynamic_route in dynamic_routes:
        fullness = sum(demands[customer] for customer in dynamic_route.full_route()) / capacity
        absolute_fullness += fullness ** (1.0 + epsilon)
    average_fullness = absolute_fullness / len(dynamic_routes)
    return 1.0 + (alpha * average_fullness)


def vns(initial_cost, initial_solution, capacity, adj_matrix, demands, simulation_time, working_day, durations,
    k_max, termination_time, min_iterations, theta, alpha, epsilon
):
    # build initial solution using Clarke and Wright savings algorithm
    current_cost, current_solution = initial_cost, initial_solution
    best_cost, best_solution = current_cost, deep_copy_routes(initial_solution)

    # calculate fullness of routes in memory
    current_fullness = calculate_fullness(capacity, demands, current_solution, alpha, epsilon)
    best_fullness = calculate_fullness(capacity, demands, best_solution, alpha, epsilon)

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
            repaired_cost, repaired_solution = repair(local_cost, capacity, adj_matrix, demands, simulation_time, working_day, durations, unshaked_routes, local_solution)
            # move to new solution if conditions are right
            repaired_fullness = calculate_fullness(capacity, demands, repaired_solution, alpha, epsilon)
            if move_or_not(min_iterations, theta, current_cost * current_fullness, repaired_cost * repaired_fullness, last_accepted):
                current_cost, current_solution, current_fullness = repaired_cost, repaired_solution, repaired_fullness
                k = 1
                last_accepted = 0
                # update best found solution
                if current_cost * current_fullness < best_cost * best_fullness:
                    best_cost, best_solution, best_fullness = current_cost, deep_copy_routes(current_solution), current_fullness
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
        capacity, adj_matrix, demands, 0.0, working_day, durations, k_max, termination_time, min_iterations, theta
    )


def wait_or_not(waiting_strategy, simulation_time, working_day, durations, adj_matrix, dynamic_route):
    if time_constraint_route(working_day, durations, adj_matrix, Route(dynamic_route.covered_route, dynamic_route.route, simulation_time)):
        if (
            (
                waiting_strategy == "wait_first"
            ) or
            (
                waiting_strategy == "max_dist" and
                len(dynamic_route.route) < len(dynamic_route.covered_route)
            ) or
            (
                waiting_strategy == "location" and
                len(dynamic_route.covered_route)/len(dynamic_route.full_route()) >= simulation_time/working_day
            )
        ):
            return True
    return False


def commit_next_time_period(adj_matrix, simulation_time, working_day, durations, time_period_length, current_solution,
    waiting_strategy, route_orientation_strategy
):
    # move all vehicles forward
    for dynamic_route in current_solution:
        # commit customers as long as the time period lasts
        while dynamic_route.processing_time < simulation_time and dynamic_route.route:
            # if possible, wait until next time period to commit next customer
            if wait_or_not(waiting_strategy, simulation_time, working_day, durations, adj_matrix, dynamic_route):
                dynamic_route.processing_time = simulation_time
                break
            # when first customer is committed, choose the closest one between first and last on route
            if not(dynamic_route.covered_route) and route_orientation_strategy == "closest_first":
                if adj_matrix[0][dynamic_route.route[-1]] < adj_matrix[0][dynamic_route.route[0]]:
                    dynamic_route.route = dynamic_route.route[::-1]
            committed_customer = dynamic_route.route.pop(0)
            dynamic_route.processing_time += adj_matrix[dynamic_route.start()][committed_customer]
            dynamic_route.processing_time += durations[committed_customer]
            dynamic_route.covered_route.append(committed_customer)
    return current_solution


def event_scheduler(n, capacity, adj_matrix, demands, working_day, durations, availabilities,
    k_max = 5, termination_time = 5, min_iterations = 500, theta = 0.05, cut_off=0.5, time_periods=25,
    waiting_strategy = "drive_first", route_orientation_strategy = "random", capacity_strategy = "normal", time_strategy="uniform",
    alpha = 0.0, epsilon = 0.0
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
        # reduce capacity early to force more routes
        reduced_capacity = capacity
        reduced_working_day = working_day
        if capacity_strategy == "reduce_capacity" and simulation_time/working_day < 0.4:
            reduction = 0.6 + simulation_time/working_day
            reduced_capacity = reduction * capacity
            reduced_working_day = reduction * working_day

        if simulation_time == 0:
            # find static customers
            static_customers = []
            for customer in range(1, n):
                if avail[customer] == 0:
                    static_customers.append(customer)
            new_customers_quantity = len(static_customers)
            # create initial solution
            current_cost, current_solution = dynamic_savings(
                static_customers,
                reduced_capacity, adj_matrix, demands,
                simulation_time, reduced_working_day,
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
            new_customers_quantity = len(new_customers)
            # add customers to current solution
            new_cost, new_routes = dynamic_savings(
                new_customers,
                reduced_capacity, adj_matrix, demands,
                simulation_time, reduced_working_day,
                durations
            )
            current_cost += new_cost
            current_solution = deep_copy_routes(current_solution) + new_routes
        
        # can't cross with only 1 route
        if len(current_solution) > 1:
            # divide time based on new customers
            altered_termination_time = termination_time
            if time_strategy == "new_customers":
                altered_termination_time = (termination_time * time_periods) * (new_customers_quantity / n)
            elif time_strategy == "uniform_new_customers":
                altered_termination_time = 0.0 if new_customers_quantity == 0 else termination_time / cut_off

            # calculate reduced alpha
            reduced_alpha = 0.0
            if simulation_time/working_day < 0.5:
                reduced_alpha = alpha - ((simulation_time/working_day) * 2 * alpha)

            # improve solution using VNS
            current_cost, current_solution = vns(current_cost, current_solution, reduced_capacity, adj_matrix, demands,
                simulation_time, reduced_working_day, durations, k_max, altered_termination_time, min_iterations, theta,
                reduced_alpha, epsilon
            )

        # commit next time period
        simulation_time += time_period_length
        current_solution = commit_next_time_period(
            adj_matrix,
            simulation_time, working_day,
            durations, time_period_length, current_solution,
            waiting_strategy, route_orientation_strategy
        )

        solution_list.append(deep_copy_routes(current_solution))
    
    return current_cost, solution_list
