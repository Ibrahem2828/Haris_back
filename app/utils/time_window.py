from datetime import datetime, timedelta


def window_start(timestamp: datetime, seconds: int) -> datetime:
    return timestamp - timedelta(seconds=seconds)
