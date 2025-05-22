import argparse
import pandas as pd
from datasets import load_dataset

from .. import ourlib

def main():
    """Reads a filename from a command-line argument using argparse.

    Example usage:
    python your_script.py --input my_file.xlsx
    """

    parser = argparse.ArgumentParser(description="Generate prompts given an input file in XLSX or CSV format.")
    parser.add_argument("-i", required=False, help="Name of the input file")
    parser.add_argument("-o", required=True, help="Name of the output file")
    parser.add_argument("-t", required=False, help="Type of the benchmark", default='MedQA')
    args = parser.parse_args()


    # Handle input data
    # TO BE MOVED TO PREPARE_DATASET


    output_file = args.o

    bench_type = args.t

    if bench_type == 'MedQA':
        input_file = args.i

        input_data = pd.read_excel( input_file )
        # filter out training data
        input_data = input_data[ input_data['filesource'] == 'test.jsonl' ].reset_index()
        # Delete multiple columns
        input_data.drop(['index', 'meta_info', 'answer_idx', 'metamap_phrases', 'filesource'], axis=1, inplace=True)

    elif bench_type == 'QASC':
        input_data = load_dataset("allenai/qasc")
        pm_dev_df = ourlib.parse_hf_benchmark(input_data, 'QASC', 'validation')
        input_data = pm_dev_df.reset_index()
        input_data.drop(['index'], axis=1, inplace=True)

    elif bench_type == 'MMLU':
        input_data = load_dataset("cais/mmlu", "all")
        pm_dev_df = ourlib.parse_hf_benchmark(input_data, 'MMLU', 'test')
        input_data = pm_dev_df.reset_index()
        input_data.drop(['index'], axis=1, inplace=True)

    elif bench_type == "MMLU-Redux":
        categories = [
                        'abstract_algebra', 
                        'anatomy', 
                        'astronomy',
                        'business_ethics',
                        'clinical_knowledge',
                        'college_biology',
                        'college_chemistry',
                        'college_computer_science',
                        'college_mathematics',
                        'college_medicine',
                        'college_physics',
                        'computer_security',
                        'conceptual_physics',
                        'econometrics',
                        'electrical_engineering',
                        'elementary_mathematics',
                        'formal_logic',
                        'global_facts',
                        'high_school_biology',
                        'high_school_chemistry',
                        'high_school_computer_science',
                        'high_school_european_history',
                        'high_school_geography',
                        'high_school_government_and_politics',
                        'high_school_macroeconomics',
                        'high_school_mathematics',
                        'high_school_microeconomics',
                        'high_school_physics',
                        'high_school_psychology',
                        'high_school_statistics',
                        'high_school_us_history',
                        'high_school_world_history',
                        'human_aging',
                        'human_sexuality',
                        'international_law',
                        'jurisprudence',
                        'logical_fallacies',
                        'machine_learning',
                        'management',
                        'marketing',
                        'medical_genetics',
                        'miscellaneous',
                        'moral_disputes',
                        'moral_scenarios',
                        'nutrition',
                        'philosophy',
                        'prehistory',
                        'professional_accounting',
                        'professional_law',
                        'professional_medicine',
                        'professional_psychology',
                        'public_relations',
                        'security_studies',
                        'sociology',
                        'us_foreign_policy',
                        'virology',
                        'world_religions'
                     ]
        
        input_dfs = []
        
        for category in categories:
            print(category)
            input_data = load_dataset("edinburgh-dawg/mmlu-redux-2.0", category)
            pm_dev_df = ourlib.parse_hf_benchmark(input_data, 'MMLU', 'test')
            input_data = pm_dev_df.reset_index()
            input_data.drop(['index'], axis=1, inplace=True)
            input_data['Category'] = category

            input_dfs.append(input_data)

        input_data = pd.concat(input_dfs)   

    
    input_data.to_excel(output_file, index=False)

if __name__ == "__main__":
  main()
