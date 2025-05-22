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

    consistency_resolution = 10
    total_correct = { f'MCA({c/consistency_resolution})': 0 for c in range(consistency_resolution+1) }
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

        for c in range(consistency_resolution+1):
            minimum_consistency = c/consistency_resolution
            if corrects/eval_idx >= minimum_consistency:
                total_correct[f'MCA({minimum_consistency})'] += 1

        count += 1
    
    CAR_curve = {}
    for c in range(consistency_resolution+1):
        minimum_consistency = c/consistency_resolution
        MCA = total_correct[f'MCA({minimum_consistency})']/count
        # print(f"MCA Accuracy:")
        # print(f"   {np.mean(MCA):.3F}")
        CAR_curve[minimum_consistency] = MCA

    auc, dtw_1 = ourlib.compute_auc_dtw( CAR_curve )
    CORE = auc * dtw_1
    print(f"CORE score:")
    print(f"   {CORE:.3F}")

if __name__ == "__main__":
  main()