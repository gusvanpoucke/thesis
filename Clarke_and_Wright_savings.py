def savings(new_customers, capacity, adj_matrix, demands, initial_routes_cost=0, initial_routes=[]):
    # initialize routes
    optimal_route = initial_routes_cost
    locked_routes = initial_routes.copy()
    new_routes = []
    new_route_demands = []
    for i in new_customers:
        new_routes.append([i])
        new_route_demands.append(demands[i])
        optimal_route += adj_matrix[0][i] + adj_matrix[i][0]
    
    # initialize locked route demands
    locked_route_demands = []
    for route in locked_routes:
        locked_route_demands.append(sum([demands[customer] for customer in route]))

    # find route ends
    route_ends = []
    for route in locked_routes + new_routes:
        route_ends.append(route[-1])

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
        route_free = [-1, -1]
        for x, route in enumerate(locked_routes):
            if route[-1] == i:
                route_indices[0] = x
                route_free[0] = 0
            if route[-1] == j:
                route_indices[1] = x
                route_free[1] = 0
        for x, route in enumerate(new_routes):
            if route[0] == i or route[-1] == i:
                route_indices[0] = x
                route_free[0] = 1
            if route[0] == j or route[-1] == j:
                route_indices[1] = x
                route_free[1] = 1
        
        # if both elements are on free routes: standard procedure
        if sum(route_free) == 2:
            # largest route index first to avoid issues when using pop
            route_indices.sort(reverse=True)
            
            # CHECK locations are on different routes
            if route_indices[0] != route_indices[1]:
                # CHECK if capacity is not violated
                if new_route_demands[route_indices[0]] + new_route_demands[route_indices[1]] <= capacity:
                    # remove to-be-merged routes
                    route1 = new_routes.pop(route_indices[0])
                    route2 = new_routes.pop(route_indices[1])

                    # align routes
                    if route1[0] == i or route1[0] == j:
                        route1 = route1[::-1]
                    if route2[-1] == i or route2[-1] == j:
                        route2 = route2[::-1]
                    
                    # add merged route to list
                    new_routes.append(route1 + route2)
                    
                    # update route demands
                    i_demand = new_route_demands.pop(route_indices[0])
                    j_demand = new_route_demands.pop(route_indices[1])
                    new_route_demands.append(i_demand + j_demand)

                    # update optimal route
                    optimal_route -= saving
        
        # one route is locked
        elif sum(route_free) == 1:
            # determine locked route and free route
            if route_free[0] == 0:
                locked_route_index = route_indices[0]
                free_route_index = route_indices[1]
            else:
                locked_route_index = route_indices[1]
                free_route_index = route_indices[0]
            
            # CHECK if capacity is not violated
            if locked_route_demands[locked_route_index] + new_route_demands[free_route_index] <= capacity:
                # remove to-be-merged routes
                locked_route = locked_routes.pop(locked_route_index)
                free_route = new_routes.pop(free_route_index)

                # align routes
                if free_route[-1] == i or free_route[-1] == j:
                    free_route = free_route[::-1]
                
                # add merged route to locked list (direction is still locked)
                locked_routes.append(locked_route + free_route)
                
                # update route demands
                i_demand = locked_route_demands.pop(locked_route_index)
                j_demand = new_route_demands.pop(free_route_index)
                locked_route_demands.append(i_demand + j_demand)

                # update optimal route
                optimal_route -= saving
    
    return optimal_route, locked_routes + new_routes
