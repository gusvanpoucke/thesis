import json
import numpy as np
from matplotlib.patches import FancyArrowPatch
import re

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def small_visualization():
    depot = [10, 10]
    customers = np.array([[0, 0], [20, 0], [20, 20], [0, 20]])

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_title(f"Small example")
    ax.set_aspect('equal')

    ax.scatter(customers[:, 0], customers[:, 1], s=50, c='blue', zorder=3, label='Customer')
    ax.scatter(depot[0], depot[1], s=50, c='red', marker='s', zorder=3, label='Depot')

    color = list(plt.cm.Paired.colors)[0]
    covered = np.array([depot] + list(customers[:3]))
    ax.plot(covered[:, 0], covered[:, 1], '-', color=color, linewidth=2, zorder=2, alpha=0.7)
    planned = np.array(list(customers[2:]) + [depot])
    ax.plot(planned[:, 0], planned[:, 1], '--', color=color, linewidth=2, zorder=2, alpha=0.7)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper center')

    plt.tight_layout()
    plt.show()
    plt.close(fig)

def bar_chart(solution_files, comparison, title="Comparison of Two Lists", compare_value="best_cost", start=0, end=-1):
    solution_files = solution_files[start:end]
    comparison = comparison[start:end]


    my_results = []
    for solution_file in solution_files:
        FILEPATH = "experiment_results/" + solution_file + ".json"
        with open(FILEPATH, 'r') as f:
            solution = json.load(f)
        my_results.append(solution[compare_value])

    if len(my_results) != len(comparison):
        raise ValueError("Both lists must have the same length")
    
    labels = solution_files
    
    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, my_results, width, label='My Results', color='skyblue')
    rects2 = ax.bar(x + width/2, comparison, width, label='VNS by Sarasola', color='salmon')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Costs')
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    fig.tight_layout()
    plt.show()
    plt.close(fig)

def parse_dat(filepath):
    """Parse a .dat file and extract coordinates"""
    with open(filepath, 'r') as f:
        text = f.read()
    
    # parse number of locations
    match = re.search(r"NUM_LOCATIONS\s*:\s*(\S.*)", text)
    n = int(match.group(1)) if match else None

    # Parse coordinates
    match = re.search(r"LOCATION_COORD_SECTION\s+([\d\s\.\-]+)\s+DEPOT_LOCATION_SECTION", text, re.DOTALL)
    if not match:
        print(f"Error for LOCATION_COORD_SECTION in {filepath}")
        return None
    
    coords = [None] * n
    for line in match.group(1).strip().split('\n'):
        parts = line.strip().split()
        if parts:
            node_id = int(parts[0])
            x = float(parts[1])
            y = float(parts[2])
            coords[node_id] = (x, y)
    
    return np.array(coords)

def visualize_dvrp_solution(dat_file, solution_file, save_images=True, show_images=True, destination_folder="visualization/"):
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

    colors = list(plt.cm.Paired.colors) + list(plt.cm.tab10.colors)
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
            first_node = route_data['covered_route'][0] if route_data['covered_route'] else 0
            if first_node not in route_colors:
                route_colors[first_node] = route_colors_index
                route_colors_index += 1

            color = colors[route_colors[first_node]]

            covered = np.array([depot] + [coords[c] for c in route_data['covered_route']])
            ax.plot(covered[:, 0], covered[:, 1], '-', color=color, linewidth=2, zorder=2, alpha=0.7)
            
            last_committed_node = coords[route_data['covered_route'][-1]] if route_data['covered_route'] else depot
            planned = np.array([last_committed_node] + [coords[c] for c in route_data['route']] + [depot])
            ax.plot(planned[:, 0], planned[:, 1], '--', color=color, linewidth=2, zorder=2, alpha=0.7)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')

        plt.tight_layout()
        if save_images:
            filename = solution_file.replace('.json', f'_visualization_{idx+1}.png').replace('experiment_results/', destination_folder)
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"Visualization saved to {filename}")
        if show_images:
            plt.show()
        plt.close(fig)

if __name__ == "__main__":
    """
    # 21 files
    list_of_solution_files = [
        "c100",
        "c100b", 
        "c120",
        "c150",
        "c199",
        "c50",
        "c75",
        "f134",
        "f71",
        "tai100a",
        "tai100b",
        "tai100c",
        "tai100d",
        "tai150a",
        "tai150b",
        "tai150c",
        "tai150d",
        "tai75a",
        "tai75b",
        "tai75c",
        "tai75d"
    ]
    VNS_best_cost = [
        943.87,
        883.91,
        1219.73,
        1253.66,
        1538.87,
        592.60,
        940.25,
        14559.58,
        273.08,
        2134.95,
        2126.68,
        1517.57,
        1807.86,
        3274.78,
        2819.46,
        2491.58,
        2927.21,
        1833.18,
        1460.65,
        1558.05,
        1428.74
    ]
    VNS_average_cost = [
        985.94,
        910.67,
        1319.39,
        1323.40,
        1608.40,
        618.44,
        994.89,
        15423.87,
        291.21,
        2246.88,
        2204.05,
        1650.93,
        1950.62,
        3408.89,
        2902.42,
        2643.11,
        3006.04,
        1913.51,
        1496.77,
        1616.87,
        1452.73
    ]
    bar_chart(list_of_solution_files, VNS_best_cost, title="Comparison of Best Costs", start=9)
    bar_chart(list_of_solution_files, VNS_average_cost, title="Comparison of Average Costs", compare_value="average_cost", start=9)
    """
    visualize_dvrp_solution('dvrp_data/raw/c50D.dat', 'experiment_results/c50_solution.json', save_images=False)
