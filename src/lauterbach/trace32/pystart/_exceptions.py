class TimeoutExpiredError(Exception):
    pass


class AlreadyRunningError(Exception):
    def __init__(self) -> None:
        super().__init__("For this instance there is already a TRACE32 instance running")
