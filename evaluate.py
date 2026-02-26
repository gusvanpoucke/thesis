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


def capacity_constraint_route(capacity, demands, route):
    return sum(demands[customer] for customer in route) <= capacity


def check_capacity(capacity, adj_matrix, demands, routes):
    # CHECK capacity
    for route in routes:
        if not capacity_constraint_route(capacity, demands, route):
            return "Capacity constraint violated"

    return "Routes are valid"

def check_all_customers_served(customers, routes):
    if sum(len(sl) for sl in routes) < customers:
        return "Some customers missing"
    if sum(len(sl) for sl in routes) > customers:
        return "Too many customers???"
    return "All customers served"
    