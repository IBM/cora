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
    parser.add_argument("-c", required=False, help="Consistency value between 0.0 and 1.0", default=0.9)
    args = parser.parse_args()


    input_file = args.i
    print(f"The provided input file is: {input_file}")

    if args.f is not None:
        to_filter = args.f.split(',')
    else:
        to_filter = None

    minimum_consistency = float(args.c)

    input_data = ourlib.read_csv_xlsx( input_file )

    total_correct = 0
    count = 0

    for idx, row in tqdm(input_data.iterrows(), total=len(input_data)):
        
        try:
            evaluation_data = json.loads(row['expanded_evaluation'])
        except json.JSONDecodeError as e:
            print("Invalid JSON data:", e)

        corrects = 0
        eval_idx = 0
        for evaluation_type in evaluation_data:

            if to_filter is None or evaluation_type in to_filter:

                curr_evaluation_data = evaluation_data[evaluation_type]

                for evaluation_element in curr_evaluation_data:
                    eval_idx += 1

                    if evaluation_element['model_choice'] == evaluation_element['correct_choice']:
                        corrects += 1

        if corrects/eval_idx >= minimum_consistency:
            total_correct += 1

        count += 1
    
    MCA = total_correct/count
    print(f"MCA Accuracy:")
    print(f"   {MCA:.3F}")


if __name__ == "__main__":
  main()