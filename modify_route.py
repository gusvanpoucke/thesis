def modify_route(adj_matrix, first_piece, original_piece, last_piece, new_piece, start=0):
    first_piece_last_node = first_piece[-1] if first_piece else start
    last_piece_first_node = last_piece[0] if last_piece else 0
    cost_original_routes = (
        adj_matrix[first_piece_last_node][original_piece[0]] + adj_matrix[original_piece[-1]][last_piece_first_node]
        if original_piece
        else adj_matrix[first_piece_last_node][last_piece_first_node]
    )
    cost_new_routes = (
        adj_matrix[first_piece_last_node][new_piece[0]] + adj_matrix[new_piece[-1]][last_piece_first_node]
        if new_piece
        else adj_matrix[first_piece_last_node][last_piece_first_node]
    )
    return cost_new_routes - cost_original_routes, first_piece + new_piece + last_piece
