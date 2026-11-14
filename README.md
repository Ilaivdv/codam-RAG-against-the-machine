*This project has been created as part of the 42 curriculum by ivan-der*

# RAG against the machine
## Description
An implementation of a retrieval-augmented generation (RAG) pipeline
using [langchain_text_splitters](https://reference.langchain.com/python/langchain-text-splitters/langchain_text_splitters), [bm25s](https://github.com/xhluca/bm25s) for indexing and retrieval
and Qwen3-0.6B for answer generation.
The program can chunk, index and retrieve sources from all \*.py, \*.md and \*.txt files from the vLLM repository provided as an example.

The CLI was made using [fire](https://github.com/google/python-fire) and loading bars were implemented using [tqdm](https://tqdm.github.io/)

## Instructions
### Prerequisites
- Python 3.14+
- [uv package manager](https://docs.astral.sh/uv/)

Below are a list of useful Makefile rules:
```bash
make install     # Extracts vllm-0.10.1.zip into data/raw
make run         # Indexes everything in data/raw/
make debug       # Runs pdb on module src/
make lint        # Runs lint checks (mypy, flake8)
make lint-strict # Runs strict lint checks (mypy --strict, flake8)
make clean       # Removes python artifacts (__pycache__, .mypy_cache, etc.)
make fclean      # Removes artifacts, data/ and .venv
```
### Running The Module
These are the steps for running the pipeline:

1. **Index the corpus:** 
To chunk and index the corpus, run either `make run` or `uv run -m src index --max_chunk_size=<int>`

2. **Search the corpus and retrieve top-k sources:** 
For a single search, use `uv run -m src search --query=<str> --k=<int>`.
To run a search over a JSON dataset of queries and save it to a JSON file, 
run `uv run -m src search_dataset --dataset_path=<str> --k=<int> --save_directory=<str>`

3. **Generate an answer to a query:** 
Getting an llm generated answer from a query can be done either for a single query using
`uv run -m src answer --query<str> --k=<int>`, or with a given JSON of queries and sources made from
`search_dataset` using `uv run -m src answer_dataset --student_search_results_path=<str> --save_directory=<str>`

4. **Evaluate retrieved sources with a recall@k metric (optional):** 
Evaluate the retrieved sources with `uv run -m src evaluate --student_search_results_path=<str> --dataset_path=<str>`.
This will compare the created `StudentSearchResults` against the ground-truth dataset to calculate its recall@k.

### Example Usage
```bash
# First, index the corpus and save it to data/processed/
uv run -m src index 5

# Then, search a dataset of queries and retrieve its most relevant source to save to a JSON file
uv run -m src search_dataset datasets_public/public/UnansweredQuestions/dataset_docs_public.json 5 data/output/UnansweredQuestions
# Also for the code related queries
uv run -m src search_dataset datasets_public/public/UnansweredQuestions/dataset_code_public.json 5 data/output/UnansweredQuestions

# Evaluate the output against a ground-truth dataset
uv run -m src evaluate data/output/UnansweredQuestions/dataset_docs_public.json datasets_public/public/AnsweredQuestions/dataset_docs_public.json
uv run -m src evaluate data/output/UnansweredQuestions/dataset_code_public.json datasets_public/public/AnsweredQuestions/dataset_docs_public.json

# Optionally, generate an answer for each query and also save it to a json (this one can take a while)
uv run -m src answer_dataset data/output/UnansweredQuestions/dataset_docs_public.json data/output/AnsweredQuestions
```
## System Architecture

## Chunking Strategy

## Retrieval Method

## Performance Analysis

## Design Decisions

## Challenges Faced

## Resources
