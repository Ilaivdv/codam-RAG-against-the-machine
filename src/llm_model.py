from .models import MinimalSource
from typing import Any


class LLM:
    def __init__(self, model_name: str) -> None:
        from transformers import (
                AutoModelForCausalLM,
                AutoTokenizer,
                TextIteratorStreamer
                )
        self.model: Any = AutoModelForCausalLM.from_pretrained(
                model_name,
                dtype="auto",
                device_map="cpu",
                )
        self.tokenizer: Any = AutoTokenizer.from_pretrained(model_name)

    def process_prompt(self, query: str, sources: list[MinimalSource]) -> str:
        sources_dict = [s.model_dump() for s in sources]
        messages = [
                {"role": "user", "content": (
                 f"Your role is to reply in only ONE sentence the query: '{
                     query}' using the retrieved sources: '{
                     [t["content"] for t in
                         sources_dict if t.get("content")]}'"
                 )},
                ]
        text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False
                )
        model_inputs = self.tokenizer(
                [text], return_tensors="pt").to(self.model.device)

        generated_ids = self.model.generate(**model_inputs, max_new_tokens=50)
        generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(
                    model_inputs.input_ids, generated_ids)]
        response: str = self.tokenizer.batch_decode(
                generated_ids, skip_special_tokens=True)[0]
        return response
