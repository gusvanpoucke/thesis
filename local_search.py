import random
from evaluate import evaluate, evaluate_route, capacity_constraint_route

def two_opt_try(adj_matrix, route):
    route_cost = evaluate_route(adj_matrix, route)
    # iterate over all lengths of segment to invert in a random order
    for length in random.sample(range(2, len(route)+1), len(route)-1):
        # iterate over all starting points of segment to invert in a random order
        for start in random.sample(range(len(route)-length+1), len(route)-length+1):
            new_route = route[:start] + list(reversed(route[start:start+length])) + route[start+length:]
            # if improvement found, restart local search
            if evaluate_route(adj_matrix, new_route) < route_cost:
                return new_route
    return []


def two_opt(adj_matrix, routes):
    new_solution = []
    # iterate over all routes
    for i, route in enumerate(routes):
        # try 2-opt moves until no more improvement possible
        new_route = route
        while new_route:
            current_route = new_route
            new_route = two_opt_try(adj_matrix, current_route)
        new_solution.append(current_route)
    return new_solution


def two_opt_star_try(adj_matrix, routes):
    # iterate over all routes for route 1
    for i, route1 in enumerate(routes):
        route1_cost = evaluate_route(adj_matrix, route1)
        # iterate over all routes for route 2
        for x, route2 in enumerate(routes[i+1:]):
            j = x+i+1
            route2_cost = evaluate_route(adj_matrix, route2)
            # iterate over all starting points in route 1 in a random order
            for start1 in random.sample(range(len(route1)+1), len(route1)+1):
                # iterate over all starting points in route 2 in a random order
                for start2 in random.sample(range(len(route2)+1), len(route2)+1):
                    new_route1 = route1[:start1] + route2[start2:]
                    new_route2 = route2[:start2] + route1[start1:]
                    new_route1_cost = evaluate_route(adj_matrix, new_route1)
                    new_route2_cost = evaluate_route(adj_matrix, new_route2)
                    # if improvement found, restart local search
                    if new_route1_cost + new_route2_cost < route1_cost + route2_cost:
                        new_routes = routes[:i] + [new_route1] + routes[i+1:j] + [new_route2] + routes[j+1:]
                        # remove empty routes
                        return [r for r in new_routes if r]
    return []


def two_opt_star(adj_matrix, current_solution):
    # try 2-opt* moves until no more improvement possible
    new_solution = current_solution
    while new_solution:
        current_solution = new_solution
        new_solution = two_opt_star_try(adj_matrix, current_solution)
    return current_solution


def local_search(adj_matrix, routes):
    current_solution = routes
    current_solution = two_opt(adj_matrix, current_solution)
    current_solution = two_opt_star(adj_matrix, current_solution)
    return current_solution
