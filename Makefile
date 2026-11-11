.PHONY: install run debug clean lint lint-strict
.DEFAULT_GOAL: run
PY = python3

FLAKE8 = uv run $(PY) -m flake8 . --exclude=.venv/,data/
MYPY = uv run $(PY) -m mypy .
MYPYFLAGS = --warn-return-any \
	--warn-unused-ignores --ignore-missing-imports \
	--disallow-untyped-defs --check-untyped-defs \
	--disallow-subclassing-any

VLLM_REPO = vllm-0.10.1.zip

run: install
	@ uv run --quiet $(PY) -m src index 2000

debug: install
	@ uv run $(PY) -m pdb -m src -v

install:
	@ uv sync --link-mode=copy
	@ mkdir -p data/raw/
	@ unzip -u $(VLLM_REPO) -d data/raw/

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

fclean: clean
	-rm -rf data/* .venv/

test: install
	@ uv run $(PY) -m pytest -v tests
