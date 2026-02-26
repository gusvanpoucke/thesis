import random
from evaluate import evaluate, evaluate_route

def cross(adj_matrix, routes, k, icross = False):
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
        pieces[0][0] + pieces[1][1] + pieces[0][2],
        pieces[1][0] + pieces[0][1] + pieces[1][2]
    ]
    reversed_routes = [
        pieces[0][0] + list(reversed(pieces[1][1])) + pieces[0][2],
        pieces[1][0] + list(reversed(pieces[0][1])) + pieces[1][2]
    ]
    if icross:
        best_routes = []
        for i in range(2):
            if evaluate_route(adj_matrix, regular_routes[i]) < evaluate_route(adj_matrix, reversed_routes[i]):
                best_routes.append(regular_routes[i])
            else:
                best_routes.append(reversed_routes[i])
        return original_routes + best_routes
    else:
        return original_routes + regular_routes


def shake(adj_matrix, routes, k):
    return cross(adj_matrix, routes, k, icross=True)
