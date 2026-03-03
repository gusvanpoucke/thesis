import random
from modify_route import modify_route

def cross(cost, adj_matrix, routes, k, icross = False):
    p = random.randint(1, k)

    # randomly select 2 routes
    original_routes = routes.copy()
    selected_routes = [original_routes.pop(random.randrange(0, len(original_routes))) for _ in range(2)]

    # randomly cut both routes
    pieces = []
    for route in selected_routes:
        segment_length = min(p, len(route))
        X_prime = random.randint(0, len(route) - segment_length)
        Y_prime = X_prime + segment_length
        pieces.append([route[:X_prime], route[X_prime:Y_prime], route[Y_prime:]])
    
    # cross routes
    regular_routes = [
        modify_route(adj_matrix, pieces[0][0], pieces[0][1], pieces[0][2], pieces[1][1]),
        modify_route(adj_matrix, pieces[1][0], pieces[1][1], pieces[1][2], pieces[0][1])
    ]
    reversed_routes = [
        modify_route(adj_matrix, pieces[0][0], pieces[0][1], pieces[0][2], list(reversed(pieces[1][1]))),
        modify_route(adj_matrix, pieces[1][0], pieces[1][1], pieces[1][2], list(reversed(pieces[0][1])))
    ]
    if icross:
        best_routes = []
        for i in range(2):
            if regular_routes[i][0] < reversed_routes[i][0]:
                best_routes.append(regular_routes[i][1])
                cost += regular_routes[i][0]
            else:
                best_routes.append(reversed_routes[i][1])
                cost += reversed_routes[i][0]
        return cost, original_routes, best_routes
    else:
        cost += regular_routes[0][0] + regular_routes[1][0]
        return cost, original_routes, regular_routes


def shake(cost, adj_matrix, routes, k):
    return cross(cost, adj_matrix, routes, k, icross=True)
