import argparse
import pandas as pd
import json
import numpy as np


# import matplotlib.pyplot as plt
# import numpy as np
# import json
# import os
# from tqdm.notebook import tqdm
# from pywaffle import Waffle

from .. import ourlib

def main():
    """Reads a filename from a command-line argument using argparse.

    Example usage:
    python your_script.py --input my_file.xlsx
    """

    parser = argparse.ArgumentParser(description="Generate prompts given an input file in XLSX or CSV format.")
    parser.add_argument("-i", required=True, help="Name of the input file")
    parser.add_argument("-o", required=True, help="Name of the output file")
    parser.add_argument("-f", required=False, help="Filter variations, separed by commas. Ex: standard_MC,standard_MC_shuffled", default=None)
    args = parser.parse_args()


    input_file = args.i
    print(f"The provided input file is: {input_file}")
    output_file = args.o
    print(f"The provided output file is: {output_file}")

    if args.f is not None:
        to_filter = args.f.split(',')
    else:
        to_filter = None

    input_data = pd.read_excel( input_file )

    input_data['consistency_stats'] = None

    for idx, row in input_data.iterrows():
        try:
            evaluation_data = json.loads(row['expanded_evaluation'])
        except json.JSONDecodeError as e:
            print("Invalid JSON data:", e)
        
        totals = {
            'correct': 0,
            'count': 0
        }

        for evaluation_type in evaluation_data:
            
                for decoupled_response in evaluation_data[evaluation_type]:

                    model_choice = decoupled_response['model_choice']
                    correct_choice = decoupled_response['correct_choice']

                    if model_choice == correct_choice:
                        totals['correct'] += 1
                    
                    totals['count'] += 1

        input_data.at[idx, 'consistency_stats'] = json.dumps(totals)

    print("Saving final file")
    input_data.to_excel(output_file, index=False)


if __name__ == "__main__":
  main()