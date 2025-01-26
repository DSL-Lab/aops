#!/bin/bash
set -e  # Exit if any command fails

WORKDIR="./out"
NUM_GPUS=4
TMPDIR="${WORKDIR}/tmp_${NUM_GPUS}"
ITEMS_RAW_PATH="${WORKDIR}/items_raw.jl"

ITEMS_RAW_FILTERED_PATH="${WORKDIR}/items_filtered.jl"
ITEMS_CLASSIFIED_PATH="${WORKDIR}/items_classified.jl"
ITEMS_PARSED_PATH="${WORKDIR}/items_parsed.jl"
ITEMS_Q_REWRITTEN_PATH="${WORKDIR}/items_q_rewritten.jl"
ITEMS_A_REWRITTEN_PATH="${WORKDIR}/items_a_rewritten.jl"

CLASSIFY_MODEL="qwen2.5_14b_it"
PARSE_MODEL="qwen2.5_32b_it"
REWRITE_MODEL="qwen2.5_72b_it"


# Step 0: Create stuff and pre-check
mkdir -p "${WORKDIR}"
mkdir -p "${TMPDIR}"
num_cuda_devices=$(echo $CUDA_VISIBLE_DEVICES | awk -F, '{print NF}')
if [ "$num_cuda_devices" -ne "$NUM_GPUS" ]; then
    echo "Error: Number of available GPUs ($num_cuda_devices) does not match NUM_GPUS ($NUM_GPUS)!"
    exit 1
fi

# Step 1: Crawl Data and create ITEMS_RAW_PATH

# python3 filter_crawl_errors.py "${ITEMS_RAW_PATH}" "${ITEMS_RAW_FILTERED_PATH}"


# Step 2: Math Question Extraction

IFS=',' read -ra CUDA_DEVICES <<< "$CUDA_VISIBLE_DEVICES"
NUM_WORKERS=$((NUM_GPUS / 2))
for i in $(seq 0 $((NUM_WORKERS - 1))); do
    CUDA_VISIBLE_DEVICES="${CUDA_DEVICES[$((2 * i))]},${CUDA_DEVICES[$((2 * i + 1))]}" python3 classify_aops.py --vllm --aops_path "${ITEMS_RAW_FILTERED_PATH}" --model "${CLASSIFY_MODEL}" --save_dir "${TMPDIR}/classify" --task_type "classify" --batch_size 512 --prefix_caching --worker_num "${NUM_GPUS}" --worker_rank $i &
done
wait

python3 classify_aops.py --export --export_path "${ITEMS_CLASSIFIED_PATH}"  --vllm --aops_path "${ITEMS_RAW_FILTERED_PATH}" --model "${CLASSIFY_MODEL}" --save_dir "${TMPDIR}/classify" --task_type "classify" --batch_size 512 --prefix_caching --worker_num "${NUM_GPUS}" --worker_rank 0


# Step 3: Parse the solutions

IFS=',' read -ra CUDA_DEVICES <<< "$CUDA_VISIBLE_DEVICES"
NUM_WORKERS=$((NUM_GPUS / 4))
for i in $(seq 0 $((NUM_WORKERS - 1))); do
    CUDA_VISIBLE_DEVICES="${CUDA_DEVICES[$((4 * i))]},${CUDA_DEVICES[$((4 * i + 1))]},${CUDA_DEVICES[$((4 * i+2))]},${CUDA_DEVICES[$((4 * i+3))]}" python3 parse_aops.py --vllm --aops_path "${ITEMS_CLASSIFIED_PATH}" --model "${PARSE_MODEL}" --save_dir "${TMPDIR}/parse" --batch_size 512 --gpu_memory_utilization 0.95 --prefix_caching --worker_num "${NUM_WORKERS}" --worker_rank $i &
done
wait

python3 gather_jsonl_pieces.py "${TMPDIR}/parse" "${ITEMS_PARSED_PATH}"

# Step 4: Rewrite Questions

IFS=',' read -ra CUDA_DEVICES <<< "$CUDA_VISIBLE_DEVICES"
NUM_WORKERS=$((NUM_GPUS / 4))
for i in $(seq 0 $((NUM_WORKERS - 1))); do
    CUDA_VISIBLE_DEVICES="${CUDA_DEVICES[$((4 * i))]},${CUDA_DEVICES[$((4 * i + 1))]},${CUDA_DEVICES[$((4 * i+2))]},${CUDA_DEVICES[$((4 * i+3))]}" python3 classify_aops.py --vllm --aops_path "${ITEMS_PARSED_PATH}" --task_type rewrite_question --model "${REWRITE_MODEL}" --save_dir "${TMPDIR}/q_rewrite" --batch_size 512 --max_model_len 8192 --gpu_memory_utilization 0.95 --prefix_caching --worker_num "${NUM_WORKERS}" --worker_rank $i &
done
wait


python3 gather_jsonl_pieces.py "${TMPDIR}/q_rewrite" "${ITEMS_Q_REWRITTEN_PATH}"

# Step 5: Rewrite Answers: Task type rewrite_sol

IFS=',' read -ra CUDA_DEVICES <<< "$CUDA_VISIBLE_DEVICES"
NUM_WORKERS=$((NUM_GPUS / 4))
for i in $(seq 0 $((NUM_WORKERS - 1))); do
    CUDA_VISIBLE_DEVICES="${CUDA_DEVICES[$((4 * i))]},${CUDA_DEVICES[$((4 * i + 1))]},${CUDA_DEVICES[$((4 * i+2))]},${CUDA_DEVICES[$((4 * i+3))]}" python3 classify_aops.py --vllm --aops_path "${ITEMS_Q_REWRITTEN_PATH}" --task_type rewrite_sol --model "${REWRITE_MODEL}" --save_dir "${TMPDIR}/a_rewrite" --batch_size 512 --max_model_len 8192 --gpu_memory_utilization 0.95 --prefix_caching --worker_num "${NUM_WORKERS}" --worker_rank $i &
done
wait

python3 gather_jsonl_pieces.py "${TMPDIR}/a_rewrite" "${ITEMS_A_REWRITTEN_PATH}"

# Step 6: Post-process and de-contamination
python tools/export_hf.py --num_proc 8 --version "AOPS_v1.0" --input_path "${ITEMS_A_REWRITTEN_PATH}" --export_train