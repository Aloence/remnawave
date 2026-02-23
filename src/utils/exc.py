class RequestError(Exception):
    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        body: str | bytes | None = None,
    ):
        self.body = body
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(Exception):
    def __init__(self, message: str = "Not found"):
        self.message = message
        super().__init__(message)
