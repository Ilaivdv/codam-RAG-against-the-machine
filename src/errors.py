class RagError(ValueError):
    pass


class CLIError(RagError):
    pass


class IndexError(RagError):
    pass


class SearchError(RagError):
    pass
