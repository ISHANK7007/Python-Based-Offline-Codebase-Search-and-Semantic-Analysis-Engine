import csv
from datetime import datetime
from collections import defaultdict

def parse_csv(file_path):
    """
    Parses a CSV file containing transaction logs.
    """
    results = defaultdict(list)
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                category = row["category"]
                amount = float(row["amount"])
                results[category].append(amount)
            except (ValueError, KeyError):
                continue
    return results

def generate_report(data_by_category):
    """
    Generates summary statistics for each category.

    Args:
        data_by_category (dict): Mapping of category -> list of floats

    Returns:
        dict: Summary report per category
    """
    def summarize(values):
        total = sum(values)
        return {
            "total": total,
            "average": total / len(values) if values else 0.0,
            "count": len(values)
        }

    return {
        category: summarize(values)
        for category, values in data_by_category.items()
    }

if __name__ == "__main__":
    sample_file = "mockpackage/analytics/transactions.csv"
    parsed_data = parse_csv(sample_file)
    report = generate_report(parsed_data)

    print(f"Report generated at {datetime.now().isoformat()}")
    for category, stats in report.items():
        print(f"{category.title()}: {stats}")
