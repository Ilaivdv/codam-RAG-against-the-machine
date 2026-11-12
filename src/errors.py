class RagError(Exception):
    """ Custom exception class for verbosity. """
    pass


class CLIError(RagError):
    pass


class IndexError(RagError):
    pass


class SearchError(RagError):
    pass
