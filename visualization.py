import json
import numpy as np
from matplotlib.patches import FancyArrowPatch
import re

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def parse_dat(filepath):
    """Parse a .dat file and extract coordinates"""
    with open(filepath, 'r') as f:
        text = f.read()
    
    # Parse coordinates
    match = re.search(r"LOCATION_COORD_SECTION\s+([\d\s\.\-]+)\s+DEPOT_LOCATION_SECTION", text, re.DOTALL)
    if not match:
        print(f"Error for LOCATION_COORD_SECTION in {filepath}")
        return None
    
    coords = [None] * 51
    for line in match.group(1).strip().split('\n'):
        parts = line.strip().split()
        if parts:
            node_id = int(parts[0])
            x = float(parts[1])
            y = float(parts[2])
            coords[node_id] = (x, y)
    
    return np.array(coords)

def visualize_dvrp_solution(dat_file, solution_file):
    """Visualize DVRP solutions over time"""
    
    # Load coordinates
    coords = parse_dat(dat_file)
    if coords is None:
        return
    
    # Load solution
    with open(solution_file, 'r') as f:
        solution = json.load(f)
    
    solutions = solution['solutions']
    num_solutions = len(solutions)
    
    depot = coords[0]

    route_colors = {}
    route_colors_index = 0

    customers = []

    colors = list(plt.cm.Paired.colors)
    for idx, sol in enumerate(solutions):
        routes = sol['routes']

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_title(f"Decision Point {idx + 1}")
        ax.set_aspect('equal')

        new_customers = []
        for route_data in routes:
            for customer in route_data['covered_route'] + route_data['route']:
                if customer not in customers:
                    new_customers.append(customer)
        
        new_customers_coords = np.array([coords[i] for i in new_customers])
        customers_coords = np.array([coords[i] for i in customers])

        if len(new_customers_coords) > 0:
            ax.scatter(new_customers_coords[:, 0], new_customers_coords[:, 1], s=50, c='green', zorder=3, label='New Customer')
        if len(customers_coords) > 0:
            ax.scatter(customers_coords[:, 0], customers_coords[:, 1], s=50, c='blue', zorder=3, label='Customer')
        ax.scatter(depot[0], depot[1], s=50, c='red', marker='s', zorder=3, label='Depot')

        customers.extend(new_customers)

        for route_idx, route_data in enumerate(routes):
            first_node = route_data['covered_route'][0]
            if first_node not in route_colors:
                route_colors[first_node] = route_colors_index
                route_colors_index += 1

            color = colors[route_colors[first_node]]

            covered = np.array([depot] + [coords[c] for c in route_data['covered_route']])
            ax.plot(covered[:, 0], covered[:, 1], '-', color=color, linewidth=2, zorder=2, alpha=0.7)
            
            last_committed_node = coords[route_data['covered_route'][-1]]
            planned = np.array([last_committed_node] + [coords[c] for c in route_data['route']] + [depot])
            ax.plot(planned[:, 0], planned[:, 1], '--', color=color, linewidth=2, zorder=2, alpha=0.7)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')

        plt.tight_layout()
        filename = solution_file.replace('.json', f'_visualization_{idx+1}.png').replace('experiment_results/', 'visualization/')
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"Visualization saved to {filename}")
        plt.show()
        plt.close(fig)

if __name__ == "__main__":
    visualize_dvrp_solution('dvrp_data/raw/c50D.dat', 'experiment_results/c50_solution.json')
