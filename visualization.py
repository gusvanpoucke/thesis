import json
import numpy as np
from matplotlib.patches import FancyArrowPatch
import re

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def dynamic_route_visualization():
    depot = [10, 10]
    customers = np.array([[0, 10], [0, 0], [10, 0], [20, 0], [20, 10], [20, 20], [10, 20]])
    vehicle = [15, 0]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_aspect('equal')

    ax.scatter(customers[:, 0], customers[:, 1], s=50, c='blue', zorder=3, label='Customer')
    ax.scatter(depot[0], depot[1], s=200, c='red', marker='s', zorder=3, label='Depot')
    ax.scatter(vehicle[0], vehicle[1], s=100, c='green', marker='^', zorder=3, label='Vehicle')

    color_past = list(plt.cm.Paired.colors)[1]
    color_future = list(plt.cm.Paired.colors)[0]
    covered = np.array([depot] + list(customers[:3]) + [vehicle])
    ax.plot(covered[:, 0], covered[:, 1], '-', color=color_past, linewidth=2, zorder=2, alpha=0.7)
    committed = np.array([vehicle] + [customers[3]])
    ax.plot(committed[:, 0], committed[:, 1], '-', color=color_future, linewidth=2, zorder=2, alpha=0.7)
    planned = np.array(list(customers[3:]) + [depot])
    ax.plot(planned[:, 0], planned[:, 1], '--', color=color_future, linewidth=2, zorder=2, alpha=0.7)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.grid(False)
    ax.axis('off')
    ax.legend(loc='upper left', fontsize=16)

    plt.tight_layout()
    plt.show()
    plt.close(fig)

def cross_operation_visualization():
    depot1 = [0, 0]
    route1 = np.array([[10, 10], [10, 20], [10, 30], [10, 40]])
    route2 = np.array([[-10, 10], [-10, 20], [-10, 30], [-10, 40]])
    depot2 = [0, 50]

    fig, axs = plt.subplots(1, 2, figsize=(8, 6), sharey=True)
    customers = np.vstack((route1, route2))
    depots = np.array([depot1, depot2])
    color = list(plt.cm.Paired.colors)[0]
    route1 = np.array([depot1] + list(route1) + [depot2])
    route2 = np.array([depot1] + list(route2) + [depot2])

    ax0, ax1 = axs

    # PRE CROSS
    ax0.set_aspect('equal')
    ax0.scatter(customers[:, 0], customers[:, 1], s=50, c='blue', zorder=3, label='Customer')
    ax0.scatter(depots[:, 0], depots[:, 1], s=200, c='red', marker='s', zorder=3, label='Depot')
    for route in [route1, route2]:
        ax0.plot(route[:2, 0], route[:2, 1], '-', color=color, linewidth=2, zorder=2, alpha=0.7)
        ax0.plot(route[1:3, 0], route[1:3, 1], '--', color=color, linewidth=2, zorder=2, alpha=0.7)
        ax0.plot(route[2:4, 0], route[2:4, 1], '-', color=color, linewidth=2, zorder=2, alpha=0.7)
        ax0.plot(route[3:5, 0], route[3:5, 1], '--', color=color, linewidth=2, zorder=2, alpha=0.7)
        ax0.plot(route[4:, 0], route[4:, 1], '-', color=color, linewidth=2, zorder=2, alpha=0.7)
    ax0.set_xlabel('X')
    ax0.set_ylabel('Y')
    ax0.grid(False)
    ax0.axis('off')

    # POST CROSS
    ax1.set_aspect('equal')
    ax1.scatter(customers[:, 0], customers[:, 1], s=50, c='blue', zorder=3, label='Customer')
    ax1.scatter(depots[:, 0], depots[:, 1], s=200, c='red', marker='s', zorder=3, label='Depot')
    for route, other_route in [(route1, route2), (route2, route1)]:
        ax1.plot(route[:2, 0], route[:2, 1], '-', color=color, linewidth=2, zorder=2, alpha=0.7)
        cross = np.array([route[1], other_route[2]])
        ax1.plot(cross[:, 0], cross[:, 1], '-', color=color, linewidth=2, zorder=2, alpha=0.7)
        ax1.plot(route[2:4, 0], route[2:4, 1], '-', color=color, linewidth=2, zorder=2, alpha=0.7)
        cross = np.array([route[3], other_route[4]])
        ax1.plot(cross[:, 0], cross[:, 1], '-', color=color, linewidth=2, zorder=2, alpha=0.7)
        ax1.plot(route[4:, 0], route[4:, 1], '-', color=color, linewidth=2, zorder=2, alpha=0.7)
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.grid(False)
    ax1.axis('off')

    handles, labels = ax0.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', fontsize=16)

    plt.tight_layout()
    plt.show()
    plt.close(fig)

def two_opt_visualization():
    depot1 = [0, 0]
    route = np.array([[0, 10], [5, 20], [-5, 30], [0, 40]])
    depot2 = [0, 50]

    fig, axs = plt.subplots(1, 2, figsize=(8, 6), sharey=True)
    customers = route
    depots = np.array([depot1, depot2])
    color =  list(plt.cm.Paired.colors)[0]
    color2 = list(plt.cm.Paired.colors)[1]
    route = np.array([depot1] + list(route) + [depot2])

    ax0, ax1 = axs

    # PRE 2 OPT
    ax0.set_aspect('equal')
    ax0.scatter(customers[:, 0], customers[:, 1], s=50, c='blue', zorder=3, label='Customer')
    ax0.scatter(depots[:, 0], depots[:, 1], s=200, c='red', marker='s', zorder=3, label='Depot')

    arrow1 = FancyArrowPatch(route[0], route[1], linestyle='-',
                            arrowstyle='->', mutation_scale=20, color=color, linewidth=2, alpha=0.7)
    ax0.add_patch(arrow1)
    arrow2 = FancyArrowPatch(route[1], route[2], linestyle='--',
                            arrowstyle='->', mutation_scale=20, color=color, linewidth=2, alpha=0.7)
    ax0.add_patch(arrow2)
    arrow3 = FancyArrowPatch(route[2], route[3], linestyle='-',
                            arrowstyle='->', mutation_scale=20, color=color2, linewidth=2, alpha=0.7)
    ax0.add_patch(arrow3)
    arrow4 = FancyArrowPatch(route[3], route[4], linestyle='--',
                            arrowstyle='->', mutation_scale=20, color=color, linewidth=2, alpha=0.7)
    ax0.add_patch(arrow4)
    arrow5 = FancyArrowPatch(route[4], route[5], linestyle='-',
                            arrowstyle='->', mutation_scale=20, color=color, linewidth=2, alpha=0.7)
    ax0.add_patch(arrow5)

    ax0.set_xlabel('X')
    ax0.set_ylabel('Y')
    ax0.grid(False)
    ax0.axis('off')

    # POST 2 OPT
    ax1.set_aspect('equal')
    ax1.scatter(customers[:, 0], customers[:, 1], s=50, c='blue', zorder=3, label='Customer')
    ax1.scatter(depots[:, 0], depots[:, 1], s=200, c='red', marker='s', zorder=3, label='Depot')

    arrow1 = FancyArrowPatch(route[0], route[1], linestyle='-',
                            arrowstyle='->', mutation_scale=20, color=color, linewidth=2, alpha=0.7)
    ax1.add_patch(arrow1)
    arrow2 = FancyArrowPatch(route[1], route[3], linestyle='-',
                            arrowstyle='->', mutation_scale=20, color=color, linewidth=2, alpha=0.7)
    ax1.add_patch(arrow2)
    arrow3 = FancyArrowPatch(route[3], route[2], linestyle='-',
                            arrowstyle='->', mutation_scale=20, color=color2, linewidth=2, alpha=0.7)
    ax1.add_patch(arrow3)
    arrow4 = FancyArrowPatch(route[2], route[4], linestyle='-',
                            arrowstyle='->', mutation_scale=20, color=color, linewidth=2, alpha=0.7)
    ax1.add_patch(arrow4)
    arrow5 = FancyArrowPatch(route[4], route[5], linestyle='-',
                            arrowstyle='->', mutation_scale=20, color=color, linewidth=2, alpha=0.7)
    ax1.add_patch(arrow5)

    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.grid(False)
    ax1.axis('off')

    handles, labels = ax0.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', fontsize=16)

    plt.tight_layout()
    plt.show()
    plt.close(fig)

def two_opt_star_visualization():
    depot1 = [0, 0]
    route1 = np.array([[10, 10], [10, 20], [10, 30], [10, 40]])
    route2 = np.array([[-10, 10], [-10, 20], [-10, 30], [-10, 40]])
    depot2 = [0, 50]

    fig, axs = plt.subplots(1, 2, figsize=(8, 6), sharey=True)
    customers = np.vstack((route1, route2))
    depots = np.array([depot1, depot2])
    color =  list(plt.cm.Paired.colors)[0]
    route1 = np.array([depot1] + list(route1) + [depot2])
    route2 = np.array([depot1] + list(route2) + [depot2])

    ax0, ax1 = axs

    # PRE 2 OPT
    ax0.set_aspect('equal')
    ax0.scatter(customers[:, 0], customers[:, 1], s=50, c='blue', zorder=3, label='Customer')
    ax0.scatter(depots[:, 0], depots[:, 1], s=200, c='red', marker='s', zorder=3, label='Depot')
    for route in [route1, route2]:
        arrow1 = FancyArrowPatch(route[0], route[1], linestyle='-',
                                arrowstyle='->', mutation_scale=20, color=color, linewidth=2, alpha=0.7)
        ax0.add_patch(arrow1)
        arrow2 = FancyArrowPatch(route[1], route[2], linestyle='-',
                                arrowstyle='->', mutation_scale=20, color=color, linewidth=2, alpha=0.7)
        ax0.add_patch(arrow2)
        arrow3 = FancyArrowPatch(route[2], route[3], linestyle='--',
                                arrowstyle='->', mutation_scale=20, color=color, linewidth=2, alpha=0.7)
        ax0.add_patch(arrow3)
        arrow4 = FancyArrowPatch(route[3], route[4], linestyle='-',
                                arrowstyle='->', mutation_scale=20, color=color, linewidth=2, alpha=0.7)
        ax0.add_patch(arrow4)
        arrow5 = FancyArrowPatch(route[4], route[5], linestyle='-',
                                arrowstyle='->', mutation_scale=20, color=color, linewidth=2, alpha=0.7)
        ax0.add_patch(arrow5)
    ax0.set_xlabel('X')
    ax0.set_ylabel('Y')
    ax0.grid(False)
    ax0.axis('off')

    # POST 2 OPT
    ax1.set_aspect('equal')
    ax1.scatter(customers[:, 0], customers[:, 1], s=50, c='blue', zorder=3, label='Customer')
    ax1.scatter(depots[:, 0], depots[:, 1], s=200, c='red', marker='s', zorder=3, label='Depot')
    for route, other_route in [(route1, route2), (route2, route1)]:
        arrow1 = FancyArrowPatch(route[0], route[1], linestyle='-',
                                arrowstyle='->', mutation_scale=20, color=color, linewidth=2, alpha=0.7)
        ax1.add_patch(arrow1)
        arrow2 = FancyArrowPatch(route[1], route[2], linestyle='-',
                                arrowstyle='->', mutation_scale=20, color=color, linewidth=2, alpha=0.7)
        ax1.add_patch(arrow2)
        arrow3 = FancyArrowPatch(route[2], other_route[3], linestyle='-',
                                arrowstyle='->', mutation_scale=20, color=color, linewidth=2, alpha=0.7)
        ax1.add_patch(arrow3)
        arrow4 = FancyArrowPatch(route[3], route[4], linestyle='-',
                                arrowstyle='->', mutation_scale=20, color=color, linewidth=2, alpha=0.7)
        ax1.add_patch(arrow4)
        arrow5 = FancyArrowPatch(route[4], route[5], linestyle='-',
                                arrowstyle='->', mutation_scale=20, color=color, linewidth=2, alpha=0.7)
        ax1.add_patch(arrow5)
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.grid(False)
    ax1.axis('off')

    handles, labels = ax0.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', fontsize=16)

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

    routecolors = {}
    routecolors_index = 0

    customers = []

    colors = list(plt.cm.Paired.colors) + list(plt.cm.tab10.colors)
    for idx, sol in enumerate(solutions):
        routes = sol['routes']

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_title(f"Decision Point {idx + 1}")
        ax.set_aspect('equal')

        new_customers = []
        for routedata in routes:
            for customer in routedata['covered_route'] + routedata['route']:
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

        for routeidx, routedata in enumerate(routes):
            first_node = routedata['covered_route'][0] if routedata['covered_route'] else 0
            if first_node not in routecolors:
                routecolors[first_node] = routecolors_index
                routecolors_index += 1

            color = colors[routecolors[first_node]]

            covered = np.array([depot] + [coords[c] for c in routedata['covered_route']])
            ax.plot(covered[:, 0], covered[:, 1], '-', color=color, linewidth=2, zorder=2, alpha=0.7)
            
            last_committed_node = coords[routedata['covered_route'][-1]] if routedata['covered_route'] else depot
            planned = np.array([last_committed_node] + [coords[c] for c in routedata['route']] + [depot])
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
    #visualize_dvrp_solution('dvrp_data/raw/c50D.dat', 'experiment_results/c50_solution.json', save_images=False)
    two_opt_star_visualization()
