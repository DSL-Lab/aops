import os
import sys
import json

def get_models_stats():
    acc_results = {}
    for model_name in sorted(os.listdir('./outputs')):
        acc_results[model_name] = {}
        result_output = os.path.join('outputs', model_name, 'math_eval')
        for dataset_name in os.listdir(result_output):
            model_dataset_dir = os.path.join(result_output, dataset_name)
            # the json file that contains 'metrics', I don't know which
            try:
                metric_file = [f for f in os.listdir(model_dataset_dir) if 'metrics' in f][0]
            except:
                print(f"cannot get metric file for dataset {dataset_name} model {model_name}, skipping")
                continue
            with open(os.path.join(model_dataset_dir, metric_file), 'r') as f:
                metrics = json.load(f)
            acc_results[model_name][dataset_name] = metrics['acc']
    return acc_results

def generate_latex_table(stats):
    """
    This function takes the output of the `get_models_stats()` function
    and converts it into a LaTeX table.

    :param stats: Dictionary with model and dataset accuracy stats
    :return: String containing LaTeX code for the table
    """
    # Extract model names and dataset names
    models = list(stats.keys())
    datasets = set()
    for model_data in stats.values():
        datasets.update(model_data.keys())
    datasets = sorted(datasets)  # Sorting for consistent order

    # Create LaTeX table header
    latex_table = "\\begin{table}[htbp]\n\\centering\n\\begin{tabular}{l" + "c" * len(datasets) + "}\n"

    # Add table caption and label
    latex_table += "\\caption{Model Performance on Different Datasets}\n"
    latex_table += "\\label{tab:model_performance}\n"

    # Table header row (datasets)
    latex_table += "Model & " + " & ".join(datasets) + " \\\\\n"
    latex_table += "\\midrule\n"

    # Table rows (model accuracy)
    for model in sorted(models):
        row = [model]
        for dataset in datasets:
            if dataset in stats[model]:
                row.append(f"{stats[model][dataset]:.2f}")
            else:
                row.append("-")
        latex_table += " & ".join(row) + " \\\\\n \\midrule\n"

    # End of LaTeX table
    latex_table += "\\end{tabular}\n\\end{table}"

    latex_table = latex_table.replace('_', '-')
    return latex_table
            

if __name__ == '__main__':
    stats = get_models_stats()
    print(stats)
    print("-"*10)
    print(generate_latex_table(stats))

