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
    return best_split_cost, route[:best_split], route[best_split:]


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
                prev = customer

    # insert single in optimal location
    if inserted:
        i, j = best_insert
        return (
            best_insert_cost - adj_matrix[0][single] - adj_matrix[single][0],
            routes[:i] + [routes[i][:j] + [single] + routes[i][j:]] + routes[i+1:]
        )
    else:
        return 0, routes + [[single]]


def repair(cost, capacity, adj_matrix, demands, safe_routes, dangerous_routes):
    # split all routes that break capacity constraints
    while dangerous_routes:
        route = dangerous_routes.pop()
        if capacity_constraint_route(capacity, demands, route):
            safe_routes.append(route)
        else:
            # choose best possible split in infeasible route
            split_cost, first_route, second_route = split_route(adj_matrix, route)
            cost += split_cost
            # if either route has only 1 element, try to insert it in another route
            for new_route in [first_route, second_route]:
                if len(new_route) == 1:
                    insertion_cost, safe_routes = cheapest_insertion(capacity, adj_matrix, demands, safe_routes, new_route[0])
                    cost += insertion_cost
                elif capacity_constraint_route(capacity, demands, new_route):
                    safe_routes.append(new_route)
                else:
                    dangerous_routes.append(new_route)
            
    return cost, safe_routes
