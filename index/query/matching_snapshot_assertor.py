import json
import os
import argparse
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def generate_performance_dashboard(results_dir, output_dir):
    """Generate a custom performance dashboard."""
    results_files = list(Path(results_dir).glob("*.json"))

    benchmarks = {}
    commits = []

    for result_file in results_files:
        with open(result_file) as f:
            data = json.load(f)
            commit = data.get("commit_hash", result_file.stem)
            commits.append(commit)

            for bench_name, bench_data in data.get("results", {}).items():
                if bench_name not in benchmarks:
                    benchmarks[bench_name] = []

                result = None
                if "result" in bench_data:
                    result = bench_data["result"]
                elif "stats" in bench_data and "mean" in bench_data["stats"]:
                    result = bench_data["stats"]["mean"]

                benchmarks[bench_name].append(result)

    os.makedirs(output_dir, exist_ok=True)

    plt.figure(figsize=(14, 8))
    time_benchmarks = {k: v for k, v in benchmarks.items() if k.startswith("time_")}

    plot_data = []
    labels = []
    for bench_name, bench_results in time_benchmarks.items():
        valid_results = [r for r in bench_results if r is not None]
        if valid_results:
            baseline = valid_results[0]
            rel_change = [(r / baseline - 1) * 100 if r is not None else 0 for r in bench_results]
            plot_data.append(rel_change)
            labels.append(bench_name.replace("time_", ""))

    ind = np.arange(len(commits))
    prev_data = np.zeros(len(commits))

    for data, label in zip(plot_data, labels):
        padded_data = np.zeros(len(commits))
        padded_data[:len(data)] = data
        plt.bar(ind, padded_data, bottom=prev_data, label=label)
        prev_data += padded_data

    plt.title('Relative Performance Change (Lower is Better)')
    plt.xlabel('Commit')
    plt.ylabel('% Change from Baseline')
    plt.xticks(ind, commits, rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'relative_performance.png'))

    html_report = generate_html_report(benchmarks, commits, output_dir)
    with open(os.path.join(output_dir, 'dashboard.html'), 'w', encoding='utf-8') as f:
        f.write(html_report)

    return output_dir

def generate_html_report(benchmarks, commits, output_dir):
    """Generate HTML performance report."""
    benchmarks_js = {}
    for bench_name, bench_results in benchmarks.items():
        benchmarks_js[bench_name] = [
            r if r is not None else 'null' for r in bench_results
        ]

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Benchmark Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; text-align: center; }}
            th {{ background-color: #f4f4f4; }}
        </style>
    </head>
    <body>
        <h1>Benchmark Performance Dashboard</h1>
        <img src="relative_performance.png" style="max-width:100%;"/>

        <h2>Raw Benchmark Data</h2>
        <table>
            <tr>
                <th>Benchmark</th>
                {''.join(f"<th>{c}</th>" for c in commits)}
            </tr>
    """

    for bench_name, values in benchmarks.items():
        html += f"<tr><td>{bench_name}</td>"
        for v in values:
            display_val = f"{v:.4f}" if isinstance(v, (float, int)) else "N/A"
            html += f"<td>{display_val}</td>"
        html += "</tr>\n"

    html += """
        </table>
    </body>
    </html>
    """

    return html

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate custom benchmark dashboard.")
    parser.add_argument("--results-dir", required=True, help="Directory with JSON benchmark results.")
    parser.add_argument("--output-dir", required=True, help="Directory to save dashboard outputs.")
    args = parser.parse_args()

    generate_performance_dashboard(args.results_dir, args.output_dir)
