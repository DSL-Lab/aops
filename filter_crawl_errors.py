import sys
import json
import os
from tqdm import tqdm

def remove_crawl_errors(raw_items_path, save_items_path):
    with open(raw_items_path, 'r') as f:
        raw_items = f.readlines()
    with open(save_items_path, 'w') as f:
        for line in tqdm(raw_items):
            if 'new_topic_settings' in json.loads(line)['response']['response']:
                f.write(line)

raw_items_path = sys.argv[1]
save_items_path = sys.argv[2]
is_done_file = os.path.join(os.path.dirname(save_items_path), '.done_filter_crawl_errors')

if os.path.exists(is_done_file):
    print("Found .done_filter_crawl_errors file. To re-run, delete this file.")
    sys.exit(0)
else:
    print("Filtering crawl errors...")
    remove_crawl_errors(raw_items_path, save_items_path)
    with open(is_done_file, 'w') as f:
        f.write("")
    print("Done filtering crawl errors.")
