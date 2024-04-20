import logging
import os

try:
    os.mkdir("../log")
except FileExistsError:
    pass

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler = logging.FileHandler("../log/app.log")
file_handler.setFormatter(formatter)
handler = logging.StreamHandler()
handler.setFormatter(formatter)

def getDebugLogger(name):
    LOG = logging.getLogger(name)
    LOG.addHandler(file_handler)
    LOG.addHandler(handler)
    LOG.setLevel(logging.DEBUG)
    return LOG
