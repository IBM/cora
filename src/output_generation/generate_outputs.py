import argparse
import pandas as pd
from tqdm import tqdm
import json
import os

from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors

from .. import ourlib

from .. import common
from ..common.inference import HFInferenceEngine

def main():
    """Reads a filename from a command-line argument using argparse
    Example usage:
    python your_script.py --input my_file.xlsx
    """

    parser = argparse.ArgumentParser(description="Generate prompts given an input file in XLSX or CSV format.")
    parser.add_argument("-i", required=True, help="Name of the input file")
    parser.add_argument("-o", required=True, help="Name of the output file")
    parser.add_argument("-m", required=False, help="Name of the model - either a HuggingFace string or the path for a local directory", default="TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    parser.add_argument("-bp", required=False, help="Base prompt used for assistant",            
            default="Answer the following multiple choice question. The first line of your response should be of the following format: 'LETTER' (without quotes), where LETTER is one of ABCD (depending on the number of alternatives), followed by a step-by-step explanation.")
    
    parser.add_argument("-fs", required=False, help="Total of fewshot examples", default=0)
    parser.add_argument("-ie", required=False, help="Inference engine: HF, OpenAI", default="HF")
#    parser.add_argument("-do_sample", required=False, help="Inference engine: HF, OpenAI", default=False)
    parser.add_argument("-temperature", required=False, help="Temperature", default=1.0)
    parser.add_argument("-max_tokens", required=False, help="Max inference tokens", default=3)


    args = parser.parse_args()

    input_file = args.i
    print(f"The provided input file is: {input_file}")
    output_file = args.o
    print(f"The provided output file is: {output_file}")
    model_id = args.m
    print(f"The provided model is: {model_id}")
    fewshot_total = int(args.fs)
    print(f"Provided number of fewshot examples: {fewshot_total}")
    inference_engine = args.ie.lower()
    base_prompt = args.bp
    temperature = float(args.temperature)
    max_tokens = int(args.max_tokens)


    input_data = ourlib.read_csv_xlsx( input_file )
    
    if inference_engine == "hf":
        model_inference = HFInferenceEngine(model_id, max_tokens=max_tokens, do_sample=True if temperature > 0.0 else False, temperature=temperature)


    if fewshot_total > 0:
        embedding_model = SentenceTransformer("all-minilm-l6-v2")
        fewshot_examples = input_data
        fewshot_embeddings = embedding_model.encode(list(fewshot_examples["question"]))
        fewshot_nns = NearestNeighbors(n_neighbors=fewshot_total+1, algorithm='ball_tree').fit(fewshot_embeddings)


    # function to get the letter in the answer
    extract_first_letter = lambda a : a[0] if len(a) >= 1 else a

    for row_id, row in tqdm(input_data.iterrows(), total=len(input_data)):
        try:
            output_data = json.loads(row['expanded_evaluation'])
        except:
            print(f"error loading json for row {row_id}")
            continue
       
        if 'output' in output_data['standard_MC'][0]: #output already computed
            continue
        
        correct_answer = row['answer']

        incontext_examples = []
        if fewshot_total > 0:
            question_embedding = embedding_model.encode([row["question"]])
            distances, indexes = fewshot_nns.kneighbors(question_embedding)
            incontext_examples = indexes[0][1:]


        prompts = []
        for config_name in output_data.keys():
            current_config = output_data[config_name]

            for idx, current_config in enumerate(output_data[config_name]):

                options = current_config['choices']
            
                current_ic_examples = [ ]
                for ic_example in incontext_examples:
                    ic_row = input_data.iloc[ic_example]
                    try:
                        ic_exp_eval = json.loads(ic_row['expanded_evaluation'])[config_name][0]
                    except:
                        print(f"ic error: {ic_example} {config_name}")
                        pass
                    current_ic_examples.append( (ic_row['question'], ic_exp_eval['choices'], ic_exp_eval['correct_choice']) )

                prompt = ourlib.build_prompt(row['question'], options, current_ic_examples)

                prompts.append( (prompt, config_name, idx) )

        outputs = model_inference([ base_prompt + prompt_full[0] for prompt_full in prompts ])


        for prompt_full, output in zip(prompts, outputs):
            prompt, config_name, idx = prompt_full

            response = output

            choices = output_data[config_name][idx]['choices']
            #model_choice = extract_first_letter(response)
            model_choice = ourlib.first_alphanumeric_letter(response)
            correct_choice = ourlib.find_key_by_value(choices, correct_answer)
            if correct_choice != output_data[config_name][idx]['correct_choice']:
                print("ERROR")

            output_data[config_name][idx]['model_choice'] = model_choice
            output_data[config_name][idx]['output'] = response

            
        input_data.at[row_id, 'expanded_evaluation'] = json.dumps(output_data)
        ourlib.save_to_csv_xlsx( input_data, output_file )

    print("Saving final file")
    ourlib.save_to_csv_xlsx( input_data, output_file )
    

if __name__ == "__main__":
  main()
