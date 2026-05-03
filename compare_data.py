import argparse
import json
import os
import numpy as np
import matplotlib.pyplot as plt

# Your 21 files in order
list_of_dvrp_files = [
    "c100.json", "c100b.json", "c120.json", "c150.json", "c199.json",
    "c50.json", "c75.json", "f134.json", "f71.json", "tai100a.json",
    "tai100b.json", "tai100c.json", "tai100d.json", "tai150a.json",
    "tai150b.json", "tai150c.json", "tai150d.json", "tai75a.json",
    "tai75b.json", "tai75c.json", "tai75d.json"
]

color = list(plt.cm.Paired.colors)[0]
color2 = list(plt.cm.Paired.colors)[1]

def load_public_data(algorithm, best_costs, average_costs):
    os.makedirs(f"hpc_jobs/{algorithm}/", exist_ok=True)
    for i, dvrp_file in enumerate(list_of_dvrp_files):
        FILEPATH = "dvrp_data/processed/" + dvrp_file

        with open(FILEPATH, 'r') as file:
            VRP = json.load(file)

        graph_name = VRP['graph_name']
        # write to file
        data = {
            "graph_name": graph_name,
            "tests_ran": 30,
            "best_cost": best_costs[i],
            "average_cost": average_costs[i]
        }
        json_filename = f"hpc_jobs/{algorithm}/{dvrp_file}"
        with open(json_filename, "w") as json_file:
            json.dump(data, json_file, indent=4)

def RD_bar_chart(folder):
    relative_deviations = []
    for dvrp_file in list_of_dvrp_files:
        file = folder + dvrp_file
        with open(file, 'r') as file:
            relative_deviation = json.load(file)['relative_deviation']
        relative_deviations.append(relative_deviation * 100)

    labels = [file.replace('.json', '') for file in list_of_dvrp_files]
    
    x = np.arange(len(labels))  # the label locations
    width = 0.8  # the width of the bars

    fig, ax = plt.subplots(figsize=(8, 6))
    rects1 = ax.bar(x, relative_deviations, width, color=color)

    ax.axhline(y=0, color=color2, linestyle='-', linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=16)
    ax.tick_params(axis='y', labelsize=16)

    fig.tight_layout()
    plt.show()
    plt.close(fig)

def latex_table(folders):
    for dvrp_file in list_of_dvrp_files:
        best_costs = []
        best_best = 0
        average_costs = []
        best_average = 0
        for i, folder in enumerate(folders):
            file = folder + dvrp_file
            with open(file, 'r') as file:
                data = json.load(file)

            best = data['best_cost']
            average = data['average_cost']
            best_costs.append(best)
            average_costs.append(average)
        
            if i > 0 and best < best_costs[best_best]:
                best_best = i
            if i > 0 and average < average_costs[best_average]:
                best_average = i
        
        line = f"{dvrp_file.replace('.json', '')}"
        for i, _ in enumerate(folders):
            best_string = f"\\textbf{{{best_costs[i]:.2f}}}" if i == best_best else f"{best_costs[i]:.2f}"
            average_string = f"\\textbf{{{average_costs[i]:.2f}}}" if i == best_average else f"{average_costs[i]:.2f}"
            line += f" & {best_string} & {average_string}"
        line += " \\\\"
        print(line)

if __name__ == "__main__":
    latex_table([
        "hpc_jobs/standard_vns/",
        "hpc_jobs/sarasola_vns/",
        "hpc_jobs/genetic_algorithm/",
        "hpc_jobs/particle_swarm/",
        "hpc_jobs/multi_environmental/"
    ])
