# Example usage
import argparse
import os
import re
import json
import time
import glob
import socket
import copy
from aops.aops import AOPS
from tqdm import tqdm
from llm import LLMParse


class TaskTypes:
    CLASSIFY = 'classify'
    REWRITE_SOL = 'rewrite_sol' # Given the original post that have both q and a, rewrite solution
    REWRITE_QUESTION = 'rewrite_question' # Given the original post that have both q and a, rewrite question
    ANNOTATE_SOL = 'annotate_sol' 
    ALL_TASKS = [CLASSIFY, REWRITE_SOL, REWRITE_QUESTION, ANNOTATE_SOL]


def build_prompt(data, start, end, worker_num, worker_rank, task_type):
    from aops.few_shot_prompt import instruct_classify_question, get_instruct_formalize_answer, get_instruct_formalize_question

    data_ = []
    for i in range(start+worker_rank, end, worker_num):
        example = copy.deepcopy(data[i])
        if task_type == TaskTypes.REWRITE_SOL:
            example['prompts'] = []
            for answer in example['parsed']['answers']:
                answer_post = data.get_post_by_number(answer['post_number'], example)
                question_str = example['parsed']['rewritten_question']
                if answer_post is None:
                    print("Post not found:", answer['post_number'], " Skipping")
                    continue
                if not isinstance(question_str, str):
                    print("Question not a string:", example['meta']['topic_id'], " Skipping")
                    continue
                content = get_instruct_formalize_answer(
                    question=question_str,
                    answer=answer_post['post_canonical']
                )
                example['prompts'].append(
                    [{'role': 'user', 'content': content}]
                )
        elif task_type == TaskTypes.ANNOTATE_SOL:
            from aops.few_shot_annotate_llama import get_fewshot_prompt
            for ans, rewritten_ans in zip(example['parsed']['answers'], example['parsed']['rewritten_answers']):
                if ans['content'] == '':
                    continue
                answer_post = data.get_post_by_number(ans['post_number'], example)
                question_str = example['parsed']['question']
                if answer_post is None:
                    print("Post not found:", ans['post_number'], " Skipping")
                    continue
                if not isinstance(question_str, str):
                    print("Question not a string:", example['meta']['topic_id'], " Skipping")
                    continue
                content = get_fewshot_prompt(
                    question=question_str,
                    solution_raw=answer_post['post_canonical'],
                    solution_rewrite=rewritten_ans
                )
                example['prompts'].append(
                    [{'role': 'user', 'content': content}]
                )
        elif task_type == TaskTypes.CLASSIFY:
            base_instruction = instruct_classify_question
            prompt = [
                {'role': 'user', 'content': base_instruction + example['top_post'].strip()}
            ]
            example['prompts'] = [prompt]
        elif task_type == TaskTypes.REWRITE_QUESTION:
            question_post = example['top_post']
            longest_solution = get_longest_solution(data, example)
            content = get_instruct_formalize_question(
                question=question_post,
                answer=longest_solution,
            )
            example['prompts'] = [
                [{'role': 'user', 'content': content}]
            ]
        data_.append(example)
    return data_

def get_longest_solution(data, example):
    max_len = 0
    max_ans = ""
    for ans in example['parsed']['answers']:
        ans_post = data.get_post_by_number(ans['post_number'], example)
        if ans_post is None:
            continue
        if len(ans_post['post_canonical']) > max_len:
            max_len = len(ans_post['post_canonical'])
            max_ans = ans_post['post_canonical']
    return max_ans

def get_parsed_topic_ids():
    with open(os.path.join(args.save_dir, 'last_id.txt'), 'r', encoding='utf-8') as f:
        lines = f.readlines()
        # Applying strip() to each line individually, then converting each to an integer
        parsed_line_ids = [int(x.strip()) for x in lines]
    return parsed_line_ids

def get_unparsed_batch(data_list, batch_size, parsed_f):
    # Load the set of already parsed IDs from file
    try:
        with open(parsed_f, 'r', encoding='utf-8') as f:
            parsed_ids = {int(line.strip()) for line in f}
    except FileNotFoundError:
        parsed_ids = set()

    # Select a batch of unparsed data points
    batch = []
    remaining_data_list = []
    for data_point in data_list:
        if int(data_point['meta']['topic_id']) not in parsed_ids:
            if len(batch) < batch_size:
                batch.append(data_point)
            else:
                remaining_data_list.append(data_point)
        else:
            print("Jumping over parsed:", data_point['meta']['topic_id'])
        #     remaining_data_list.append(data_point)

    return remaining_data_list, batch

def export_parsed_result(export_path, result_folder, dataset):
    export_f = open(export_path, 'w')
    jsonls = glob.glob(os.path.join(result_folder, '*.jsonl'))
    parsed = {}
    for file in jsonls:
        if not os.path.exists(_get_is_done_file_path(file)):
            print(f"Warning: File {file} not done yet! Continuing anyways!", file)
        with open(file, 'r') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line.strip())
                    is_question = data.get("is_question")
                    topic_id = data.get("topic_id")
                    if topic_id is None:
                        topic_id = data['response']['response']['new_topic_settings']['topic_id'] 
                    if topic_id is None:
                        print("Error: No topic_id found in", file)
                        continue
                    parsed[topic_id] = is_question
    # import ipdb; ipdb.set_trace()
    for i, data_point in enumerate(dataset):
        topic_id = data_point['topic_id']
        if topic_id not in parsed:
            print("Jump over", i, " ", topic_id)
        else:
            is_q = parsed[topic_id]
            num_post = len(data_point['raw']['response']['response']['posts'])
            if int(is_q) != 0 and num_post > 1:
                export_f.write(json.dumps(data_point['raw']))
                export_f.write('\n')
            else:
                print("Topic_id", topic_id, " is filtered out")
    is_done_export_path = _get_is_done_file_path(export_path)
    with open(is_done_export_path, 'w') as f:
        f.write("")
    export_f.close()

def _flatten_prompts(unflat_prompts):
    flat_prompts = []
    lens = []
    for prompt in unflat_prompts:
        flat_prompts.extend(prompt)
        lens.append(len(prompt))
    return flat_prompts, lens

def _unflatten_prompts(prompts, lens):
    examples = []
    start = 0
    for l in lens:
        examples.append(prompts[start:start+l])
        start += l
    return examples

def _get_is_done_file_path(jsonl_path):
    return os.path.join(os.path.dirname(jsonl_path), f'.done_{os.path.basename(jsonl_path)}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-m", "--model", type=str, default="llama3.1_8b_it")
    parser.add_argument("--vllm", action='store_true')
    parser.add_argument("--aops_path", type=str, default="data/aops/items_filtered.jl")
    parser.add_argument("-s", "--start", type=int, default=0)
    parser.add_argument("-e", "--end", type=int, default=None)
    parser.add_argument("--worker_num", type=int, default=10)
    parser.add_argument("--worker_rank", type=int, default=0)
    parser.add_argument("--save_dir", type=str, default="./.exps/classified")
    parser.add_argument("--export", action="store_true")
    parser.add_argument("--task_type", default=TaskTypes.CLASSIFY)
    parser.add_argument("--max_model_len", type=int, default=32768)
    parser.add_argument("--gpu_memory_utilization", type=float, default=0.9)
    parser.add_argument("--batch_size", type=int, default=2000)
    parser.add_argument("--prefix_caching", action='store_true')
    parser.add_argument("--export_path", type=str, default=None)

    args = parser.parse_args()

    os.makedirs(args.save_dir, exist_ok=True)
    assert args.task_type in TaskTypes.ALL_TASKS, f"Invalid task type: {args.task_type}"

    batch_size = args.batch_size
    dataset = AOPS(args.aops_path)
    if args.end is None:
        args.end = len(dataset)
    if args.export:
        export_path = args.export_path
        if export_path is None:
            export_path = os.path.join(args.save_dir, f'items_{args.task_type}_8b.jl')
        if os.path.exists(_get_is_done_file_path(export_path)):
            print(f"Export already done. To re-export, delete the {_get_is_done_file_path(export_path)} file")
            exit(0)
        export_parsed_result(
            export_path,
            os.path.join(args.save_dir, 'output'),
            dataset
            )
        exit(0)
    data_w_prompts = build_prompt(dataset, args.start, args.end, args.worker_num, args.worker_rank, args.task_type)

    parser = LLMParse(
        model_name=args.model, use_vllm=args.vllm, prefix_caching=args.prefix_caching
    )
    parser.build(max_model_len=args.max_model_len, gpu_memory_utilization=args.gpu_memory_utilization)

    job_suffix = f's{args.start}_e{args.end}_r{args.worker_rank}'
    os.makedirs(os.path.join(args.save_dir, 'output'), exist_ok=True)
    os.makedirs(os.path.join(args.save_dir, 'log'), exist_ok=True)
    output_jsonl_path = os.path.join(args.save_dir, 'output', f'extracted_jsons_{job_suffix}.jsonl')
    is_done_jsonl_path = _get_is_done_file_path(output_jsonl_path)
    if os.path.exists(is_done_jsonl_path):
        print(f"{args.task_type} Worker {args.worker_rank} already done. Exiting.")
        exit(0)
    output_data = open(output_jsonl_path, 'a', encoding='utf-8')
    logger = open(os.path.join(args.save_dir, 'log', f'log_{job_suffix}.txt'), 'a', encoding='utf-8')
    parsed_f = os.path.join(args.save_dir, 'last_id.txt')

    start_time = time.time()
    data_list = data_w_prompts
    total_data_points = len(data_list)
    processed_count = 0
    print("Total data points:", total_data_points, "-"*100)
    while len(data_list) > 0:
        print(f"Worker {args.worker_rank}/{args.worker_num}: Processing data from index {args.start} to {args.end}")
        # print some info about how much time used so far, how much data point processed and how much left
        data_list, batch = get_unparsed_batch(data_list, batch_size, parsed_f)
        prompts_unflattened = [x['prompts'] for x in batch]
        prompts_flat, example_lens = _flatten_prompts(prompts_unflattened)
        outputs_flat, finish_completion = parser.generate(prompts_flat)
        outputs = _unflatten_prompts(outputs_flat, example_lens)
        for j, (p, o) in enumerate(zip(prompts_unflattened, outputs)):
            print('#'*50, file=logger)
            print("topic_id: ", batch[j]['meta']['topic_id'], file=logger)
            print('-'*50, file=logger)
            print(p, file=logger)
            print('-'*50, file=logger)
            print(o, file=logger)
            print('#'*60, file=logger)

        json_data = []
        raw_matches = []
        json_pattern = re.compile(r'```json(.*?)```', re.DOTALL)
          
        for j, outputs in tqdm(enumerate(outputs)):
            if args.task_type == TaskTypes.REWRITE_SOL:
                json_obj = copy.deepcopy(batch[j])
                json_obj['parsed']['rewritten_answers'] = outputs
            elif args.task_type == TaskTypes.REWRITE_QUESTION:
                json_obj = copy.deepcopy(batch[j]['raw'])
                json_obj['parsed']['rewritten_question'] = outputs[0] # Only one prompt
            elif args.task_type == TaskTypes.ANNOTATE_SOL:
                json_obj = copy.deepcopy(batch[j])
                json_obj['parsed']['annotate_posts'] = outputs
            elif args.task_type == TaskTypes.CLASSIFY:
                output = outputs[0] # only one prompt
                result_output = re.findall(r'\\boxed\{(\d+)\}', output)
                if not len(result_output):
                    result_output = re.findall(r'```output\s*([\d]+)\s*```', output)
                if len(result_output) > 1:
                    print("Warning: Multiple match found")
                if len(result_output) == 0 or int(result_output[0]) not in [0, 1]:
                    print("Warning: No response")
                    print("prompt:", prompts_unflattened[j][0])
                    print("response:", output)
                    if len(output) == 0:
                        print("Input context too long")
                        result_output = 0
                    else:
                        result_output = -1
                else:
                    result_output = result_output[0]

                json_obj = batch[j]['raw']
                json_obj['is_question'] = result_output
                json_obj['classify_raw_decode'] = output
            output_data.write(json.dumps(json_obj))
            output_data.write('\n')
            output_data.flush()
            with open(parsed_f, 'a') as f:
                f.write(f'{batch[j]["meta"]["topic_id"]}\n')
                f.flush()
                
        current_time = time.time()
        elapsed_time = current_time - start_time
        elapsed_hours = elapsed_time / 3600  # Convert seconds to hours
        processed_count += len(batch)
        remaining_data_points = len(data_list)
        print(f"Worker {args.worker_rank}/{args.worker_num}: Processing data from index {args.start} to {args.end}")
        print(f"Elapsed Time: {elapsed_hours:.2f} hours - Processed: {processed_count}/{total_data_points}, Remaining: {remaining_data_points}")
    with open(is_done_jsonl_path, 'w') as f:
        f.write("")
