class RagError(Exception):
    """ Custom exception class for verbosity. """
    def __init__(self, msg: str) -> None:
        super().__init__(f"\033[31m\x1b[1mERROR: \033[39m\x1b[0m{msg}")


class CLIError(RagError):
    pass


class IndexError(RagError):
    pass


class SearchError(RagError):
    pass


class EvalError(RagError):
    pass
