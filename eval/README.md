### Requirements
You can install the required packages with the following command:
```bash
cd latex2sympy
pip install -e .
cd ..
pip install -r requirements.txt 
```

### Evaluation
You can evaluate models on AoPS24, OlympiadBench, AIME24, AMC23, Omni-Math, MATH using the following command:
```bash
PROMPT_TYPE='qwen25-math-cot' # See PROMPT_TEMPLATES in utils.py
MODEL_NAME_OR_PATH='Qwen/Qwen2.5-Math-7B-Instruct'
OUTPUT_DIR='qwen_math_7b_eval'
DATASET_NAME='aops24' # Either of aops_1224, olympiadbench, aime24, amc23, omni_math, math
bash sh/eval.sh $PROMPT_TYPE $MODEL_NAME_OR_PATH $DATASET_NAME $OUTPUT_DIR
```
where the `MODEL_NAME_OR_PATH` is the path to a model, `PROMPT_TYPE` is its prompting format for the model, `DATASET_NAME` is the name of the dataset, and `OUTPUT_DIR` is the directory to save the output results.

## Acknowledgement

The codebase is adapted from [qwen-math evaluation](https://github.com/QwenLM/Qwen2.5-Math/tree/main/evaluation) and [math-evaluation-harness](https://github.com/ZubinGou/math-evaluation-harness).
