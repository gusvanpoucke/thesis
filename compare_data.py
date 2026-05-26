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

# 20 files
dvrp_files_without_f134 = [
    "c100.json", "c100b.json", "c120.json", "c150.json", "c199.json",
    "c50.json", "c75.json", "f71.json", "tai100a.json",
    "tai100b.json", "tai100c.json", "tai100d.json", "tai150a.json",
    "tai150b.json", "tai150c.json", "tai150d.json", "tai75a.json",
    "tai75b.json", "tai75c.json", "tai75d.json"
]

color = list(plt.cm.Paired.colors)[0]
color2 = list(plt.cm.Paired.colors)[1]
color3 = list(plt.cm.Paired.colors)[5]

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

def RD_bar_chart(files, folder, y_range=(-16, 2)):
    relative_deviations = []
    relative_deviations_best = []
    for dvrp_file in files:
        file = folder + dvrp_file
        with open(file, 'r') as file:
            data = json.load(file)
        relative_deviations.append(data['relative_deviation'] * 100)
        relative_deviations_best.append(data['relative_deviation_best'] * 100)

    file = folder + "_compare_heuristics.json"
    with open(file, 'r') as file:
        average_relative_deviation = json.load(file)['average_relative_deviation']
    average_relative_deviation *= 100

    labels = [file.replace('.json', '') for file in files]
    
    x = np.arange(len(labels))  # the label locations
    width = 0.8  # the width of the bars

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(x, relative_deviations, width, color=color)

    ax.axhline(y=0, color=color2, linestyle='-', linewidth=0.8)
    ax.axhline(y=average_relative_deviation, color=color2, linestyle='--', linewidth=0.8)
    ax.set_ylabel('Relative Deviation (%)', fontsize=16)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=16)
    ax.tick_params(axis='y', labelsize=16)
    ax.set_ylim(y_range[0], y_range[1])

    fig.tight_layout()
    plt.show()
    plt.close(fig)

def RD_parameters(parameters, prefix, x_range=(0, 16), y_range=(-1.2, 0.2)):
    relative_deviations = []
    standard_deviations = []
    parameters_percent = []
    for parameter in parameters:
        file = prefix + str(parameter).replace(".", "_") + "/_compare_heuristics.json"
        with open(file, 'r') as file:
            data = json.load(file)
        relative_deviations.append(data['average_relative_deviation'] * 100)
        standard_deviations.append(data['standard_deviation_relative_deviation'] * 100)
        parameters_percent.append(parameter * 100)

    fig, ax = plt.subplots(figsize=(8, 6))
    #ax.plot(parameters_percent, relative_deviations, marker='o', linestyle='-', color=color)
    #ax.vlines(parameters_percent, relative_deviations, standard_deviations, color=color3, linewidth=0.8)
    ax.errorbar(
        parameters_percent,
        relative_deviations,
        yerr=standard_deviations,
        fmt='o-',
        color=color,
        ecolor=plt.cm.Reds(0.4),
        capsize=4,
        elinewidth=1.5,
        label='Average RD'
    )

    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax.set_xlabel('Wait Margin (%)', fontsize=16)
    ax.set_ylabel('Average Relative Deviation (%)', fontsize=16)
    ax.set_xticks(parameters_percent)
    ax.set_xticklabels([f"{p:.0f}" for p in parameters_percent], fontsize=16)
    ax.tick_params(axis='y', labelsize=16)
    ax.set_xlim(x_range[0], x_range[1])
    ax.set_ylim(y_range[0], y_range[1])

    fig.tight_layout()
    plt.show()
    plt.close(fig)

def RD_reduce_capacity(parameters_axis, parameters_lines, prefix, infix, x_range, y_range):
    relative_deviations = []
    parameters_axis_percent = [(1-parameter)*100 for parameter in parameters_axis]
    for parameter_line in parameters_lines:
        line = []
        for parameter_axis in parameters_axis:
            folder = prefix + str(parameter_axis).replace(".", "_") + infix + str(parameter_line).replace(".", "_")
            file = folder + "/_compare_heuristics.json"
            with open(file, 'r') as file:
                data = json.load(file)
            line.append(data['average_relative_deviation'] * 100)
        relative_deviations.append(line)

    fig, ax = plt.subplots(figsize=(8, 6))
    for i, parameter_line in enumerate(parameters_lines):
        ax.plot(
            parameters_axis_percent,
            relative_deviations[i],
            marker='o',
            linestyle='-',
            color=plt.cm.Blues(i/len(parameters_lines)*0.6 + 0.4),
            label=f'{parameter_line:.1f} · T'
        )

    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax.set_xlabel('Capacity Reduction at Start (%)', fontsize=16)
    ax.set_ylabel('Average Relative Deviation (%)', fontsize=16)
    ax.set_xticks(parameters_axis_percent)
    ax.set_xticklabels([f"{p:.0f}" for p in parameters_axis_percent], fontsize=16)
    ax.tick_params(axis='y', labelsize=16)
    ax.set_xlim(x_range[0], x_range[1])
    ax.set_ylim(y_range[0], y_range[1])
    ax.legend(title='Full Capacity Time', fontsize=16, title_fontsize=16)

    fig.tight_layout()
    plt.show()
    plt.close(fig)

def RD_fullness(parameters_axis, parameters_lines, prefix, infix, x_range, y_range):
    relative_deviations = []
    for parameter_line in parameters_lines:
        line = []
        for parameter_axis in parameters_axis:
            if parameter_axis == 0.0:
                line.append(0.0)
            else:
                folder = prefix + str(parameter_axis).replace(".", "_") + infix + str(parameter_line).replace(".", "_")
                file = folder + "/_compare_heuristics.json"
                with open(file, 'r') as file:
                    data = json.load(file)
                line.append(data['average_relative_deviation'] * 100)
        relative_deviations.append(line)

    fig, ax = plt.subplots(figsize=(8, 6))
    for i, parameter_line in enumerate(parameters_lines):
        intensity = i/len(parameters_lines)
        line_color = plt.cm.Blues(0.8-(intensity*1.2)) if intensity < 0.5 else plt.cm.Reds((intensity-0.5)*1.2+0.1)
        ax.plot(
            parameters_axis,
            relative_deviations[i],
            marker='o',
            linestyle='-',
            color=line_color,
            label=f'{parameter_line:.2f}'
        )

    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax.set_xlabel('Alpha', fontsize=16)
    ax.set_ylabel('Average Relative Deviation (%)', fontsize=16)
    ax.set_xticks(parameters_axis)
    ax.set_xticklabels([f"{p:.2f}" for p in parameters_axis], fontsize=16)
    ax.tick_params(axis='y', labelsize=16)
    ax.set_xlim(x_range[0], x_range[1])
    ax.set_ylim(y_range[0], y_range[1])
    ax.legend(title='Epsilon', fontsize=16, title_fontsize=16)

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
    #RD_bar_chart(list_of_dvrp_files, "hpc_jobs/clockwise_tests/fullness_alpha_0_25_epsilon_0_5/", (-6, 6))
    #RD_parameters(list(np.arange(0.0, 0.17, 0.01)), "hpc_jobs/wait_margin_tests/wait_first/wait_margin_", (-0.5, 16.5), (-3, 1.5))
    """
    RD_reduce_capacity(
        [1.0, 0.95, 0.9, 0.85, 0.8],
        [0.4, 0.5, 0.6],
        "hpc_jobs/reduce_capacity_parameters/wait_margin_0_08/starting_capacity_",
        "_full_capacity_time_",
        (-0.5, 20.5),
        (-1, 6)
    )
    """
    RD_fullness(
        [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5],
        [0.0, 0.05, 0.1, 0.15, 0.2, 0.5, 1.0],
        "hpc_jobs/fullness_parameters/wait_margin_0_08/alpha_",
        "_epsilon_",
        (-0.01, 0.51),
        (-0.5, 2.0)
    )
