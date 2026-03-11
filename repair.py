from evaluate import capacity_constraint_route, time_constraint_route
from dynamic_route import Route

def split_route(adj_matrix, route, start=0):
    best_split = 0
    best_split_cost = 0
    for split in range(1, len(route)):
        i, j = route[split-1], route[split]
        split_cost = adj_matrix[i][0] + adj_matrix[0][j] - adj_matrix[i][j]
        if split_cost < best_split_cost or split == 1:
            best_split = split
            best_split_cost = split_cost

    if start > 0:
        split_cost_start = adj_matrix[start][0] + adj_matrix[0][route[0]] - adj_matrix[start][route[0]]
        if split_cost_start < best_split_cost:
            best_split = 0
            best_split_cost = split_cost_start

    return best_split_cost, route[:best_split], route[best_split:]


def cheapest_insertion(capacity, adj_matrix, demands, time_left, durations, routes, single):
    inserted = False
    best_insert = (0, 0)
    best_insert_cost = 0
    for i, dynamic_route in enumerate(routes):
        route = dynamic_route.route
        # check if single fits on route
        if capacity_constraint_route(capacity, demands, dynamic_route.full_route() + [single]):
            # try to insert single between every 2 customers and at the start and end of the route
            prev = dynamic_route.start()
            for j, customer in enumerate(route + [0]):
                # check time constraint of route
                suggested_route = dynamic_route.copy()
                suggested_route.route = suggested_route.route[:j] + [single] + suggested_route.route[j:]
                if time_constraint_route(time_left, durations, adj_matrix, suggested_route):
                    insert_cost = adj_matrix[prev][single] + adj_matrix[single][customer] - adj_matrix[prev][customer]
                    if insert_cost < best_insert_cost or not inserted:
                        inserted = True
                        best_insert = (i, j)
                        best_insert_cost = insert_cost
                prev = customer

    # insert single in optimal location
    if inserted:
        i, j = best_insert
        route_i = routes[i].copy()
        route_i.route = route_i.route[:j] + [single] + route_i.route[j:]
        return (
            best_insert_cost - adj_matrix[0][single] - adj_matrix[single][0],
            routes[:i] + [route_i] + routes[i+1:]
        )
    else:
        return 0, routes + [Route([], [single], 0)]


def repair(cost, capacity, adj_matrix, demands, time_left, durations, safe_routes, dangerous_routes):
    # split all routes that break capacity constraints
    while dangerous_routes:
        dynamic_route = dangerous_routes.pop()
        route = dynamic_route.route
        if capacity_constraint_route(capacity, demands, dynamic_route.full_route()) and time_constraint_route(time_left, durations, adj_matrix, dynamic_route):
            safe_routes.append(dynamic_route)
        else:
            # choose best possible split in infeasible route
            split_cost, first_route, second_route = split_route(adj_matrix, route, start=dynamic_route.start())
            cost += split_cost
            
            dynamic_first_route = dynamic_route.copy()
            dynamic_first_route.route = first_route
            if len(first_route) == 1 and not(dynamic_route.covered_route):
                insertion_cost, safe_routes = cheapest_insertion(capacity, adj_matrix, demands, time_left, durations, safe_routes, first_route[0])
                cost += insertion_cost
            elif capacity_constraint_route(capacity, demands, first_route) and time_constraint_route(time_left, durations, adj_matrix, dynamic_first_route):
                safe_routes.append(dynamic_first_route)
            else:
                dangerous_routes.append(dynamic_first_route)

            dynamic_second_route = Route([], second_route, 0)
            if len(second_route) == 1:
                insertion_cost, safe_routes = cheapest_insertion(capacity, adj_matrix, demands, time_left, durations, safe_routes, second_route[0])
                cost += insertion_cost
            elif capacity_constraint_route(capacity, demands, second_route) and time_constraint_route(time_left, durations, adj_matrix, dynamic_second_route):
                safe_routes.append(dynamic_second_route)
            else:
                dangerous_routes.append(dynamic_second_route)
            
    return cost, safe_routes
