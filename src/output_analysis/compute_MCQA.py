import argparse
import pandas as pd
import json
import numpy as np
from tqdm import tqdm

from .. import ourlib

def main():
    """Reads a filename from a command-line argument using argparse.

    Example usage:
    python your_script.py --input my_file.xlsx
    """

    parser = argparse.ArgumentParser(description="Generate prompts given an input file in XLSX or CSV format.")
    parser.add_argument("-i", required=True, help="Name of the input file")
    args = parser.parse_args()


    input_file = args.i
    print(f"The provided input file is: {input_file}")

    input_data = ourlib.read_csv_xlsx( input_file )

    totals = { 'correct':0, 'count': 0}

    for idx, row in tqdm(input_data.iterrows(), total=len(input_data)):
        try:
            evaluation_data = json.loads(row['expanded_evaluation'])['standard_MC'][0]
        except json.JSONDecodeError as e:
            print("Invalid JSON data:", e)
            
        if evaluation_data['model_choice'] == evaluation_data['correct_choice']:
            totals['correct'] += 1

        totals['count'] += 1

    print(f"MCQA Accuracy:")
    print(f"   {totals['correct']/totals['count']:.3F}")


if __name__ == "__main__":
  main()