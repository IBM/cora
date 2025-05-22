import random
random.seed(0)
import collections
from collections import OrderedDict 

import pandas as pd
import numpy as np
import json
import csv
from dtw import dtw
from numpy.linalg import norm


evaluation_types = ['standard_MC',
    'standard_MC_shuffled', 'standard_MC_wNOTA',
    'decoupled_MC', 'decoupled_MC_wNOTA'
    ]

NOTA_text = "None of the alternatives"

def get_key(my_dict, val):
  
    for key, value in my_dict.items():
        if val == value:
            return key

    return "key doesn't exist"

def get_different_indexes(length, index=-1):
    indexes = list(range(length))
    if index >= 0:
        indexes.remove(index)
    random.shuffle(indexes)
    return indexes[:5]

def get_key_with_value(v, d):
    for key, value in d.items():
        if value == v:
            return key
    return None

def shuffle_options(options):
    keys = list(options.keys())
    random.shuffle(keys)
    options = dict(OrderedDict(zip(keys, options.values())))

    # sort by key values
    sorted_list = sorted(options.items())
    sorted_dict = {}
    for key, value in sorted_list:
        sorted_dict[key] = value

    return sorted_dict

def get_decoupled_options(row):
    question = row['question']

    options = eval(row['options'])
    answer = row['answer']
    correct_choice = get_key(options, answer)

    decoupled_options = []
    for option in options:

        if option == correct_choice:
            continue

        new_options = { 'A':answer }
        new_options[ 'B' ] = options[ option ]

        decoupled_options.append( new_options )

    return decoupled_options

def add_new_option(options, value):
    # Find the last key in the dictionary
    last_key = max(options.keys())
    
    # Calculate the next key in the sequence
    next_key = chr(ord(last_key) + 1)
    
    # Add the new element to the dictionary
    options[next_key] = value
    
    return options

def get_alternative_choices(row, provided_args):
    # default options
    args = {
        'decouple': False,
        'alternative_options': None,
        'none_of_the_above': None, # options are: 'include', 'replace_incorrect', 'replace_correct'
        'shuffle_options': False,
        'mc_type': 'original', 
        'replications': 1,
        
    }

    for key in provided_args:
        args[key] = provided_args[key]

    # decouple to less options
    if args['decouple']:
        return [ get_alternative_choices(row, args|{'alternative_options': new_options, 'decouple': False})[0] for new_options in get_decoupled_options(row) ]
    
    elif args['none_of_the_above'] == 'replace_incorrect':
        answer = row['answer']
        options = eval(row['options'])
        correct_choice = get_key(options, answer)
        

        new_options = []
        for option in options:
            if option != correct_choice:
                n_ops = dict(options)
                n_ops[ option ] = NOTA_text
                new_options.append( get_alternative_choices(row, args|{'alternative_options': n_ops, 'none_of_the_above': None} )[0])                
        
        return new_options



    if args['alternative_options'] is not None:
        options = args['alternative_options']
    else:
        options = eval(row['options'])

    if args['none_of_the_above'] == 'include':
        options = add_new_option(options, NOTA_text)


    if args['shuffle_options']:
        options = shuffle_options(options)

    if args['replications'] == 1:
        return [ options ]
    else:
        args['replications'] -= 1
        return [ options ] + get_alternative_choices(row, args)


def build_prompt(question, options, incontext_examples=[], is_incontext_example=False, correct_choice=None):
    prompt = ""

    for ic_example in incontext_examples:
        ic_question, ic_options, ic_correct_choice = ic_example
        prompt += build_prompt(ic_question, ic_options, incontext_examples=[], is_incontext_example=True, correct_choice=ic_correct_choice)

    prompt += "Question: " + question + '\n'

    for option in options:
        prompt += f'{option}. {options[option]}\n'

    prompt += 'Answer:'
    
    if is_incontext_example:
        prompt += f'{correct_choice}\n\n'

    return prompt

def find_key_by_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    return None  # If value is not found in the dictionary

def count_evaluations(data):
    total = 0

    for key in data:
        total += len(data[key])
    
    return total

def parse_output(output):
    pat = "Answer: "
    pos = output.find(pat)

    if pos == -1:
        return output

    return output[pos + len(pat):]

def first_alphanumeric_letter(s):
    for char in s:
        if char.isalnum():
            return char
    return None  # Or raise an exception if preferred


def read_csv_xlsx(filename):
    extension = filename.split('.')[-1]

    if extension == 'xlsx':
        return pd.read_excel(filename)
    elif extension == 'csv':
        return pd.read_csv(filename)


def save_to_csv_xlsx(df, filename):
    extension = filename.split('.')[-1]

    if extension == 'xlsx':
        df.to_excel(filename, index=False)
    elif extension == 'csv':
        df.to_csv(filename, index=False, quoting=csv.QUOTE_MINIMAL)


#### FUNCTIONS FOR evaluate_outputs.py
def has_any_false(values):
    return not any(values)

def all_equal(values):
    previous_v = values[0]
    for v in values[1:]:
        if v == 'None of the above':
            continue

        if v != previous_v:
            return False

        previous_v = v

    return True

def get_answer(c, choices):
    if c in choices:
        return choices[c]
    return None

is_correct = lambda totals: True if totals['correct'] > totals['incorrect'] and totals['correct'] > totals['nota'] else False
is_not_correct = lambda totals: True if totals['incorrect'] > totals['correct'] and totals['incorrect'] > totals['nota'] else False


def add_response(responses, response):
    if response not in responses:
        responses[response] = 0
    responses[response] += 1
    
def get_most_provided_response(responses, skip_nota=False):
    max_ = 0
    most_provided_response = 0
    for response in responses:
        if skip_nota and response == NOTA_STRING:
            continue
        
        if responses[response] > max_:
            max_ = responses[response]
            most_provided_response = response
    
    return most_provided_response, max_

def compute_auc_dtw(data: dict):
    x = np.array(sorted(data.keys()))
    y = np.array([data[xi] for xi in x])

    area = np.trapz(y, x)

    # # Common x
    # x_ref = np.linspace(0.0, 1.0, num=len(x))
    y_perfect = np.ones_like(x)

    # Worst-case curve: y=1 at x=0, y=0 elsewhere
    y_worst = np.zeros_like(x)
    y_worst[0] = 1.0

    # Compute normalization factor
    dtw_max, _, _, _ = dtw(y_perfect.reshape(-1, 1), y_worst.reshape(-1, 1), dist=lambda a, b: norm(a - b, ord=1))

    # Compute DTW to flat line
    y_ref = np.ones_like(y)
    dtw_val, _, _, _ = dtw(y.reshape(-1, 1), y_ref.reshape(-1, 1), dist=lambda a, b: norm(a - b, ord=1))
    norm_dtw = 1.0 - (dtw_val / dtw_max if dtw_max > 0 else 0)

    return area, norm_dtw

#### FUNCTIONS FOR prepare_dataset.py

def parse_hf_benchmark(ds_pm, benchmark_name, type_of_data):
    def get_value(row):
        """Retrieves the value from the dictionary in the 'dict_col' column 
            using the key in the 'key_col' column.
        """
        return eval(row['options']).get(row['answer_idx'])

    col = str(type_of_data)
    pm_dev = ds_pm[col].to_pandas()
    ## check if there are numbers along with letters, and what is the smallest number, then create a dict
    #answer_dict = {"1": 'A', "2": 'B', "3": 'C', "4": 'D'}

    #pm_dev['answerKey'] = pm_dev['answerKey'].apply(str).replace(answer_dict)

    temp_dict = {}
    if benchmark_name == 'QASC':
        answer_dict = {"A": 0, "B": 1, "C": 2, "D" : 4, "E" : 5, "F" : 6, "G": 7}
        temp_dict['question']= pm_dev['question'].values
        temp_dict['options']= [pd.Series(x['text'], index=x['label']).to_dict() for x in pm_dev['choices']]
        temp_dict['answer_idx']= pm_dev['answerKey'].values

    elif benchmark_name == 'MMLU':
        answer_dict = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}
        temp_dict['question']= pm_dev['question'].values
        #temp_dict['answer_idx']= pm_dev['answer'].values
        temp_dict['options']= [pd.Series(x, index=['A', 'B', 'C', 'D']).to_dict() for x in pm_dev['choices']]
        temp_dict['answer_idx']= [answer_dict[x] for x in pm_dev['answer'].values]

    pm_dev_df = pd.DataFrame(temp_dict)
    pm_dev_df['options'] = pd.Series(pm_dev_df['options'], dtype="string")
    pm_dev_df['answer'] = pm_dev_df.apply(get_value, axis=1) 


    return pm_dev_df
