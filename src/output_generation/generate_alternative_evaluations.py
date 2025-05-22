import pandas as pd
from tqdm import tqdm
from datasets import load_dataset #load_from_disk
import os
import json
import argparse

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


    # Handle input data
    # TO BE MOVED TO PREPARE_DATASET


    input_file = args.i
    print(f"The provided input file is: {input_file}")
    output_file = args.o
    print(f"The provided output file is: {output_file}")

    if args.f is not None:
        to_filter = args.f.split(',')
    else:
        to_filter = None

    
    # read input file
    input_data = ourlib.read_csv_xlsx( input_file )


    # this column will contain all generated here in JSON format
    if 'expanded_evaluation' not in input_data.columns:
        input_data['expanded_evaluation'] = None

    # word-around for handling the dataset
    for idx, row in input_data.iterrows():
        options = eval(row['options'])
        answer = row['answer']
        
        # work-around
        if answer in options.keys():
            input_data.at[idx, 'answer'] = options[answer]

    configs = {
            'standard_MC': {'replications': 10},
            'standard_MC_shuffled': {'shuffle_options': True, 'replications': 10},
            'standard_MC_wNOTA': {'none_of_the_above': 'replace_incorrect'},
            'standard_MC_wNOTA_shuffled': {'none_of_the_above': 'replace_incorrect', 'shuffle_options': True},
            'decoupled_MC': {'decouple': True, },
            'decoupled_MC_wNOTA': {'decouple': True, 'none_of_the_above': 'include'},
            'decoupled_MC_shuffled': {'decouple': True, 'shuffle_options': True},
            'decoupled_MC_wNOTA_shuffled': {'decouple': True, 'none_of_the_above': 'include', 'shuffle_options': True},
        }

    for idx, row in tqdm(input_data.iterrows(), total=len(input_data)):
        output_data = {}
        for config_name in configs:

            # filter to only desired configs... TODO: move to a yaml config file
            if to_filter is None or config_name in to_filter:

                options = eval(row['options'])
                answer = row['answer']
                
                # work-around
                if answer in options.keys():
                    row['answer'] = options[answer]
                    answer = row['answer']
                
                output_data[config_name] = []
                
                choices = ourlib.get_alternative_choices(row, configs[config_name])

                for choice in choices:
                    correct_choice = ourlib.find_key_by_value(choice, answer)

                    output_data[config_name].append( { 'correct_choice': correct_choice, 'choices': choice} )

                input_data.at[idx, 'expanded_evaluation'] = json.dumps(output_data)
            

    print("Saving final file")
    ourlib.save_to_csv_xlsx( input_data, output_file )



if __name__ == "__main__":
  main()