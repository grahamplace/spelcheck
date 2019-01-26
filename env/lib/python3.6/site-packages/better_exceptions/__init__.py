"""Beautiful and helpful exceptions

Just set your `BETTER_EXCEPTIONS` environment variable. It handles the rest.


   Name: better_exceptions
 Author: Josh Junon
  Email: josh@junon.me
    URL: github.com/qix-/better-exceptions
License: Copyright (c) 2017 Josh Junon, licensed under the MIT license
"""

from __future__ import absolute_import
from __future__ import print_function

import logging
import sys

from .formatter import THEME, MAX_LENGTH, PY3, ExceptionFormatter
from .color import SUPPORTS_COLOR, STREAM
from .log import BetExcLogger, patch as patch_logging


__version__ = '0.2.1.post6'


THEME = THEME.copy()  # Users customizing the theme should not impact core


def write_stream(data):
    STREAM.write(data)


def format_exception(exc, value, tb):
    # Rebuild each time to take into account any changes made by the user to the global parameters
    formatter = ExceptionFormatter(colored=SUPPORTS_COLOR, theme=THEME, max_length=MAX_LENGTH,
                                   encoding=STREAM.encoding)
    return formatter.format_exception(exc, value, tb)


def excepthook(exc, value, tb):
    formatted = format_exception(exc, value, tb)
    for line in formatted:
        write_stream(line)


def hook():
    sys.excepthook = excepthook

    logging.setLoggerClass(BetExcLogger)
    patch_logging()

    if hasattr(sys, 'ps1'):
        print('WARNING: better_exceptions will only inspect code from the command line\n'
              '         when using: `python -m better_exceptions\'. Otherwise, only code\n'
              '         loaded from files will be inspected!', file=sys.stderr)
