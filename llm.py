import os
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
from tqdm import tqdm


MODEL_WEIGHTS = {
    "mappings": {
        "ds_7b_it": {
            'model_path': "deepseek-ai/deepseek-math-7b-instruct",
            'tokenizer_path': "deepseek-ai/deepseek-math-7b-instruct",
        },
        "ds_7b_rl": {
            'model_path': "deepseek-ai/deepseek-math-7b-rl",
            'tokenizer_path': "deepseek-ai/deepseek-math-7b-rl",
        },
        "llama3_8b_it": {
            'model_path': 'meta-llama/Meta-Llama-3-8B-Instruct',
            'tokenizer_path': 'meta-llama/Meta-Llama-3-8B-Instruct'
        },
        "llama3_70b_it": {
            'model_path': 'meta-llama/Meta-Llama-3-70B-Instruct',
            'tokenizer_path': 'meta-llama/Meta-Llama-3-70B-Instruct'
        },
        "mixtral": {
            'model_path': 'mistralai/Mixtral-8x7B-Instruct-v0.1',
            'tokenizer_path': 'mistralai/Mixtral-8x7B-Instruct-v0.1',
        },
        "llama3.1_8b_it": {
            'model_path': 'meta-llama/Meta-Llama-3.1-8B-Instruct',
            'tokenizer_path': 'meta-llama/Meta-Llama-3.1-8B-Instruct'
        },
        "llama3.1_70b_it": {
            'model_path': 'meta-llama/Meta-Llama-3.1-70B-Instruct',
            'tokenizer_path': 'meta-llama/Meta-Llama-3.1-70B-Instruct'
        },
        "qwen2_math_72b": {
            'model_path': 'Qwen/Qwen2-Math-72B',
            'tokenizer_path': 'Qwen/Qwen2-Math-72B'
        },
        "qwen2.5_14b_it": {
            'model_path': 'Qwen/Qwen2.5-14B-Instruct',
            'tokenizer_path': 'Qwen/Qwen2.5-14B-Instruct'
        },
        "qwen2.5_72b_it": {
            'model_path': 'Qwen/Qwen2.5-72B-Instruct',
            'tokenizer_path': 'Qwen/Qwen2.5-72B-Instruct'
        },
        "qwen2.5_32b_it": {
            'model_path': 'Qwen/Qwen2.5-32B-Instruct',
            'tokenizer_path': 'Qwen/Qwen2.5-32B-Instruct'
        },
    },
}

class LLMParse:
    def __init__(self, model_name, use_vllm=True, temperature=0.0, max_tokens=4096, eval_batch_size=1,
                 load_in_8bit=False, load_in_half=False, gptq=False,
                 no_execution=False, prompt_format='default', prefix_caching=False) -> None:
        self.model_name = model_name
        cfg = MODEL_WEIGHTS['mappings'].get(model_name, model_name)
        self.model_name_or_path = cfg['model_path']
        self.tokenizer_name_or_path = cfg['tokenizer_path']
        self.use_vllm = use_vllm
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.eval_batch_size = eval_batch_size
        self.load_in_8bit = load_in_8bit
        self.load_in_half = load_in_half
        self.gptq = gptq
        self.no_execution = no_execution
        self.prompt_format = prompt_format
        self.prefix_caching = prefix_caching
        self.model = None
        self.tokenizer = None

    def build(self, max_model_len=32768, gpu_memory_utilization=0.90):
        print("Loading model and tokenizer...")
        if self.use_vllm:
            self.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_name_or_path, trust_remote_code=True)
            print(f"{'-' * 20} prompt_to_ids {'-' * 20}\n{self.tokenizer.encode('Example prompt')}\n{'-' * 50}", flush=True)
            print(f"eos_token: {self.tokenizer.eos_token}", flush=True)
            self.model = LLM(model=self.model_name_or_path, tokenizer=self.tokenizer_name_or_path, max_model_len=max_model_len, gpu_memory_utilization=gpu_memory_utilization,
                             trust_remote_code=True, tensor_parallel_size=len(os.environ['CUDA_VISIBLE_DEVICES'].split(",")), enable_prefix_caching=self.prefix_caching)
        else:
            raise ValueError("Only VLLM is supported for now.")

    def create_context_caching(self, context):
        raise NotImplementedError


    def generate(self, model_inputs):
        if self.model is None:
            raise ValueError("Model and tokenizer not initialized. Call build() first.")
        if self.use_vllm:
            stop_words = [self.tokenizer.eos_token if self.tokenizer is not None and self.tokenizer.eos_token is not None else '</s>']
            # NOTE Uncomment below for code_int / fewshot
            # if not self.no_execution:
            #     stop_words.append("```output")
            # if self.prompt_format == 'few_shot':
            #     stop_words.extend(prompting.stop_words())
            prompt_token_ids = self.model.get_tokenizer().apply_chat_template(model_inputs, add_generation_prompt=True)
            outputs = self.model.generate(
                prompt_token_ids=prompt_token_ids,
                sampling_params=SamplingParams(
                    temperature=self.temperature, top_p=1.0, max_tokens=self.max_tokens, n=1, stop=stop_words
            ))
            # outputs = sorted(outputs, key=lambda x: int(x.request_id))
            # finish_completion = [output.outputs[0].token_ids[-1] == self.tokenizer.eos_token_id for output in outputs]
            finish_completion = []
            outputs = [output.outputs[0].text for output in outputs]
        else:
            raise ValueError("Only VLLM is supported for now.")

        return outputs, finish_completion

    def streaming_generate(self, model_inputs, batch_size=10):
        assert self.use_vllm, "Streaming generation is only supported for VLLM."

        prompt_token_ids = self.model.get_tokenizer().apply_chat_template(model_inputs, add_generation_prompt=True)
        for i in range(0, len(prompt_token_ids), batch_size):
            batch_prompt_token_ids = prompt_token_ids[i:i + batch_size]
            outputs = self.model.generate(
                prompt_token_ids=batch_prompt_token_ids,
                sampling_params=SamplingParams(
                    temperature=self.temperature, top_p=1.0, max_tokens=self.max_tokens, n=1
                )
            )
            for output in outputs:
                yield output.outputs[0].text
