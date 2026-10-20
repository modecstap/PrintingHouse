class InvalidSheetCountException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidPriceException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InsufficientInkException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidIdException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
