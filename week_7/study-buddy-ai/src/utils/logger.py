import logging

_logger = None


def get_logger(name: str = "study_buddy"):
    global _logger
    if _logger:
        return _logger

    _logger = logging.getLogger(name)
    _logger.setLevel(logging.INFO)

    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    _logger.addHandler(h)

    return _logger
