from loguru import logger
import os
import sys

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger.remove()  

logger.add(
    os.path.join(LOG_DIR, "app.log"),
    rotation="500 KB",      
    # retention="7 days",     
    compression=None,       
    level="INFO",
    format="{time} | {level} | {message}",
)

logger.add(sys.stdout, level="INFO", format="{time} | {level} | {message}")