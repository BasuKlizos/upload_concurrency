import logging

logger = logging.getLogger("dramatiq_worker")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("worker.log")
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)  # Now logger is defined!

# Also log to console (optional)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)