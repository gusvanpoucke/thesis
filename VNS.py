import time
import math
from Clarke_and_Wright_savings import dynamic_savings
from shake import shake
from local_search import local_search
from repair import repair, split_route
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


def calculate_fullness(capacity, demands, dynamic_routes, alpha, epsilon, fullness_strategy):
    absolute_fullness = 0.0
    max_fullness = 0.0
    for dynamic_route in dynamic_routes:
        fullness = sum(demands[customer] for customer in dynamic_route.full_route()) / capacity
        absolute_fullness += fullness ** (1.0 + epsilon)
        max_fullness = max(max_fullness, fullness)
    average_fullness = absolute_fullness / len(dynamic_routes)

    if fullness_strategy == "epsilon":
        return 1.0 + (alpha * average_fullness)
    elif fullness_strategy == "max":
        return 1.0 + (alpha * max_fullness)
    return 1.0


def vns(initial_cost, initial_solution, capacity, adj_matrix, demands, simulation_time, working_day, durations,
    k_max, termination_time, min_iterations, theta, alpha, epsilon, fullness_strategy
):
    # build initial solution using Clarke and Wright savings algorithm
    current_cost, current_solution = initial_cost, initial_solution
    best_cost, best_solution = current_cost, deep_copy_routes(initial_solution)

    # calculate fullness of routes in memory
    current_fullness = calculate_fullness(capacity, demands, current_solution, alpha, epsilon, fullness_strategy)
    best_fullness = calculate_fullness(capacity, demands, best_solution, alpha, epsilon, fullness_strategy)

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
            repaired_fullness = calculate_fullness(capacity, demands, repaired_solution, alpha, epsilon, fullness_strategy)
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


def wait_or_not(waiting_strategy, simulation_time, working_day, durations, capacity, adj_matrix, demands, dynamic_route, margin, margin_strategy):
    # calculate relative margin
    time_in_route = 0.0
    prev = 0
    for customer in dynamic_route.full_route():
        time_in_route += adj_matrix[prev][customer] + durations[customer]
        prev = customer
    time_in_route += adj_matrix[prev][0]
    capacity_fullness = sum(demands[customer] for customer in dynamic_route.full_route()) / capacity
    relative_margin = (time_in_route / capacity_fullness) * (1.0 - capacity_fullness)

    if (
        margin_strategy == "absolute" and
        time_constraint_route(
            working_day * (1.0 - margin), durations, adj_matrix,
            Route(dynamic_route.covered_route, dynamic_route.route, simulation_time)
        )
    ) or (
        margin_strategy == "relative" and
        time_constraint_route(
            working_day - relative_margin, durations, adj_matrix,
            Route(dynamic_route.covered_route, dynamic_route.route, simulation_time)
        )
    ):
        if (
            (
                waiting_strategy == "wait_first"
            ) or
            (
                waiting_strategy == "depot" and
                len(dynamic_route.covered_route) == 0
            ) or
            (
                waiting_strategy == "max_dist" and
                max([adj_matrix[0][c] for c in dynamic_route.covered_route], default=0.0) >
                max([adj_matrix[0][c] for c in dynamic_route.route], default=0.0)
            ) or
            (
                waiting_strategy == "spread" and
                len(dynamic_route.covered_route)/len(dynamic_route.full_route()) >= simulation_time/working_day
            )
        ):
            return True
    return False


def commit_next_time_period(capacity, adj_matrix, demands, simulation_time, working_day, durations, angles, time_period_length, current_solution,
    waiting_strategy, route_orientation_strategy, margin, margin_strategy
):
    # move all vehicles forward
    for dynamic_route in current_solution:
        # commit customers as long as the time period lasts
        while dynamic_route.processing_time < simulation_time and dynamic_route.route:
            # if possible, wait until next time period to commit next customer
            if wait_or_not(
                waiting_strategy, simulation_time, working_day,
                durations, capacity, adj_matrix, demands,
                dynamic_route, margin, margin_strategy
            ):
                dynamic_route.processing_time = simulation_time
                break
        
            # when first customer is committed, choose the closest one between first and last on route
            if not(dynamic_route.covered_route) and route_orientation_strategy == "closest_first":
                if adj_matrix[0][dynamic_route.route[-1]] < adj_matrix[0][dynamic_route.route[0]]:
                    dynamic_route.route = dynamic_route.route[::-1]
            
            # when first customer is committed, traverse route in clockwise order
            if not(dynamic_route.covered_route) and route_orientation_strategy == "clockwise":
                if ((angles[dynamic_route.route[-1]] - angles[dynamic_route.route[0]]) % (2 * math.pi)) < math.pi:
                    dynamic_route.route = dynamic_route.route[::-1]
            committed_customer = dynamic_route.route.pop(0)
            dynamic_route.processing_time += adj_matrix[dynamic_route.start()][committed_customer]
            dynamic_route.processing_time += durations[committed_customer]
            dynamic_route.covered_route.append(committed_customer)
    return current_solution


def initial_routes(capacity, adj_matrix, demands, working_day, durations, angles, time_period_length,
    current_cost, current_solution, initial_routes_strategy
):
    if initial_routes_strategy == "split_routes":
        new_routes = []
        for dynamic_route in current_solution:
            split_cost, route1, route2 = split_route(adj_matrix, dynamic_route.route)
            current_cost += split_cost
            new_routes.append(Route([], route1, 0.0))
            new_routes.append(Route([], route2, 0.0))
        return current_cost, commit_next_time_period(
            adj_matrix, 0.1, working_day, durations, angles, time_period_length,
            new_routes,
            "drive_first", "random", 0.0
        )
    elif initial_routes_strategy == "VIP_list":
        # determine vips
        n_vips = len(current_solution) * 2
        customers = [customer for dynamic_route in current_solution for customer in dynamic_route.route]
        customers_with_distance = [(adj_matrix[0][customer], customer) for customer in customers]
        vips = [customer for _, customer in sorted(customers_with_distance)[:n_vips]]
        
        # each vip gets a route
        vip_routes = []
        vip_cost = 0.0
        for vip in vips:
            vip_routes.append(Route([vip], [], adj_matrix[0][vip] + durations[vip]))
            vip_cost += 2 * adj_matrix[0][vip]
        
        # put other customers on routes
        other_cost, other_routes = dynamic_savings(
            [customer for customer in customers if customer not in vips],
            capacity, adj_matrix, demands,
            0.0, working_day,
            durations
        )
        return vip_cost + other_cost, vip_routes + other_routes
    return current_cost, current_solution


def event_scheduler(n, capacity, adj_matrix, demands, working_day, durations, availabilities, angles,
    k_max = 5, termination_time = 5, min_iterations = 500, theta = 0.05, cut_off=0.5, time_periods=25,
    waiting_strategy = "drive_first", route_orientation_strategy = "random", time_strategy="uniform", fullness_strategy="epsilon",
    alpha = 0.0, epsilon = 0.0, starting_capacity = 1.0, full_capacity_time = 0.0, wait_margin = 0.0,
    initial_routes_strategy = "regular", margin_strategy = "absolute"
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
        if simulation_time/working_day < full_capacity_time:
            reduction = starting_capacity + (simulation_time/working_day) * (1 - starting_capacity) / full_capacity_time
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
            # execute initial routes strategy
            current_cost, current_solution = initial_routes(
                reduced_capacity, adj_matrix, demands, reduced_working_day, durations, angles, time_period_length,
                current_cost, current_solution, initial_routes_strategy
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
                reduced_alpha, epsilon, fullness_strategy
            )

        # commit next time period
        simulation_time += time_period_length
        current_solution = commit_next_time_period(
            capacity, adj_matrix, demands,
            simulation_time, working_day,
            durations, angles, time_period_length, current_solution,
            waiting_strategy, route_orientation_strategy,
            wait_margin, margin_strategy
        )

        solution_list.append(deep_copy_routes(current_solution))
    
    return current_cost, solution_list
