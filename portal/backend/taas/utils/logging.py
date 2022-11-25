import logging


def create_logger(name, log_path):
    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()

    # Create handlers
    ch = logging.StreamHandler()
    fh = logging.FileHandler(log_path)
    ch.setLevel(logging.INFO)
    fh.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    cf = logging.Formatter('%(asctime)s - %(message)s')
    ff = logging.Formatter('%(asctime)s - %(message)s')
    ch.setFormatter(cf)
    fh.setFormatter(ff)

    # Add handlers to the logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger
