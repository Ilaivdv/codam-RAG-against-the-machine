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
The pipeline is made with modularity in mind keeping every command seperate, this is what the pipeline looks like:

`ingest/index → search the dataset → evaluate recall -> answer the dataset`

## Chunking Strategy
[langchain_text_splitters](https://reference.langchain.com/python/langchain-text-splitters/langchain_text_splitters) was used for chunking the corpus.
Each .py, .md and .txt file is split into chunks using the `RecursiveCharacterTextSplitter` class and saved into a JSON file holding:
- A chunks file path
- The content that it holds
- The first and last character index of the chunk in the file
- It's last modified time used for caching

## Retrieval Method
[bm25s](https://github.com/xhluca/bm25s) was used for lexical retrieval to find which documents match a user's query best.
It was considered to use a term frequency inverse document length (TF-IDF) implementation first, but best-match 25 (BM25) improves upon it by adding term frequency saturation and document length normalization.

## Performance Analysis
Evaluating the recall can be done using the modules `evaluate` command.
Recalls meet the subjects requirements, 
being a minimum 80% for document retrieval and 50% for code retrieval for recall@5.

|Docs     |Recall  |
|---------|--------|
|Recall@1 |64.0%   |
|Recall@3 |79.0%   |
|Recall@5 |88.0%   |
|Recall@10|91.0%   |
|---------|--------|
|Code     |        |
|---------|--------|
|Recall@1 |33.3%   |
|Recall@3 |49.5%   |
|Recall@5 |58.6%   |
|Recall@10|60.6%   |


## Design Decisions
- This module was made with modularity in mind, every command is reusable and contained seperately in `src/`
- Unit tests were added for easy repetitive tests in case of breaking changes
- The cpu only version of torch was used to shrink installation size and to accomodate CODAM's computers

## Challenges Faced
- Keeping the module simple and not over complicating tasks
- Making every command contained and seperated from one another
- Error handling of all the required path arguments

The biggest struggles faced were complying with the very poorly written subject and 
using the required `pydantic` models which were not structured well and they felt extremely messy to work with at times.

## Resources
- [About TF-IDF compared to BM-25](https://kmwllc.com/index.php/2020/03/20/understanding-tf-idf-and-bm-25/)
- [RAG implementation](https://www.youtube.com/watch?v=pvCabUerwss)
- [Crash course by KodeKloud](https://www.youtube.com/watch?v=swvzKSOEluc)
