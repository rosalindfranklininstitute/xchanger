import logging
import sys
from .microservice import MicroService
from .main import main
logger = logging.getLogger('xchanger')
logger.setLevel(logging.DEBUG)

log_fmt_long = logging.Formatter(
    fmt='%(asctime)s %(name)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# log to stdout
log_handler_stream = logging.StreamHandler(sys.stdout)
log_handler_stream.setFormatter(log_fmt_long)
log_handler_stream.setLevel(logging.DEBUG)
logger.addHandler(log_handler_stream)