from src.errors import CLIError, IndexError, SearchError
from json import JSONDecodeError
from .cli import CLI
import fire


if __name__ == "__main__":
    try:
        fire.Fire(CLI)
    except (CLIError, IndexError,
            SearchError, JSONDecodeError) as e:
        print(e)
