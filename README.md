*This project has been created as part of the 42 curriculum by ivan-der*

# RAG against the machine
## Description
An implementation of a retrieval-augmented generation (RAG) pipeline
using [langchain_text_splitters](https://reference.langchain.com/python/langchain-text-splitters/langchain_text_splitters), [bm25s](https://github.com/xhluca/bm25s) for indexing and retrieval
and Qwen3-0.6B for answer generation.
The program can chunk, index and retrieve sources from all \*.py, \*.md and \*.txt files from the vLLM repository provided as an example.

## Instructions
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

### Example Usage

## System Architecture

## Chunking Strategy

## Retrieval Method

## Performance Analysis

## Design Decisions

## Challenges Faced

## Resources
