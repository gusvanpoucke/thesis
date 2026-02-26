def savings(n, capacity, adj_matrix, demands):
    # initialize routes
    optimal_route = 0
    routes = []
    route_demands = []
    for i in range(1, n):
        routes.append([i])
        route_demands.append(demands[i])
        optimal_route += adj_matrix[0][i] + adj_matrix[i][0]
    
    # compute savings
    savings = []
    for i in range(1, n):
        for j in range(i+1, n):
            saving = adj_matrix[i][0] + adj_matrix[0][j] - adj_matrix[i][j]
            savings.append((saving, i, j))
    
    # sort savings
    savings.sort(reverse=True)
    
    # merge routes
    while savings:
        saving, i, j = savings.pop(0)

        # find routes i and j are on
        route_indices = [-1, -1]
        for x, route in enumerate(routes):
            if route[0] == i or route[-1] == i:
                route_indices[0] = x
            if route[0] == j or route[-1] == j:
                route_indices[1] = x
        
        # largest route index first to avoid issues when using pop
        route_indices.sort(reverse=True)
        
        # CHECK locations are on different routes
        if route_indices[0] != route_indices[1]:
            # CHECK locations are still connected to depot on their route
            if route_indices[0] >= 0 and route_indices[1] >= 0:
                # CHECK if capacity is not violated
                if route_demands[route_indices[0]] + route_demands[route_indices[1]] <= capacity:
                    # remove to-be-merged routes
                    route1 = routes.pop(route_indices[0])
                    route2 = routes.pop(route_indices[1])

                    # align routes
                    if route1[0] == i or route1[0] == j:
                        route1 = route1[::-1]
                    if route2[-1] == i or route2[-1] == j:
                        route2 = route2[::-1]
                    
                    # add merged route to list
                    routes.append(route1 + route2)
                    
                    # update route demands
                    i_demand = route_demands.pop(route_indices[0])
                    j_demand = route_demands.pop(route_indices[1])
                    route_demands.append(i_demand + j_demand)

                    # update optimal route
                    optimal_route -= saving
    
    return optimal_route, routes
