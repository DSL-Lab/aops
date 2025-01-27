import json
import datetime
from tqdm import tqdm

def process_data(data):
    """Processes the data by performing some modifications.
       For example, you could add a new field or modify existing ones."""
    # Example processing: adding a new field
    # data['processed'] = True
    # import ipdb; ipdb.set_trace()
    if 'error_code' not in data['response'] and 'new_topic_settings' in data['response']['response']:
        return data 
    else:
        return None

def find_post_year(all_posts):
    first_post = all_posts[0]
    # for post in all_posts:
    post_time = datetime.datetime.fromtimestamp(first_post['post_time'])
    # if post_time < earlist_post_time:
    #     earlist_post_time = post_time
    return post_time

def read_and_write_jsonl(input_path, output_path, reference_path=None, start_date='2000-01', end_date='2030-01'):
    """Reads a JSON Lines file, processes each line, and writes it to another file."""
    # First, determine the number of lines in the file to setup the progress bar
    topic_id_reference = {}
    if reference_path is not None:
        with open(reference_path, 'r') as reference_file:
            for line in reference_file:
                json_data = json.loads(line)
                if 'error_code' in json_data['response'] or 'new_topic_settings' not in json_data['response']['response']:
                    continue
                topic_id = json_data['response']['response']['new_topic_settings']['topic_id']
                init_time = json_data['response']['response']['initialization_time']
                init_time = datetime.datetime.fromtimestamp(init_time)
                if topic_id in topic_id_reference:
                    if init_time > topic_id_reference[topic_id]:
                        topic_id_reference[topic_id] = init_time
                else:
                    topic_id_reference[topic_id] = init_time
    
    total_lines = sum(1 for _ in open(input_path))
    start_date = datetime.datetime.strptime(start_date, '%Y-%m')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m')
    with open(input_path, 'r') as input_file, open(output_path, 'w') as output_file:
        for line in tqdm(input_file, total=total_lines, desc="Processing"):
            json_data = json.loads(line)  # Convert string to JSON (dictionary)
            processed_data = process_data(json_data)  # Process the data
            if processed_data is not None:
                topic_id = processed_data['response']['response']['new_topic_settings']['topic_id']
                init_time = datetime.datetime.fromtimestamp(processed_data['response']['response']['initialization_time'])
                # use init time to handle the most recent scrape
                if init_time < topic_id_reference[topic_id]:
                    continue
                else:
                    if len(processed_data['response']['response']['posts']) == 0:
                        continue
                    post_time = find_post_year(processed_data['response']['response']['posts'])
                    print(post_time)
                    if post_time >= start_date and post_time <= end_date:
                        json_output = json.dumps(processed_data)  # Convert dictionary back to JSON string
                        output_file.write(json_output + '\n')  # Write to the output file


if __name__ == '__main__':
    # Usage example
    import argparse
    parser = argparse.ArgumentParser(description='Clean raw data')
    parser.add_argument('--input', type=str, default="/data/datasets/QED/aops/RAW/items.jl", help='Path to the input file')
    parser.add_argument('--output', type=str, default="", help='Path to the input file')
    parser.add_argument('--start', type=str, default="2000-01", help='Start time')
    parser.add_argument('--end', type=str, default="2030-01", help='End time')
    args = parser.parse_args()
    # add date
    if args.output == "":
        output_path = args.input.replace('.jl', f'_clean_{args.start}-{args.end}.jl')
    else:
        output_path = args.output
    read_and_write_jsonl(args.input, output_path, args.input, args.start, args.end)