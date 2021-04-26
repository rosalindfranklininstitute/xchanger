import logging
import sys
from .microservice import MicroService
from .main import main
from .version import __version__
import bugsnag
from bugsnag.handlers import BugsnagHandler

BUGSNAG_API_KEY = "d6d4b4c0f6e866618fbc7c89969649c5"

logger = logging.getLogger('xchanger')


bugsnag.configure(
    api_key=BUGSNAG_API_KEY,
    project_root=".",
    app_version=__version__,
    notify_release_stages=["production"]
)

log_fmt_long = logging.Formatter(
    fmt='%(asctime)s %(name)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# log to stdout
log_handler_stream = logging.StreamHandler(sys.stdout)
log_handler_stream.setFormatter(log_fmt_long)
log_handler_stream.setLevel(logging.DEBUG)
logger.addHandler(log_handler_stream)


# log to bugsnag
log_handler_bugsnag = BugsnagHandler()
log_handler_bugsnag.setLevel(logging.INFO)
logger.addHandler(log_handler_bugsnag)