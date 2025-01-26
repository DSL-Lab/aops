ITEMS_A_REWRITTEN_PATH1="out/items_a_rewritten_qwen.jl"
ITEMS_A_REWRITTEN_PATH2="out/items_a_rewritten_llama.jl"
python tools/export_hf.py --num_proc 8 --version "qwen" --input_path "${ITEMS_A_REWRITTEN_PATH1}" --export_bench
python tools/export_hf.py --num_proc 8 --version "llama" --input_path "${ITEMS_A_REWRITTEN_PATH1}" --export_bench
python tools/cross_check_formalize.py --jsonl1 out/llama/test_2024_to_annotate.jsonl --jsonl2 out/qwen/test_2024_to_annotate.jsonl
