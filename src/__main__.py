from src.errors import CLIError, IndexError, SearchError
from json import JSONDecodeError
from .cli import CLI
import fire
import os


if __name__ == "__main__":
    try:
        print("\033c")
        with open("src/logo.txt") as f:
            print("\033[31m" + f.read() + "\033[39m")
        fire.Fire(CLI)
    except (CLIError, IndexError,
            SearchError, JSONDecodeError) as e:
        print(e)
