class InvalidInput(Exception):
    def __init__(self, subject: str, reason: str) -> None:
        """Stores the rejected data and why it was rejected.

        :param subject: the name of the rejected data.
        :param reason: why that data is rejected.

        :return: an error whose message is "{subject}: {reason}".
        The caller can read subject and reason.
        """
        self.subject = subject
        self.reason = reason
        super().__init__(f"{subject}: {reason}")
