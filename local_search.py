import random
from modify_route import modify_route

def two_opt_try(adj_matrix, dynamic_route):
    route = dynamic_route.route
    # iterate over all lengths of segment to invert in a random order
    for length in random.sample(range(2, len(route)+1), len(route)-1):
        # iterate over all starting points of segment to invert in a random order
        for start in random.sample(range(len(route)-length+1), len(route)-length+1):
            cost_increment, new_route = modify_route(adj_matrix,
                route[:start], route[start:start+length], route[start+length:],
                list(reversed(route[start:start+length]))
            )
            # if improvement found, restart local search
            if cost_increment < 0:
                new_dynamic_route = dynamic_route.copy()
                new_dynamic_route.route = new_route
                return cost_increment, new_dynamic_route
    return 0, None


def two_opt(cost, adj_matrix, routes):
    new_solution = []
    # iterate over all routes
    for i, route in enumerate(routes):
        # try 2-opt moves until no more improvement possible
        new_route = route
        while new_route:
            current_route = new_route
            cost_increment, new_route = two_opt_try(adj_matrix, current_route)
            cost += cost_increment
        new_solution.append(current_route)
    return cost, new_solution


def two_opt_star_try(adj_matrix, routes):
    # iterate over all routes for route 1
    for i, dynamic_route1 in enumerate(routes):
        route1 = dynamic_route1.route
        # iterate over all routes for route 2
        for x, dynamic_route2 in enumerate(routes[i+1:]):
            route2 = dynamic_route2.route
            j = x+i+1
            # iterate over all starting points in route 1 in a random order
            for start1 in random.sample(range(len(route1)+1), len(route1)+1):
                # iterate over all starting points in route 2 in a random order
                for start2 in random.sample(range(len(route2)+1), len(route2)+1):
                    cost_increment1, new_route1 = modify_route(adj_matrix,
                        route1[:start1], route1[start1:], [],
                        route2[start2:]
                    )
                    cost_increment2, new_route2 = modify_route(adj_matrix,
                        route2[:start2], route2[start2:], [],
                        route1[start1:]
                    )
                    # if improvement found, restart local search
                    if cost_increment1 + cost_increment2 < 0:
                        new_dynamic_route1 = dynamic_route1.copy()
                        new_dynamic_route1.route = new_route1
                        new_dynamic_route2 = dynamic_route2.copy()
                        new_dynamic_route2.route = new_route2
                        # only add non-empty routes
                        new_routes = routes[:i]
                        if new_dynamic_route1.route or new_dynamic_route1.covered_route: new_routes.append(new_dynamic_route1)
                        new_routes += routes[i+1:j]
                        if new_dynamic_route2.route or new_dynamic_route2.covered_route: new_routes.append(new_dynamic_route2)
                        new_routes += routes[j+1:]
                        return cost_increment1 + cost_increment2, new_routes
    return 0, []


def two_opt_star(cost, adj_matrix, current_solution):
    # try 2-opt* moves until no more improvement possible
    new_solution = current_solution
    while new_solution:
        current_solution = new_solution
        cost_increment, new_solution = two_opt_star_try(adj_matrix, current_solution)
        cost += cost_increment
    return cost, current_solution


def local_search(cost, adj_matrix, routes):
    current_cost, current_solution = cost, routes
    current_cost, current_solution = two_opt(current_cost, adj_matrix, current_solution)
    current_cost, current_solution = two_opt_star(current_cost, adj_matrix, current_solution)
    return current_cost, current_solution
