set -ex

PROMPT_TYPE=$1
MODEL_NAME_OR_PATH=$2
DATA_NAME=$3
OUTPUT_DIR=${4:-"outputs"}

SPLIT="test"
NUM_TEST_SAMPLE=-1
START=${START:-0}
END=${END:--1}
TEMPERATURE=${TEMPERATURE:-0}
TOP_P=${TOP_P:-1}
N_SAMPLE=${N_SAMPLE:-1}
MAX_TOKENS_PER_CALL=${MAX_TOKENS_PER_CALL:-16384}

TOKENIZERS_PARALLELISM=false \
python3 -u math_eval.py \
    --model_name_or_path ${MODEL_NAME_OR_PATH} \
    --data_name ${DATA_NAME} \
    --output_dir ${OUTPUT_DIR} \
    --split ${SPLIT} \
    --prompt_type ${PROMPT_TYPE} \
    --num_test_sample ${NUM_TEST_SAMPLE} \
    --seed 0 \
    --temperature ${TEMPERATURE} \
    --n_sampling ${N_SAMPLE} \
    --top_p ${TOP_P} \
    --start ${START} \
    --end ${END} \
    --use_vllm \
    --save_outputs \
    --overwrite \
    --max_tokens_per_call ${MAX_TOKENS_PER_CALL}

