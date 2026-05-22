import json
import numpy as np
from matplotlib.patches import FancyArrowPatch
import re

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

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

def vrp_visualization():
    # Load coordinates
    coords = parse_dat('dvrp_data/raw/c50D.dat')
    if coords is None:
        return
    
    # Load solution
    with open('experiment_results/c50_solution.json', 'r') as f:
        solution = json.load(f)
    
    solutions = solution['solutions']
    num_solutions = len(solutions)
    
    depot = coords[0]

    sol = solutions[-1]
    routes = sol['routes']

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect('equal')
    ax.axis('off')

    customers = []
    for routedata in routes:
        for customer in routedata['covered_route'] + routedata['route']:
            customers.append(customer)
    customers_coords = np.array([coords[i] for i in customers])

    ax.scatter(customers_coords[:, 0], customers_coords[:, 1], s=50, c='blue', zorder=3, label='Customer')
    ax.scatter(depot[0], depot[1], s=50, c='red', marker='s', zorder=3, label='Depot')

    for routeidx, routedata in enumerate(routes):
        #color = plt.cm.Blues(routeidx/len(routes)*0.6 + 0.2)
        color = list(plt.cm.Paired.colors)[routeidx]

        route = np.array([depot] + [coords[c] for c in routedata['covered_route']] + [coords[c] for c in routedata['route']] + [depot])
        ax.plot(route[:, 0], route[:, 1], '-', color=color, linewidth=2, zorder=2, alpha=0.7)

    ax.legend(loc='upper right', fontsize=16)

    plt.tight_layout()
    plt.show()
    plt.close(fig)

def computer_pictogram():
    for x in range(2):
        fig, ax = plt.subplots(figsize=(4, 4))
        # draw arrow
        arrow = mpatches.FancyArrow(-0.1, 1.05, 1.2, 0, width=0.06, length_includes_head=True, color='black')
        ax.add_patch(arrow)
        # Draw monitor
        monitor = mpatches.FancyBboxPatch((0.2, 0.5), 0.6, 0.35, boxstyle="round,pad=0.05", linewidth=2, edgecolor='black', facecolor='#B0C4DE')
        ax.add_patch(monitor)
        # Draw screen
        screen = mpatches.Rectangle((0.25, 0.55), 0.5, 0.25, linewidth=1, edgecolor='black', facecolor='white')
        ax.add_patch(screen)
        # Draw stand
        stand = mpatches.FancyBboxPatch((0.45, 0.45), 0.1, 0.07, boxstyle="round,pad=0.02", linewidth=1, edgecolor='black', facecolor='#A9A9A9')
        ax.add_patch(stand)
        # Draw base
        base = mpatches.FancyBboxPatch((0.38, 0.38), 0.24, 0.06, boxstyle="round,pad=0.03", linewidth=1, edgecolor='black', facecolor='#696969')
        ax.add_patch(base)
        # Draw keyboard
        keyboard = mpatches.FancyBboxPatch((0.25, 0.25), 0.5, 0.1, boxstyle="round,pad=0.02", linewidth=1, edgecolor='black', facecolor='#D3D3D3')
        ax.add_patch(keyboard)
        # Optionally, add some keys
        for i in range(6):
            for j in range(2):
                key = mpatches.Rectangle((0.27 + i*0.08, 0.27 + j*0.04), 0.06, 0.03, linewidth=0.5, edgecolor='#888', facecolor='#F8F8FF')
                ax.add_patch(key)
        # Draw circles and plus sign under the computer
        y = 0
        if x == 0:
            # Only blue circle
            circ = mpatches.Circle((0.5, y), 0.15, color='blue')
            ax.add_patch(circ)
        else:
            # Blue circle, plus, green circle
            circ1 = mpatches.Circle((0.2, y), 0.15, color='blue')
            circ2 = mpatches.Circle((0.8, y), 0.15, color='green')
            ax.add_patch(circ1)
            ax.add_patch(circ2)
            # Plus sign
            ax.add_line(Line2D([0.5, 0.5], [y-0.1, y+0.1], color='black', linewidth=5))
            ax.add_line(Line2D([0.4, 0.6], [y, y], color='black', linewidth=5))
        ax.set_xlim(-0.2, 1.2)
        ax.set_ylim(-0.2, 1.2)
        ax.axis('off')
        plt.tight_layout()
        plt.show()

def time_line_visualization():
    depot = [0, 10]
    customers = np.array([[0, 20], [10, 20], [10, 10], [10, 0], [0, 0]])
    color_past = list(plt.cm.Paired.colors)[1]
    color_future = list(plt.cm.Paired.colors)[0]

    vehicle_list = [[0, 10], [2, 20], [10, 16], [6, 10]]
    new_customer = [6, 10]
    new_customer_list = [[], new_customer, new_customer, []]
    covered_list = [
        [],
        np.array([depot] + list(customers[:1]) + [vehicle_list[1]]),
        np.array([depot] + list(customers[:2]) + [vehicle_list[2]]),
        np.array([depot] + list(customers[:3]) + [vehicle_list[3]]),
    ]
    committed_list = [
        np.array([depot] + list(customers[:2])),
        np.array([vehicle_list[1]] + list(customers[1:3])),
        np.array([vehicle_list[2]] + [customers[2]] + [new_customer] + [customers[3]]),
        np.array([vehicle_list[3]] + list(customers[3:])),
    ]
    planned_list = [
        np.array(list(customers[1:]) + [depot]),
        np.array(list(customers[2:]) + [depot]),
        np.array(list(customers[3:]) + [depot]),
        np.array(list(customers[4:]) + [depot]),
    ]
    
    # legend
    fig, ax = plt.subplots(figsize=(7, 1))
    ax.grid(False)
    ax.axis('off')
    ax.legend(handles=[
        plt.scatter([], [], s=50, c='blue', label='Customer'),
        plt.scatter([], [], s=50, c='green', label='New Customer'),
        plt.scatter([], [], s=200, c='red', marker='s', label='Depot'),
        plt.scatter([], [], s=100, c='green', marker='^', label='Vehicle'),
    ], loc='center', ncol=4, fontsize=12, frameon=False)
    plt.tight_layout()
    plt.show()
    plt.close(fig)

    # time line
    for frame in range(4):
        vehicle = vehicle_list[frame]
        new_customer = new_customer_list[frame]

        fig, ax = plt.subplots(figsize=(4, 6))
        ax.set_aspect('equal')

        ax.scatter(customers[:, 0], customers[:, 1], s=50, c='blue', zorder=3, label='Customer')
        if new_customer:
            ax.scatter(new_customer[0], new_customer[1], s=50, c='green', zorder=3, label='New Customer')
        ax.scatter(depot[0], depot[1], s=200, c='red', marker='s', zorder=3, label='Depot')
        ax.scatter(vehicle[0], vehicle[1], s=100, c='green', marker='^', zorder=3, label='Vehicle')

        covered = covered_list[frame]
        if len(covered) > 0:
            ax.plot(covered[:, 0], covered[:, 1], '-', color=color_past, linewidth=2, zorder=2, alpha=0.7)
        committed = committed_list[frame]
        ax.plot(committed[:, 0], committed[:, 1], '-', color=color_future, linewidth=2, zorder=2, alpha=0.7)
        planned = planned_list[frame]
        ax.plot(planned[:, 0], planned[:, 1], '--', color=color_future, linewidth=2, zorder=2, alpha=0.7)

        ax.grid(False)
        ax.axis('off')
        #ax.legend(loc='upper center', bbox_to_anchor=(0.5, 0.92), fontsize=16)

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

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_title(f"Time Period {idx + 1}", fontsize=16)
        ax.set_aspect('equal')
        ax.axis('off')

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

        ax.legend(loc='upper right', fontsize=16)

        plt.tight_layout()
        if save_images:
            filename = solution_file.replace('.json', f'_visualization_{idx+1}.png').replace('experiment_results/', destination_folder)
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"Visualization saved to {filename}")
        if show_images:
            plt.show()
        plt.close(fig)

def time_period_visualization(dat_file, solution_file, time_period, important_routes=[]):
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

    sol = solutions[time_period-1]
    routes = sol['routes']

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_title(f"Time Period {time_period}", fontsize=16)
    ax.set_aspect('equal')
    ax.axis('off')

    customers = []
    for routedata in routes:
        for customer in routedata['covered_route'] + routedata['route']:
            customers.append(customer)
    customers_coords = np.array([coords[i] for i in customers])

    ax.scatter(customers_coords[:, 0], customers_coords[:, 1], s=50, c='blue', zorder=3, label='Customer')
    ax.scatter(depot[0], depot[1], s=50, c='red', marker='s', zorder=3, label='Depot')

    for routeidx, routedata in enumerate(routes):
        first_node = routedata['covered_route'][0] if routedata['covered_route'] else 0
        if first_node in important_routes:
            color = plt.cm.Reds(0.4)
            color2 = plt.cm.Reds(0.7)
        else:
            color = plt.cm.Blues(routeidx/len(routes)*0.6 + 0.2)
            color2 = color

        covered = np.array([depot] + [coords[c] for c in routedata['covered_route']])
        if first_node in important_routes:
            committed = np.array([covered[-2], covered[-1]])
            covered = covered[:-1]
        ax.plot(covered[:, 0], covered[:, 1], '-', color=color, linewidth=2, zorder=2, alpha=0.7)
        if first_node in important_routes:
            ax.plot(committed[:, 0], committed[:, 1], '-', color=color2, linewidth=4, zorder=2, alpha=0.7)
        
        last_committed_node = coords[routedata['covered_route'][-1]] if routedata['covered_route'] else depot
        planned = np.array([last_committed_node] + [coords[c] for c in routedata['route']] + [depot])
        ax.plot(planned[:, 0], planned[:, 1], '--', color=color, linewidth=2, zorder=2, alpha=0.7)

    ax.legend(loc='upper right', fontsize=16)

    plt.tight_layout()
    plt.show()
    plt.close(fig)

if __name__ == "__main__":
    #visualize_dvrp_solution('dvrp_data/raw/c50D.dat', 'experiment_results/c50_solution.json', save_images=False)
    #time_period_visualization('dvrp_data/raw/c50D.dat', 'experiment_results/c50_solution.json', 1, [27, 46, 38])
    vrp_visualization()
