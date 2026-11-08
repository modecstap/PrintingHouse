from collections.abc import Sequence


class InvalidPriceException(Exception):
    pass


class InvalidInput(Exception):
    def __init__(self, subject: str, reason: str | Sequence[str]) -> None:
        """Stores the rejected data and why it was rejected.

        :param subject: the name of the rejected data.
        :param reason: why that data is rejected. A sequence lists every
        failed field and is joined with "; ".

        :return: an error whose message is "{subject}: {reason}".
        The caller can read subject and reason. reason is one string.
        """
        if not isinstance(reason, str):
            reason = "; ".join(reason)
        self.subject = subject
        self.reason = reason
        super().__init__(f"{subject}: {reason}")
