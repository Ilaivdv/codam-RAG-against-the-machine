class ValidationError(ValueError):
    ...


class CLIError(ValidationError):
    ...


class IndexError(ValidationError):
    ...


class SearchError(ValidationError):
    ...
