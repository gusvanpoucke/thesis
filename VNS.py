import time
from Clarke_and_Wright_savings import savings
from shake import shake
from local_search import local_search
from repair import repair
from evaluate import evaluate
from dynamic_route import Route

def move_or_not(min_iterations, theta, original_cost, new_cost, last_accepted):
    # always accept improving solution
    if new_cost < original_cost:
        return True
    if last_accepted >= min_iterations:
        if new_cost < original_cost * (1 + theta):
            return True
    return False


def vns(initial_cost, initial_solution, capacity, adj_matrix, demands, time_left, durations,
    k_max, termination_time, min_iterations, theta
):
    # build initial solution using Clarke and Wright savings algorithm
    current_cost, current_solution = initial_cost, initial_solution
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
            repaired_cost, repaired_solution = repair(local_cost, capacity, adj_matrix, demands, time_left, durations, unshaked_routes, local_solution)
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


def cvrp(n, capacity, adj_matrix, demands, working_day, durations, 
    k_max = 5, termination_time = 600, min_iterations = 500, theta = 0.05
):
    # build initial solution using Clarke and Wright savings algorithm
    initial_cost, initial_solution = savings(list(range(1, n)), capacity, adj_matrix, demands, working_day, durations)

    # do vns
    return vns(initial_cost, initial_solution,
        capacity, adj_matrix, demands, working_day, durations, k_max, termination_time, min_iterations, theta
    )


def event_scheduler(n, capacity, adj_matrix, demands, working_day, durations, availabilities,
    k_max = 5, termination_time = 5, min_iterations = 500, theta = 0.05, cut_off=0.5, time_periods=25
):
    simulation_time = 0
    time_period_length = working_day / time_periods

    while simulation_time < working_day:
        if simulation_time == 0:
            # find static customers
            static_customers = []
            for customer in range(1, n):
                if availabilities[customer] > working_day * cut_off:
                    static_customers.append(customer)
            # create initial solution
            current_cost, current_solution = savings(
                static_customers,
                capacity, adj_matrix, demands,
                working_day,
                durations
            )
        else:
            # find new customers in current time period
            new_customers = []
            for customer in range(1, n):
                if (availabilities[customer] >= simulation_time - time_period_length
                    and availabilities[customer] < simulation_time
                    and simulation_time <= working_day * cut_off
                ):
                    new_customers.append(customer)
            # add customers to current solution
            current_cost, current_solution = savings(
                new_customers,
                capacity, adj_matrix, demands,
                working_day - simulation_time,
                durations,
                initial_routes_cost=current_cost, initial_routes=current_solution
            )
        
        # can't cross with only 1 route
        if len(current_solution) > 1:
            # improve solution using VNS
            current_cost, current_solution = vns(current_cost, current_solution, capacity, adj_matrix, demands,
                working_day - simulation_time,
                durations, k_max, termination_time, min_iterations, theta
            )

        # move all vehicles forward
        for dynamic_route in current_solution:
            time_left = time_period_length - dynamic_route.duration_until_decision_point
            # commit customers as long as the time period lasts
            while time_left > 0:
                if dynamic_route.route:
                    committed_customer = dynamic_route.route.pop(0)
                    time_left -= adj_matrix[dynamic_route.start()][committed_customer]
                    time_left -= durations[committed_customer]
                    dynamic_route.covered_route.append(committed_customer)
                else:
                    # wait at last customer
                    time_left = 0.0
            dynamic_route.duration_until_decision_point = -time_left
        simulation_time += time_period_length

        print("Cost: " + str(current_cost))
        print("Time: " + str(simulation_time))
        for i, route in enumerate(current_solution):
            print("Route " + str(i))
            print("Covered route: " + str(route.covered_route))
            print("Route: " + str(route.route))
            print("Duration until decision point: " + str(route.duration_until_decision_point))
        print()
    
    return current_cost, current_solution
