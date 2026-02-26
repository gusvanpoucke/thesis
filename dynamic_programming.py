def vrp(n, vehicles, capacity, adj_matrix, demands, depot = 0, H = 0, E = 0):
    # in each step we will only expand the H states with the smallest costs
    if H == 0:
        H = (2**n) * n * vehicles * (capacity+1) # set H to infinite by default
    
    # in each expansion we will only expand to the E nearest unvisited nodes
    if E == 0:
        E = n # set E to infinite by default

    # state (S, j, v, c):d represents a path starting at depot, visiting every in S once,
    #   ending in j, passing through depot v times, carrying c capacity, covering distance d
    current_states = []
    next_states = {}
    prev_states = {}

    # costs C({j}j0(demands[j])) = distance from depot to j
    for j in range(n):
        if j != depot:
            set_j = 1 << j
            next_states[(set_j, j, 0, demands[j])] = adj_matrix[depot][j]
            prev_states[(set_j, j, 0, demands[j])] = depot

    # only matters for very small H or E
    sorted_states = sorted(next_states.items(), key=lambda item: item[1]) # sort starting states by cost
    current_states = sorted_states[:min(E, H)] # only expand the H states with smallest costs
    next_states = {}
    
    # make paths 1 step longer
    for k in range(2, n + vehicles - 1): # length of path
        for (S, i, v, c), d in current_states: # set of visited nodes, last visited node, id of vehicle,
                                               #    current capacity, distance covered
            unvisited = [j for j in range(n) if not(S & 1 << j) and i != j] # only unvisited nodes can be added to S
            sorted_unvisited = sorted(unvisited, key= lambda j: adj_matrix[i][j]) # sort unvisited (we only want nearest E)
            succesful_expansions = 0 # when this reaches E, stop expanding this state

            for j in sorted_unvisited: # new last visited node
                if succesful_expansions >= E:
                    break

                if c + demands[j] <= capacity: # make sure vehicle has capacity remaining
                    if j != depot or v < vehicles-1:
                        S_with_j = S | 1 << j  if j != depot else S # add j to S (unless it's the depot)
                        new_c = c + demands[j] if j != depot else 0 # add demand to capacity
                        new_v = v              if j != depot else v+1 # switch vehicles if in depot

                        if  (S_with_j, j, new_v, new_c) not in next_states or \
                            next_states[(S_with_j, j, new_v, new_c)] > d + adj_matrix[i][j]:

                            # update shortest path to (S_with_j,j, new_v, new_c)
                            next_states[(S_with_j, j, new_v, new_c)] = d + adj_matrix[i][j]
                            prev_states[(S_with_j, j, new_v, new_c)] = (S, i, v, c)
                        succesful_expansions += 1
                    
        # get sets to expand for next step
        sorted_states = sorted(next_states.items(), key=lambda item: item[1]) # sort starting states by cost
        current_states = sorted_states[:H] # only expand the H states with smallest costs
        next_states = {}
    
    # find optimal VRP tour
    optimal_tour = float('inf')
    prev = depot
    for (S, j, v, c), d in current_states: # set of all nodes except depot, last visited node, # of vehicles,
                                           #    final capacity, total distance except last stretch
        # finish the tour by ending back in depot
        if d + adj_matrix[j][depot] < optimal_tour:
            optimal_tour = d + adj_matrix[j][depot]
            prev = (S, j, v, c)
    
    # recreate tours through backtracking
    tours = []
    tour = []
    while prev != depot:
        if prev[1] == 0: # end of tour (pass through depot)
            tours.append(tour)
            tour = []
        else:
            tour = tour + [prev[1]]
        prev = prev_states[prev]
    tours.append(tour)

    if optimal_tour == float('inf'):
        optimal_tour, tours = vrp(n, vehicles+1, capacity, adj_matrix, demands, depot, H, E)

    # return length of shortest tour and list of tours
    return optimal_tour, tours
