import time
import os
import json
from collections import deque
from typing import List

from google import genai
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception
from google.api_core.exceptions import GoogleAPIError
# from google.generativeai.types import HarmCategory, HarmBlockThreshold

class GeminiLLM:
    def __init__(self, model_name: str = 'gemini-2.0-flash-thinking-exp'):
        api_key = os.environ.get('GEMINI_KEY')
        self.client = genai.Client(api_key=api_key, http_options={'api_version':'v1alpha'})
        self.model_name = model_name
        self.rate_limit_queue = deque(maxlen=10)  # Track last 10 call timestamps
        self.default_config = {'thinking_config': {'include_thoughts': True}}
        if os.path.exists("outputs/gemini_cache.txt"):
            with open("outputs/gemini_cache.txt", "r") as f:
                self.cache = json.load(f)
        else:
            self.cache = {}

    def generate(self, prompts: List[str], sampling_params: dict) -> List[str]:
        outputs = []
        for prompt in prompts:
            self._enforce_rate_limit()
            
            config = {
                "temperature": sampling_params.get('temperature', 0.7),
                **self.default_config
            }
            print(f"Generating for prompt: {prompt}")
            if prompt in self.cache:
                print("Using cached response")
                outputs.append(self.cache[prompt])
                continue
            response = self._generate_with_retry(prompt, config)
            outputs.append(self._parse_response(response))
            self.cache[prompt] = outputs[-1]
            with open("outputs/gemini_cache.txt", "w") as f:
                json.dump(self.cache, f)
            
        return outputs

    def _enforce_rate_limit(self):
        """Ensure we don't exceed 10 requests per minute"""
        now = time.time()
        
        if len(self.rate_limit_queue) == 10:
            # Check if oldest request was within the last minute
            oldest = self.rate_limit_queue[0]
            elapsed = now - oldest
            if elapsed < 60:
                sleep_time = 60 - elapsed
                time.sleep(sleep_time)
        
        self.rate_limit_queue.append(time.time())

    def _generate_with_retry(self, prompt: str, config: dict):
        max_retries = 200
        retry_wait_seconds = 60  # 1 minutes
        attempt = 0
        
        while attempt <= max_retries:
            try:
                return self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
            # except genai.errors.ServerErro as e:
            #     attempt += 1
            #     if attempt <= max_retries:
            #         print(f"Rate limit exceeded. Retry attempt {attempt}/{max_retries}")
            #         print(f"Waiting {retry_wait_seconds//60} minutes before retrying...")
            #         time.sleep(retry_wait_seconds)
            #     else:
            #         # Re-raise original exception if not retrying
            #         print(f"API Error: {str(e)}")
            #         raise
            except Exception as e:
                attempt += 1
                if attempt <= max_retries:
                    print(f"Unexpected error: {str(e)}")
                    time.sleep(retry_wait_seconds)
                else:
                    # Re-raise original exception if not retrying
                    print(f"API Error: {str(e)}")
                    raise

        # This should never be reached due to the raise above
        raise RuntimeError("Max retries exceeded unexpectedly")

    def _parse_response(self, response) -> str:
        """Parse Gemini response and concatenate all text parts"""
        
        if response.candidates is None or response.candidates[0].content is None:
            return "No response"
        parts = response.candidates[0].content.parts
        return '\n'.join([part.text for part in parts])

# Usage example:
# llm = GeminiLLM(api_key='your_api_key')
# outputs = llm.generate(
#     ["Explain quantum computing in simple terms"],
#     {'temperature': 0.5, 'top_p': 0.9, 'max_tokens': 1024}
# )