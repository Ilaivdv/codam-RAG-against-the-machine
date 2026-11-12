"""
Entry point for the RAG pipeline,
prints logo and initializes fire for argument parsing.
"""


from src.errors import CLIError, IndexError, SearchError
from json import JSONDecodeError
from .cli import CLI
import fire


def main() -> None:
    try:
        print("\033c")
        with open("src/logo.txt") as f:
            print("\033[31m" + f.read() + "\033[39m")
        fire.Fire(CLI)
    except (CLIError, IndexError,
            SearchError, JSONDecodeError) as e:
        print(e)


if __name__ == "__main__":
    main()
