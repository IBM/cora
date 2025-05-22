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
    parser.add_argument("-f", required=False, help="Filter variations, separed by commas. Ex: standard_MC,standard_MC_shuffled", default=None)
    args = parser.parse_args()


    input_file = args.i
    print(f"The provided input file is: {input_file}")

    if args.f is not None:
        to_filter = args.f.split(',')
    else:
        to_filter = None


    input_data = ourlib.read_csv_xlsx( input_file )

    #total_evaluations = ourlib.count_evaluations( json.loads(input_data.iloc[0]['expanded_evaluation']) )
    total_evaluations = 100 # workaround since the number of total evaluations varies
    totals_correct = [0] * total_evaluations
    count = 0

    total_evaluation_sizes = []

    for idx, row in tqdm(input_data.iterrows(), total=len(input_data)):
        
        try:
            evaluation_data = json.loads(row['expanded_evaluation'])
        except json.JSONDecodeError as e:
            print("Invalid JSON data:", e)

        corrects = 0
        incorrects = 0
        eval_idx = 0
        for evaluation_type in evaluation_data:

            if to_filter is None or evaluation_type in to_filter:

                curr_evaluation_data = evaluation_data[evaluation_type]

                for evaluation_element in curr_evaluation_data:

                    if evaluation_element['model_choice'] == evaluation_element['correct_choice']:
                        totals_correct[eval_idx] += 1
                    
                    eval_idx += 1

        count += 1

    individual_accuracies = [ tc/count for tc in totals_correct if tc > 0 ]

    print(f"MCQA+ Accuracy:")
    print(f"   {np.mean(individual_accuracies):.3F}")


if __name__ == "__main__":
  main()