import singer
import time
import random

LOGGER = singer.get_logger()

def sleep(range_start: int = 45, range_end: int = 90):
    delay = random.randint(range_start, range_end)
    LOGGER.info(f"Sleeping for {delay} seconds.")
    time.sleep(delay)