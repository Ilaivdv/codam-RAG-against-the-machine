from .models import MinimalSource
from typing import Any


class LLM:
    """
    LLM class holding the initialized model and tokenizer with a method for
    answer generation.
    """

    def __init__(self, model_name: str) -> None:
        """
        Initializes an LLM model with it's required tokenizer and streamer
        for live output generation.
        """

        from transformers import (
                AutoModelForCausalLM,
                AutoTokenizer,
                TextStreamer,
                set_seed
                )
        set_seed(4242)
        self.model: Any = AutoModelForCausalLM.from_pretrained(
                model_name,
                dtype="auto",
                device_map="cpu",
                )
        self.tokenizer: Any = AutoTokenizer.from_pretrained(model_name)
        self.streamer: TextStreamer = TextStreamer(
                self.tokenizer,
                skip_prompt=True,
                skip_special_tokens=True
                )

    def answer_prompt(self, query: str, sources: list[MinimalSource]) -> str:
        """
        Given a query and its top-k sources, feed it to the initialized model
        and generate an answer with live feedback.

        Arguments:
            query - A single query to give the model
            sources - The retrieved list of sources for the query

        Returns:
            str - The generated answer to the query
        """

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

        print("\033[1A\x1b[2K\033[32m", end="")
        print(f"\033[30m>> {query} <<\033[39m")
        print("\n\033[31m>> \033[39m", end="")
        generated_ids = self.model.generate(
                **model_inputs,
                streamer=self.streamer,
                max_new_tokens=50
                )
        generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(
                    model_inputs.input_ids, generated_ids)]
        response: str = self.tokenizer.batch_decode(
                generated_ids, skip_special_tokens=True)[0]
        print("\033[1A\x1b[2K\033[32m", end="")
        return response
