import json
import argparse
import os
import re
import json
import time
from aops.aops import AOPS
from tqdm import tqdm
from llm import LLMParse


def build_few_shot_prompt_new():
    from aops.few_shot_prompt import TOPIC_495607_ANS, TOPIC_1766376_ANS, TOPIC_3387088_ANS
    aops = AOPS('aops/aops_fewshot.jl')
    topic_ids = [
        495607,
        1766376,
        3387088
    ]
    ans_jsons = [TOPIC_495607_ANS, TOPIC_1766376_ANS, TOPIC_3387088_ANS]
    few_shot_prompt = "\n".join([f"Topic:\n{aops.get_topic_by_id(topic_id)['thread'].strip()}\nOutput:\n{ans_json}" for topic_id, ans_json in zip(topic_ids, ans_jsons)])
    return few_shot_prompt

def build_prompt(data, start, end, worker_num, worker_rank):
    from aops.few_shot_prompt import parse_instruct_answer_only
    few_shot_prompt = build_few_shot_prompt_new()
    base_instruction = parse_instruct_answer_only

    data_ = []
    for i in range(start+worker_rank, end, worker_num):
        example = data[i]
        prompt = [
            {'role': 'user', 'content': base_instruction.format(
                few_shot_examples=few_shot_prompt, query_topic=example['thread'].strip()
            )}
        ]
        example['prompt'] = prompt
        data_.append(example)
    return data_

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
        if data_point['meta']['topic_id'] not in parsed_ids:
            if len(batch) < batch_size:
                batch.append(data_point)
            else:
                remaining_data_list.append(data_point)
        else:
            print("Jumping over parsed:", data_point['meta']['topic_id'])
        #     remaining_data_list.append(data_point)

    return remaining_data_list, batch

def _get_is_done_file_path(jsonl_path):
    return os.path.join(os.path.dirname(jsonl_path), f'.done_{os.path.basename(jsonl_path)}')

def sanity_check(data, post_data, answers):
    # make sure post number is among the posts and the user is the correct user
    for answer in answers:
        answer_post = data.get_post_by_number(answer['post_number'], post_data)
        if answer_post is None:
            print("Warning for extract solution: Post {} not found, topic id: {}".format(answer['post_number'], post_data['topic_id']))
            return False
        if answer['user'] != answer_post['username']:
            print("Warning for extract solution: User {} is not the same as the post user {} in topic id: {}".format(answer['user'], answer_post['username'], post_data['topic_id']))
            return False
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-m", "--model", type=str, default="llama3.1_70b_it")
    parser.add_argument("--vllm", action='store_true')
    parser.add_argument("--aops_path", type=str, default="data/aops/items_classified_8b.jl")
    parser.add_argument("-s", "--start", type=int, default=0)
    parser.add_argument("-e", "--end", type=int, default=None)
    parser.add_argument("--worker_num", type=int, default=10)
    parser.add_argument("--worker_rank", type=int, default=0)
    parser.add_argument("--save_dir", type=str, default="./.exps/parsed")
    parser.add_argument("--batch_size", type=int, default=2000)
    parser.add_argument("--prefix_caching", action='store_true')
    parser.add_argument("--max_model_len", type=int, default=32768)
    parser.add_argument("--gpu_memory_utilization", type=float, default=0.9)

    args = parser.parse_args()

    os.makedirs(args.save_dir, exist_ok=True)

    batch_size = args.batch_size
    data = AOPS(args.aops_path)
    if args.end is None:
        args.end = len(data)
    data_w_prompts = build_prompt(data, args.start, args.end, args.worker_num, args.worker_rank)

    parser = LLMParse(model_name=args.model, use_vllm=args.vllm, prefix_caching=args.prefix_caching)
    parser.build(max_model_len=args.max_model_len, gpu_memory_utilization=args.gpu_memory_utilization)

    username = os.getenv('USER') or os.getenv('USERNAME')
    job_suffix = f's{args.start}_e{args.end}_r{args.worker_rank}'
    outpath = os.path.join(args.save_dir, 'output', username)
    logpath = os.path.join(args.save_dir, 'log', username)
    os.makedirs(outpath, exist_ok=True)
    os.makedirs(logpath, exist_ok=True)
    output_jsonl_path = os.path.join(args.save_dir, 'output', f'extracted_jsons_{job_suffix}.jsonl')
    is_done_jsonl_path = _get_is_done_file_path(output_jsonl_path)
    if os.path.exists(is_done_jsonl_path):
        print(f"Worker {args.worker_rank} already done. Exiting.")
        exit(0)
    output_data = open(output_jsonl_path, 'a', encoding='utf-8')
    logger = open(os.path.join(logpath, f'log_{job_suffix}.txt'), 'a', encoding='utf-8')
    parsed_f = os.path.join(args.save_dir, 'last_id.txt')

    start_time = time.time()
    data_list = data_w_prompts
    total_data_points = len(data_list)
    processed_count = 0
    while len(data_list) > 0:
        print(f"Worker {args.worker_rank}/{args.worker_num}: Processing data from index {args.start} to {args.end}")
        # print some info about how much time used so far, how much data point processed and how much left
        data_list, batch = get_unparsed_batch(data_list, batch_size, parsed_f)
        prompts = [x['prompt'] for x in batch]
        outputs, finish_completion = parser.generate(prompts)
        for j, (p, o) in enumerate(zip(prompts, outputs)):
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
        for j, output in tqdm(enumerate(outputs)):
            if args.model.endswith('json'):
                json_matches = [output]
            else:
                json_matches = json_pattern.findall(output)
            if len(json_matches) > 1:
                print("Warning: Multiple match found")
            for json_str in json_matches:
                json_obj = None
                raw_matches.append(json_str)
                try:
                    json_obj = json.loads(json_str.strip())
                    json_obj['success'] = 1
                    json_data.append(json_obj)
                except Exception as e:
                    try:
                        json_obj = eval(json_str.strip().replace('\n', '\t'))
                        json_obj['success'] = 2
                        print(f"JSON FAILED, EVAL SUCCESS, Topic_id: {batch[j]['meta']['topic_id']}")
                    except Exception as e:
                        print(f"Error decoding JSON from output: {e} with topic_id: {batch[j]['meta']['topic_id']}")

                if not isinstance(json_obj, dict):
                    json_obj = {"question": "", "answers": []}
                    json_obj['success'] = 0
                sanity_check(data, batch[j], json_obj['answers'])
                json_obj['raw_decode'] = output
                result_data = {}
                result_data.update(batch[j]['raw'])
                result_data.update({"parsed": json_obj})

                output_data.write(json.dumps(result_data))
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
