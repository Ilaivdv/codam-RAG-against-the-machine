.PHONY: install run debug clean fclean lint lint-strict test eval_docs eval_code
.DEFAULT_GOAL: run
PY = python3

FLAKE8 = uv run $(PY) -m flake8 . --exclude=.venv/,data/
MYPY = uv run $(PY) -m mypy .
MYPYFLAGS = --warn-return-any \
	--warn-unused-ignores --ignore-missing-imports \
	--disallow-untyped-defs --check-untyped-defs \
	--disallow-subclassing-any

VLLM_REPO = vllm-0.10.1.zip
DATASET_PATH = datasets_public
OUTPUT_PATH = data/output/search_results

run: install
	@ uv run --quiet $(PY) -m src index 2000
	@ uv run --quiet $(PY) -m src search_dataset $(DATASET_PATH)/public/UnansweredQuestions/dataset_code_public.json 5 $(OUTPUT_PATH)/code/
	@ uv run --quiet $(PY) -m src search_dataset $(DATASET_PATH)/public/UnansweredQuestions/dataset_docs_public.json 5 $(OUTPUT_PATH)/docs/

eval-docs:
	@ uv run --quiet $(PY) -m src evaluate $(OUTPUT_PATH)/docs/dataset_docs_public.json $(DATASET_PATH)/public/AnsweredQuestions/dataset_docs_public.json

eval-code:
	@ uv run --quiet $(PY) -m src evaluate $(OUTPUT_PATH)/code/dataset_code_public.json $(DATASET_PATH)/public/AnsweredQuestions/dataset_code_public.json

debug: install
	@ uv run $(PY) -m pdb -m src

install:
	@ uv sync --link-mode=copy
	@ mkdir -p data/raw/
	@ unzip -u $(VLLM_REPO) -d data/raw/
	@ unzip -u $(DATASET_PATH).zip

lint:
	-@ $(FLAKE8)
	-@ $(MYPY) $(MYPYFLAGS)

lint-strict:
	-@ $(FLAKE8)
	-@ $(MYPY) --strict

clean:
	-find . -type d -name "__pycache__" -exec rm -rf {} +
	-find . -type d -name ".mypy_cache" -exec rm -rf {} +
	-find . -type d -name ".pytest_cache" -exec rm -rf {} +
	-find . -name "*.egg-info*" -exec rm -rf {} +

fclean: clean
	-rm -rf data/* .venv/ $(DATASET_PATH)

test: install
	@ uv run $(PY) -m pytest -v tests
