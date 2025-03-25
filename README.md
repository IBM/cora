<!-- Build Status, is a great thing to have at the top of your repository, it shows that you take your CI/CD as first class citizens -->
<!-- [![Build Status](https://travis-ci.org/jjasghar/ibm-cloud-cli.svg?branch=master)](https://travis-ci.org/jjasghar/ibm-cloud-cli) -->
# CORA
This is the repo with the code for the paper Improving score reliability of multiple choice benchmarks with consistency evaluation and altered answer choices.

<!-- A more detailed Usage or detailed explaination of the repository here -->
## Getting started

To run this code, we advise that you create a Python enviroment first, install the required libraries, and then follow the steps in [Steps to generate results section](#steps-to-generate-results)
and execute the scripts to generate results.

### Create a Python environment

After cloning this repository, create a virtual environment:
```
python -m venv .venv
```
Activate the virtual environment:
```
source .venv/bin/activate
```
Install the required packages:
```
pip install -r requirements.txt
```

## Steps to generate results

Inside the `\src` folder, we have enumerated the script folders in the order they are run:

0. Data preparation
1. Output generation

    0. Generate alternative evaluations
    1. Generate outputs
    2. Evaluate outputs

2. Output analysis

There are no enumerations for `Data preparation` and `Output analysis`, because `Data preparation` only leaves the data in an specific format and `Output analysis` contains the files for generating the metrics after running `Output generation`.

Initialy, prepare the data, then generate multiple versions of the data, which are the alternative evaluations. With those evaluations, generate the model outputs and, finally, evaluate those outputs to obtain results.

## How to use

As an example, we have provided the MedQA data, the same data we have used in the paper, originally from [MedQA's paper github](https://github.com/jind11/MedQA?tab=readme-ov-file)

You can modify the `format_data` script to add different data. 

Those are the steps to generate the results: 

``` python
python -m src.data_preparation.prepare_dataset -i data/MedQA/MedQA.xlsx -o data/MedQA/MedQA_prepared.xlsx
python -m src.output_generation.generate_alternative_evaluations -i data/MedQA/MedQA_prepared.xlsx -o data/MedQA/MedQA_wAlternativeEvaluations.xlsx
python -m src.output_generation.generate_outputs -i data/MedQA/MedQA_wAlternativeEvaluations.xlsx -o data/MedQA/MedQA_wOutputs.xlsx
python -m src.output_generation.evaluate_outputs -i data/MedQA/MedQA_wOutputs.xlsx -o data/MedQA/MedQA_results.json
python -m src.output_analysis.compute_accuracies -i data/MedQA/MedQA_results.json
```

### Documentation

Documentation can be found primarily in this file and soon at Cora's github pages.

## Contribute

<!-- Questions can be useful but optional, this gives you a place to say, "This is how to contact this project maintainers or create PRs -->
If you have any questions or issues you can create a new [issue here](https://github.com/IBM/cora/issues).

Pull requests are very welcome! Make sure your patches are well tested.
Ideally create a topic branch for every separate change you make. For
example:

1. Fork the repo
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Added some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request

## License
<!-- All source files must include a Copyright and License header. The SPDX license header is
preferred because it can be easily scanned. -->

This project is licensed under the [Apache License 2.0](LICENSE).

<!--
```text
#
# Copyright IBM Corp. 2023 - 2024
# SPDX-License-Identifier: Apache-2.0
#
``` -->
## Contributors
[<img src="https://github.com/paulocavalin.png" width="60px;"/>](https://github.com/paulocavalin/)
[<img src="https://github.com/cassiasamp.png" width="60px;"/>](https://github.com/cassiasamp/)
[<img src="https://github.com/marcelo-grave.png" width="60px;"/>](https://github.com/marcelo-grave/)
