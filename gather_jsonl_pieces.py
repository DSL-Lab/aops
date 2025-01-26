import sys
import glob
import os

def _get_is_done_file_path(jsonl_path):
    return os.path.join(os.path.dirname(jsonl_path), f'.done_{os.path.basename(jsonl_path)}')


def gather_jsonl_pieces(input_dir, output_jsonl_path):
    jsonl_files = [y for x in os.walk(input_dir) for y in glob.glob(os.path.join(x[0], '*.jsonl'))]
    print(f'Found {len(jsonl_files)} jsonl files in {input_dir}')
    with open(output_jsonl_path, 'w') as out_f:
        for jsonl_file in jsonl_files:
            with open(jsonl_file, 'r') as in_f:
                for line in in_f:
                    out_f.write(line)
    with open(_get_is_done_file_path(output_jsonl_path), 'w') as f:
        f.write('')
    

if __name__ == '__main__':
    input_dir = sys.argv[1]
    output_jsonl_path = sys.argv[2]
    if os.path.exists(_get_is_done_file_path(output_jsonl_path)):
        print(f'{output_jsonl_path} is already complete. Exiting...')
        sys.exit(0)
    gather_jsonl_pieces(input_dir, output_jsonl_path)
    print(f'Finished gathering jsonl files from {input_dir} to {output_jsonl_path}')
