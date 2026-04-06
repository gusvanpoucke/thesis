def evaluate_route(adj_matrix, route):
    cost = 0.0
    prev = 0
    for customer in route:
        cost += adj_matrix[prev][customer]
        prev = customer
    cost += adj_matrix[prev][0]
    return cost


def evaluate(adj_matrix, routes):
    cost = 0.0
    for route in routes:
        cost += evaluate_route(adj_matrix, route)
    return cost


def check_constraints(capacity, demands, time_left, durations, adj_matrix, dynamic_route):
    return (
        capacity_constraint_route(capacity, demands, dynamic_route.full_route())
        and time_constraint_route(time_left, durations, adj_matrix, dynamic_route)
    ) or not(dynamic_route.route)


def capacity_constraint_route(capacity, demands, route):
    return sum(demands[customer] for customer in route) <= capacity


def time_constraint_route(time_left, durations, adj_matrix, dynamic_route):
    if dynamic_route.duration_until_decision_point == 0.0 and not(dynamic_route.route):
        return True

    time_spent = dynamic_route.duration_until_decision_point
    prev = dynamic_route.start()
    for customer in dynamic_route.route:
        time_spent += adj_matrix[prev][customer] + durations[customer]
        prev = customer
    time_spent += adj_matrix[prev][0]
    return time_spent <= time_left


def check_capacity(capacity, demands, routes):
    return all([capacity_constraint_route(capacity, demands, route) for route in routes])


def check_time(time_left, durations, adj_matrix, dynamic_routes):
    return all([time_constraint_route(time_left, durations, adj_matrix, dynamic_route) for dynamic_route in dynamic_routes])


def check_customers(availabilities, simulation_time, half_way, customers_served):
    for customer, availability in enumerate(availabilities):
        if customer != 0 and customer not in customers_served and (availability < simulation_time or availability >= half_way):
            return False
    for customer in customers_served:
        if availabilities[customer] != 0 and availabilities[customer] >= simulation_time and availabilities[customer] < half_way:
            return False
    return True


def check_all_customers_served(customers, routes):
    if sum(len(sl) for sl in routes) < customers:
        return "Some customers missing"
    if sum(len(sl) for sl in routes) > customers:
        return "Too many customers???"
    return "All customers served"
    

def test_dynamic_solution(capacity, demands, working_day, time_periods, durations, adj_matrix, availabilities, cut_off, solutions):
    # test every solution individually
    for time_period, dynamic_routes in enumerate(solutions):
        # CHECK CAPACITIES
        routes = [route.full_route() for route in dynamic_routes]
        if not(check_capacity(capacity, demands, routes)):
            return "Capacity Fail"
        # CHECK TIME CONSTRAINTS
        time_left = (working_day / time_periods) * (time_periods - time_period - 1)
        if not(check_time(time_left, durations, adj_matrix, dynamic_routes)):
            return "Time Fail in time period " + str(time_period)
        # CHECK ALL CUSTOMERS PRESENT
        simulation_time = (working_day / time_periods) * (time_period - 1)
        customers_served = [customer for route in routes for customer in route]
        half_way = working_day * cut_off
        if not(check_customers(availabilities, simulation_time, half_way, customers_served)):
            return "Customer Fail in time period " + str(time_period)
    return "Solution Correct with cost: " + str(evaluate(adj_matrix, routes))
