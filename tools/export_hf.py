import json
import os
import glob
import logging
# add parent directory to the path
import pyarrow.parquet as pq
import sys
import re
import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aops.aops import AOPS
from datasets import load_dataset, Dataset
from tqdm import tqdm

##################################################################################################
def is_real_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_fraction(s):
    # Check for fractions formatted as \frac{numerator}{denominator}
    return bool(re.match(r'\\frac\{(\d+)\}\{(\d+)\}', s))

def convert_fraction(s):
    # Convert LaTeX \frac{numerator}{denominator} to a float
    match = re.match(r'\\frac\{(\d+)\}\{(\d+)\}', s)
    numerator = int(match.group(1))
    denominator = int(match.group(2))
    return float(numerator) / float(denominator)

def is_equation(s):
    # Basic check for operations or equal signs typical in equations
    return any(op in s for op in ['+', '-', '*', '/', '=', '^'])

def is_tuple_or_list(s):
    # Check for comma-separated values enclosed in parentheses or brackets
    return (s.startswith('(') and s.endswith(')')) or (s.startswith('[') and s.endswith(']'))

def categorize_content(content):
    if is_real_number(content):
        return 'Real Number'
    elif is_fraction(content):
        return 'Real Number'  # Treat fractions as real numbers for simplicity
    elif is_equation(content):
        return 'Equation'
    elif is_tuple_or_list(content):
        return 'Tuple/List'
    else:
        return 'String'
##################################################################################################

def get_post_by_number(post_number, post_data):
    for post in post_data:
        if post['post_number'] == post_number:
            return post
    return None

def save_to_json(data, path):
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        logging.error(f"Error saving data to {path}: {e}")

def save_to_json_lines(data, path):
    try:
        with open(path, 'w') as f:
            for item in data:
                json.dump(item, f)
                f.write('\n')  # Write a newline after each JSON object
    except IOError as e:
        logging.error(f"Error saving data to {path}: {e}")

def save_to_parquet(dataset, path):
    try:
        pq.write_table(dataset.data.table, path)
    except Exception as e:
        logging.error(f"Error saving data to {path}: {e}")

def get_user_info(path='/data/muchenli/QED/data/aops/username_user_scores.jl'):
    user_info = {}
    for line in open(path, 'r').readlines():
        user_data = json.loads(line)
        user_info[user_data['username']] = user_data
    return user_info

def find_earliest_time_stamp(all_posts):
    earlist_post_time = 9999 * 100 + 1
    for post in all_posts:
        if 'post_time' in post:
            post_time = datetime.datetime.fromtimestamp(post['post_time']).strftime('%Y-%m')
            year = int(post_time.split('-')[0])
            month = int(post_time.split('-')[1])
            if year * 100 + month < earlist_post_time:
                earlist_post_time = year * 100 + month
    if earlist_post_time == 3000 * 100 + 1:
        earlist_post_time = 2000 * 100 + 1
    return {
        'year': int(earlist_post_time // 100),
        'month': int(earlist_post_time % 100)
    }
    
def extract_last_boxed(s):
    """
    Extracts the content within the last \boxed{...} in the given string.

    Args:
        s (str): The input string containing one or more \boxed{...}.

    Returns:
        str or None: The content inside the last \boxed{...}, or None if not found.
    """
    boxed_positions = []
    idx = 0
    pattern = r'\boxed{'
    while idx < len(s):
        # Find the next occurrence of \boxed{
        start = s.find(r'\boxed{', idx)
        if start == -1:
            break  # No more \boxed{ found

        # Initialize brace counting
        brace_depth = 0
        content_start = start + len(r'\boxed{')
        i = content_start
        while i < len(s):
            if s[i] == '{':
                brace_depth += 1
            elif s[i] == '}':
                if brace_depth == 0:
                    break  # Found the closing brace for \boxed{
                brace_depth -= 1
            i += 1

        # Extract the content within \boxed{...}
        if i < len(s):
            content = s[content_start:i]
            boxed_positions.append(content)
            idx = i + 1  # Move index past the current \boxed{...}
        else:
            # Unbalanced braces
            break

    if boxed_positions:
        return boxed_positions[-1]  # Return the last \boxed{...} content
    else:
        return None  # No \boxed{...} found


def parse_data_rewritten(data, math_stack=False, added_prompt=""):
    pattern = re.compile(r'\\boxed\{([^}]*)\}')
    # user_info = get_user_info()
    sft_data = []
    non_prove_data = []
    post_time_missing_cnt = 0
    for entry in tqdm(data):
        entry = json.loads(entry)
        if 'raw' in entry:
            all_posts = entry['raw']['response']['response']['posts']
        else:
            all_posts = entry['response']['response']['posts']

        parsed = entry['parsed']
        if isinstance(parsed['rewritten_question'], dict):
            logging.info(f"Skipping entry with dict question: {parsed['rewritten_question']} {entry['topic_id']}")
            continue
        elif parsed['rewritten_question'] is None or parsed['rewritten_question'] == "":
            logging.info(f"Skipping entry with None question: {parsed['rewritten_question']} {entry['topic_id']}")
            continue
            
        entry_is_proved = 'prove' in parsed['rewritten_question'].lower() or 'show that' in parsed['rewritten_question'].lower()
        for post, rewritten_ans in zip(parsed['answers'], parsed['rewritten_answers']):
            if 'qed' in rewritten_ans.lower() or 'q.e.d.' in rewritten_ans.lower():
                entry_is_proved = True
                break
        if not entry_is_proved:
            non_prove_data.append(entry)
        
        for post, rewritten_ans in zip(parsed['answers'], parsed['rewritten_answers']):
            original_post = get_post_by_number(post['post_number'], all_posts)
            # jump over the case when the original post is not found
            if original_post is None:
                print(f"Original post not found for post number {post['post_number']}")
                continue

            post_time = find_earliest_time_stamp(all_posts)
            

            score_post = int(original_post['thanks_received']) - int(original_post['nothanks_received'])
            if math_stack:
                score_user = 0
            else:
                score_user = 1 #user_info[original_post['username']]['answer_score']
            is_prove = 'prove ' in parsed['rewritten_question'].lower() or 'show that' in parsed['rewritten_question'].lower()\
                or 'qed' in rewritten_ans.lower() or 'q.e.d.' in rewritten_ans.lower()
            matches = pattern.findall(rewritten_ans)
            is_boxed = 0 if not matches else 1
            # match for answer
            if matches:
                last_boxed = matches[-1]
                if is_fraction(last_boxed):
                    last_boxed = convert_fraction(last_boxed)  # Convert fraction to float
                ans = last_boxed
                category = categorize_content(str(last_boxed))
            else:
                ans = ""
                category = 'unknown'
            topic_id = entry['meta']['topic_id']
            ####################################################################################################################
            sft_data.append({
                "topic_id": topic_id,
                "post_time": post_time,
                "origin_q": all_posts[0]['post_canonical'],
                "origin_a": original_post['post_canonical'],
                "origin_a_id": original_post['post_number'],
                "rewritten_q": parsed['rewritten_question'],
                "rewritten_a": rewritten_ans,
                "score_post": score_post,
                "score_user": score_user,
                "is_prove": is_prove,
                "is_boxed": is_boxed,
                "answer": ans,
                "category": category,
                "content": parsed['rewritten_question'] + all_posts[0]['post_canonical'],
                "messages": [
                    {'content': parsed['rewritten_question'] + added_prompt, 'role': 'user'},
                    {'content': rewritten_ans, 'role': 'assistant'}
                ]
            })
    print(f"Post time missing count: {post_time_missing_cnt}")
    return sft_data, non_prove_data

def save_for_annotate(sft_data, file_path):
    data_to_annotate = {}
    skip_figure = 0
    skip_no_boxed = 0
    qa_cnt = 0
    for x in sft_data:
        if x['is_prove']:
            continue
        if "figure " in x['origin_q'].lower() or "diagram " in x['origin_q'].lower():
            skip_figure += 1
            continue
        boxed_ans = extract_last_boxed(x['rewritten_a'])
        boxed_ans_original = extract_last_boxed(x['origin_a'])
        if boxed_ans is None and boxed_ans_original is None:
            skip_no_boxed += 1
            continue
        topic_id = x['topic_id']
        qa_cnt = qa_cnt + 1
        if topic_id not in data_to_annotate:
            data_to_annotate[topic_id] =\
                {
                    'topic_id': x['topic_id'],
                    'rewritten_question': x['rewritten_q'],
                    'post_numbers': [x['origin_a_id']],
                    'rewritten_answers': [x['rewritten_a']],
                    "original_answers": [{
                        'post_number': x['origin_a_id'],
                        'content': x['origin_a']
                    }],
                    "boxed_answers": [boxed_ans],
                    "boxed_answers_original": [boxed_ans_original],
                    'link': f"https://artofproblemsolving.com/community/h{x['topic_id']}",
                    'post_time': x['post_time'],
                }
        else:
            data_to_annotate[topic_id]['post_numbers'].append(x['origin_a_id'])
            data_to_annotate[topic_id]['rewritten_answers'].append(x['rewritten_a'])
            data_to_annotate[topic_id]['original_answers'].append({
                'post_number': x['origin_a_id'],
                'content': x['origin_a']
            })
            data_to_annotate[topic_id]['boxed_answers'].append(boxed_ans)
            data_to_annotate[topic_id]['boxed_answers_original'].append(boxed_ans_original)
    
    data_to_annotate = list(data_to_annotate.values())
    print(f"Number of entries to annotate: {len(data_to_annotate)}")
    print(f"Number of QA pairs: {qa_cnt}")
    print(f"Number of entries skipped due to figure: {skip_figure}")
    print(f"Number of entries skipped due to no boxed answer: {skip_no_boxed}")
    save_to_json_lines(data_to_annotate, file_path)

def process_files(args):
    file_path = args.input_path 
    if file_path.startswith('AI-MO/NuminaMath-CoT'):
        from tools.decontamination.find_substrings import SubstringFilterer
        folder_path = '/data/muchenli/QED/data/numina'
        filterer = SubstringFilterer(
            output_dir=os.path.join(folder_path, 'dct_new'),
            cached_decontamination_dir=None,
            cache_retrieval_key='hexsha',
            num_grams=10,
            content_key='problem',
        )
        ds = load_dataset(file_path, split='train')
        sft_data = filterer.run(ds, args.num_proc, args.batch_size)
        return
    else:
        added_prompt = args.prompt
        with open(file_path, 'r') as file:
            all_data = file.readlines()

        folder_path = os.path.dirname(file_path)
        logging.basicConfig(
            filename=os.path.join(folder_path, 'error_log.log'),
            level=logging.ERROR,
            format='%(asctime)s:%(levelname)s:%(message)s'
        )
        folder_path = os.path.join(folder_path, f'{args.version}')
        os.makedirs(folder_path, exist_ok=True)
        sft_data, non_prove_data = parse_data_rewritten(all_data, math_stack=args.math_stack, added_prompt=added_prompt)
    

    if args.filter:
        def has_http_link(s):
            pattern = r'http[s]?://\S+'
            return bool(re.search(pattern, s))

        # def filter(x):
        #     return x['is_boxed'] #and (x['score_post'] > 0 or x['score_user'] > 0)
        # print(f"Number of entries: {len(sft_data)}")
        # print("Filtering based on x['is_boxed'] and (x['score_post'] > 0 or x['score_user'] > 0)")
        # sft_data = [x for x in sft_data if filter(x)]
        # print(f"Number of entries after filtering: {len(sft_data)}")

        print("Filtering based on has_http_link is false")
        sft_data = [x for x in sft_data if not has_http_link(x['origin_a'])]
        print(f"Number of entries after filtering: {len(sft_data)}")

    if args.dct:
        from tools.decontamination.find_substrings import SubstringFilterer
        filterer = SubstringFilterer(
            output_dir=os.path.join(folder_path, 'dct'),
            cached_decontamination_dir=None,
            cache_retrieval_key='hexsha',
            num_grams=10,
        )
        ds = Dataset.from_list(sft_data)
        sft_data = filterer.run(ds, args.num_proc, args.batch_size)
    
    # split data
    train_data = [{"messages": x["messages"]} for x in sft_data if x['post_time']['year'] < 2024]
    val_data = [{"messages": x["messages"]} for x in sft_data if x['post_time']['year'] == 2024 and x['post_time']['month'] <= 2]
    test_data = [{"messages": x["messages"]} for x in sft_data if x['post_time']['year'] == 2024 and x['post_time']['month'] > 2]
    print(f"Train: {len(train_data)} Val: {len(val_data)} Test: {len(test_data)}")

    if args.export_bench:
        def apply_dct(data):
            from tools.decontamination.find_substrings import SubstringFilterer
            filterer = SubstringFilterer(
                output_dir=os.path.join(folder_path, 'dct'),
                cached_decontamination_dir=None,
                cache_retrieval_key='hexsha',
                num_grams=8,
                include_train=True
            )
            ds = Dataset.from_list(data)
            return filterer.run(ds, args.num_proc, args.batch_size)
        # save_for_annotate(
        #     sft_data,
        #     os.path.join(folder_path, 'train_to_annotate.jsonl')
        # )
        # Uncomment the following lines to save val and test data for annotation
        # save_for_annotate(
        #     apply_dct(val_data),
        #     os.path.join(folder_path, 'val_to_annotate.jsonl')
        # )
        data_2024 = [x for x in sft_data if x['post_time']['year'] == 2024]
        save_for_annotate(
            apply_dct(data_2024),
            os.path.join(folder_path, 'test_2024_to_annotate.jsonl')
        )
        data_other = [x for x in sft_data if x['post_time']['year'] != 2024]
        save_for_annotate(
            data_other,
            os.path.join(folder_path, 'train_to_annotate.jsonl')
        )


    if args.export_train:
        save_to_json(train_data, os.path.join(folder_path, 'train.json'))
        save_to_json(val_data, os.path.join(folder_path, 'val.json'))
        save_to_json(test_data, os.path.join(folder_path, 'test.json'))
        # Uncomment the following lines to save the data in parquet format
        # print("Saving to parquet")
        # dataset_train = load_dataset('json', data_files=str(train_json_path), split='train')
        # save_to_parquet(dataset_train, os.path.join(folder_path,'train_prefs-00000-of-00001.parquet'))
        # dataset_val = load_dataset('json', data_files=str(val_json_path), split='train')
        # save_to_parquet(dataset_val, os.path.join(folder_path, 'val_prefs-00000-of-00001.parquet'))
        # dataset_test = load_dataset('json', data_files=str(test_json_path), split='train')
        # save_to_parquet(dataset_test, os.path.join(folder_path, 'test_prefs-00000-of-00001.parquet'))


if __name__ == "__main__":
    # add argparse to get the input path   
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", type=str, default="data/aops/70b_rewritten/70b_rewritten_all.jl", help="Path to the input files")
    # ins prompt to be added to the end of the data
    parser.add_argument("--prompt", type=str, default='', help="Set default prompt to be empty")
    parser.add_argument("--dct", action="store_true", help="Decontaminate the dataset")
    parser.add_argument("--num_proc", type=int, default=32, help="Number of processes to use for decontamination")
    parser.add_argument("--batch_size", type=int, default=10000, help="Batch size for decontamination")
    parser.add_argument("--export_train", action="store_true", help="Export the dataset to parquet format")
    parser.add_argument("--export_bench", action="store_true", help="Export the dataset to jsonl format")
    parser.add_argument("--version", type=str, default="AOPS", help="Version of the dataset")
    parser.add_argument("--filter", action="store_true", help="Filter the dataset")
    parser.add_argument("--math_stack", action="store_true", help="is math stack dataset")
    args = parser.parse_args()


    process_files(args)
