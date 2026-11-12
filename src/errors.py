class ValidationError(ValueError):
    pass


class CLIError(ValidationError):
    pass


class IndexError(ValidationError):
    pass


class SearchError(ValidationError):
    pass
