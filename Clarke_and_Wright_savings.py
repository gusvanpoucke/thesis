from dynamic_route import Route
from evaluate import time_constraint_route

def savings(new_customers, capacity, adj_matrix, demands, time_left, durations, initial_routes_cost=0, initial_routes=[]):
    # initialize routes
    optimal_route = initial_routes_cost
    routes = initial_routes.copy()

    # initialize initial route demands
    route_demands = []
    for dynamic_route in routes:
        route_demands.append(sum([demands[customer] for customer in dynamic_route.full_route()]))

    # initialize new customers on seperate routes
    for i in new_customers:
        new_route = Route([], [i], 0)
        routes.append(new_route)
        route_demands.append(demands[i])
        optimal_route += adj_matrix[0][i] + adj_matrix[i][0]

    # find route ends
    route_ends = []
    for dynamic_route in routes:
        if dynamic_route.route:
            route_ends.append(dynamic_route.route[-1])
        else:
            route_ends.append(dynamic_route.start())

    # compute savings
    savings = []
    for index, i in enumerate(route_ends):
        for j in route_ends[index+1:]:
            saving = adj_matrix[i][0] + adj_matrix[0][j] - adj_matrix[i][j]
            savings.append((saving, i, j))
    
    # sort savings
    savings.sort(reverse=True)
    
    # merge routes
    while savings:
        saving, i, j = savings.pop(0)

        # find routes i and j are on
        route_indices = [-1, -1]
        for x, dynamic_route in enumerate(routes):
            route = dynamic_route.route
            if not(route):
                if dynamic_route.start() == i:
                    route_indices[0] = x
                if dynamic_route.start() == j:
                    route_indices[1] = x
            else:
                if (route[0] == i and not(dynamic_route.covered_route)) or route[-1] == i:
                    route_indices[0] = x
                if (route[0] == j and not(dynamic_route.covered_route)) or route[-1] == j:
                    route_indices[1] = x
        
        # largest route index first to avoid issues when using pop
        route_indices.sort(reverse=True)
        
        # CHECK both indices are still at the end of routes
        if route_indices[0] >= 0 and route_indices[1] >= 0:
            # CHECK locations are on different routes
            if route_indices[0] != route_indices[1]:
                # CHECK if capacity is not violated
                if route_demands[route_indices[0]] + route_demands[route_indices[1]] <= capacity:
                    # CHECK if at least one route is new (2 routes with commited starts can't be merged)
                    if not(routes[route_indices[0]].covered_route) or not(routes[route_indices[1]].covered_route):
                        # remove to-be-merged routes and demands
                        dynamic_route1 = routes.pop(route_indices[0])
                        dynamic_route2 = routes.pop(route_indices[1])
                        i_demand = route_demands.pop(route_indices[0])
                        j_demand = route_demands.pop(route_indices[1])

                        # commited route first
                        if dynamic_route2.covered_route:
                            temp = dynamic_route1
                            dynamic_route1 = dynamic_route2
                            dynamic_route2 = temp
                            temp = i_demand
                            i_demand = j_demand
                            j_demand = temp

                        route1 = dynamic_route1.route
                        route2 = dynamic_route2.route

                        # align routes
                        if route and (route1[0] == i or route1[0] == j):
                            route1 = route1[::-1]
                        if route2[-1] == i or route2[-1] == j:
                            route2 = route2[::-1]
                        
                        # merge routes
                        new_route = dynamic_route1.copy()
                        new_route.route = route1 + route2

                        # CHECK if time constraint is not violated
                        if time_constraint_route(time_left, durations, adj_matrix, new_route):
                            # add merged route to list and update route demands
                            routes.append(new_route)
                            route_demands.append(i_demand + j_demand)

                            # update optimal route
                            optimal_route -= saving
                        else:
                            # re-add unchanged routes and demands to lists
                            routes.append(dynamic_route1)
                            routes.append(dynamic_route2)
                            route_demands.append(i_demand)
                            route_demands.append(j_demand)
    
    return optimal_route, routes
