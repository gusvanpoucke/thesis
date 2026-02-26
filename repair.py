from evaluate import capacity_constraint_route

def split_route(adj_matrix, route):
    best_split = 0
    best_split_cost = 0
    for split in range(1, len(route)):
        i, j = route[split-1], route[split]
        split_cost = adj_matrix[i][0] + adj_matrix[0][j] - adj_matrix[i][j]
        if split_cost < best_split_cost or split == 1:
            best_split = split
            best_split_cost = split_cost
    return route[:best_split], route[best_split:]


def cheapest_insertion(capacity, adj_matrix, demands, routes, single):
    inserted = False
    best_insert = (0, 0)
    best_insert_cost = 0
    for i, route in enumerate(routes):
        # check if single fits on route
        if sum(demands[customer] for customer in route) + demands[single] <= capacity:
            # try to insert single between every 2 customers and at the start and end of the route
            prev = 0
            for j, customer in enumerate(route + [0]):
                insert_cost = adj_matrix[prev][single] + adj_matrix[single][customer] - adj_matrix[prev][customer]
                if insert_cost < best_insert_cost or not inserted:
                    inserted = True
                    best_insert = (i, j)
                    best_insert_cost = insert_cost

    # insert single in optimal location
    if inserted:
        i, j = best_insert
        return routes[:i] + [routes[i][:j] + [single] + routes[i][j:]] + routes[i+1:]
    else:
        return routes + [[single]]


def repair(capacity, adj_matrix, demands, routes):
    repaired_routes = routes.copy()
    # split all routes that break capacity constraints
    while True:
        split = False
        for i, route in enumerate(repaired_routes):
            if not capacity_constraint_route(capacity, demands, route):
                # choose best possible split in infeasible route
                route1, route2 = split_route(adj_matrix, route)
                repaired_routes.pop(i)
                # if either route has only 1 element, try to insert it in another route
                if len(route1) == 1:
                    repaired_routes = cheapest_insertion(capacity, adj_matrix, demands, repaired_routes, route1[0])
                else:
                    repaired_routes.append(route1)
                if len(route2) == 1:
                    repaired_routes = cheapest_insertion(capacity, adj_matrix, demands, repaired_routes, route2[0])
                else:
                    repaired_routes.append(route2)
                split = True
                break
        if not split:
            break
    return repaired_routes
