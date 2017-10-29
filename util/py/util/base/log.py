#
# Copyright (c) 2016 Pi Inc. All rights reserved.
#
# Author: asarcar@piekul.com
#
# Example:
#
#   from log import *
#   import log
#
#   log.initialize("foo.log")
#   INFO("A log message")
#
#   x = 10
#   y = 5 + 5
#   CHECK_EQ(x, y)
#
__all__ = [ "initialize", "DEBUG", "INFO", "WARNING", "ERROR", "FATAL",
            "CHECK", "CHECK_EQ", "CHECK_NE", "CHECK_LT", "CHECK_LE",
            "CHECK_GT", "CHECK_GE" ]

import logging
import os
import sys
import traceback

import gflags

FLAGS = gflags.FLAGS

gflags.DEFINE_string("logfile",
                     None,
                     "If specified, logfile to write to.")

gflags.DEFINE_boolean("debug",
                      "PI_LOG_DEBUG" in os.environ,
                      "If True, enable DEBUG log messages.")

gflags.DEFINE_boolean("use_sys_exit_on_fatal",
                      False,
                      "If True, use sys.exit() rather than os._exit() to end "
                      "the process on FATAL errors.")

gflags.DEFINE_boolean("logtostderr",
                      False,
                      "If True, log to stderr instead of a log file.")

class LogLevel:
  """
  Logging severity level.
  """
  (kEmergency, kAlert, kCritical, kError, kWarn,
      kNotice, kInfo, kDebug) = range(8)

class _PiLogger(object):
  """
  The method logging.getLogger already has singleton behavior. But we need to
  prevent adding handles multiple times to the same logger. Hence this class is
  used to help store the logger and remember that we already initialized.
  """
  _pi_logger = None
  _min_log_level = logging.INFO

def initialize(logfile=None):
  """
  Initialize logging subsystem to log to the file 'logfile'.

  If 'logfile' is None and environment variable PI_LOG_DIR is unset, then
  log messages go to stdout. If 'logfile' is None and the PI_LOG_DIR
  environment variable has a path to a directory, then log file is created in
  that directory with the current script name and a ".log" extension.
  """
  if _PiLogger._pi_logger:
    # Initialization already done.
    return

  # Both --logtostderr and --logfile should not be set.
  CHECK(not FLAGS.logtostderr or not logfile,
        "--logtostderr and --logfile are mutually exclusive options")

  # Set up log_handler to either a file or stderr.
  log_handler = None
  if not FLAGS.logtostderr:
    if not logfile and os.environ.has_key("PI_LOG_DIR") and \
        os.path.isdir(os.environ["PI_LOG_DIR"]):

      logfile = os.path.join(
        os.environ["PI_LOG_DIR"],
        os.path.basename(os.path.splitext(sys.argv[0])[0]) + ".log")

  if logfile:
    log_handler = logging.FileHandler(filename=logfile)
  else:
    log_handler = logging.StreamHandler() # Defaults to stderr.

  formatter = logging.Formatter("%(asctime)s %(levelname)s %(file_line)s "
                                "%(message)s", datefmt="%Y-%m-%d %H:%M:%S")
  log_handler.setFormatter(formatter)

  _PiLogger._pi_logger = logging.getLogger("util.base.log")
  _PiLogger._pi_logger.addHandler(log_handler)
  # Propagate ensures messages don't get passed to parent loggers till root.
  _PiLogger._pi_logger.propagate = False
  _PiLogger._logfile = logfile
  update_min_log_level()

def DEBUG(msg, **kwargs):
  if _PiLogger._min_log_level > logging.DEBUG:
    return
  if hasattr(msg, "__call__"):
    msg = msg()
  if not kwargs:
    kwargs = { "file_line" : _compute_file_line() }
  if _PiLogger._pi_logger:
    _PiLogger._pi_logger.debug(msg, extra=kwargs)
  else:
    logging.debug(msg, extra=kwargs)

def INFO(msg, **kwargs):
  if _PiLogger._min_log_level > logging.INFO:
    return
  if hasattr(msg, "__call__"):
    msg = msg()
  if not kwargs:
    kwargs = { "file_line" : _compute_file_line() }
  if _PiLogger._pi_logger:
    _PiLogger._pi_logger.info(msg, extra=kwargs)
  else:
    logging.info(msg, extra=kwargs)

def WARNING(msg, **kwargs):
  if _PiLogger._min_log_level > logging.WARNING:
    return
  if hasattr(msg, "__call__"):
    msg = msg()
  if not kwargs:
    kwargs = { "file_line" : _compute_file_line() }
  if _PiLogger._pi_logger:
    _PiLogger._pi_logger.warning(msg, extra=kwargs)
  else:
    logging.warning(msg, extra=kwargs)

def ERROR(msg, **kwargs):
  if _PiLogger._min_log_level > logging.ERROR:
    return
  if hasattr(msg, "__call__"):
    msg = msg()
  if not kwargs:
    kwargs = { "file_line" : _compute_file_line() }
  if _PiLogger._pi_logger:
    _PiLogger._pi_logger.error(msg, extra=kwargs)
  else:
    logging.error(msg, extra=kwargs)

def FATAL(msg, **kwargs):
  if hasattr(msg, "__call__"):
    msg = msg()
  if not kwargs:
    kwargs = { "file_line" : _compute_file_line() }
  if _PiLogger._pi_logger:
    _PiLogger._pi_logger.critical(msg, extra=kwargs)
  else:
    logging.critical(msg, extra=kwargs)

  logging.shutdown()
  if FLAGS.use_sys_exit_on_fatal:
    sys.exit(1)
  else:
    os._exit(1)

def CHECK(expr, msg=""):
  if not expr:
    stack_frames = traceback.format_stack()
    stack_str = "".join(stack_frames[0:len(stack_frames) - 1]).strip()
    if msg:
      log_msg = "%s, Stack:\n%s" % (msg, stack_str)
    else:
      log_msg = stack_str
    kwargs = { "file_line" : _compute_file_line() }
    FATAL(log_msg, **kwargs)

def CHECK_EQ(expr1, expr2, msg=""):
  if expr1 != expr2:
    stack_frames = traceback.format_stack()
    stack_str = "".join(stack_frames[0:len(stack_frames) - 1]).strip()
    if msg:
      log_msg = "%s == %s failed, %s, Stack:\n%s" % \
        (str(expr1), str(expr2), msg, stack_str)
    else:
      log_msg = "%s == %s failed, Stack:\n%s" % \
        (str(expr1), str(expr2), stack_str)
    kwargs = { "file_line" : _compute_file_line() }
    FATAL(log_msg, **kwargs)

def CHECK_NE(expr1, expr2, msg=""):
  if expr1 == expr2:
    stack_frames = traceback.format_stack()
    stack_str = "".join(stack_frames[0:len(stack_frames) - 1]).strip()
    if msg:
      log_msg = "%s != %s failed, %s, Stack:\n%s" % \
        (str(expr1), str(expr2), msg, stack_str)
    else:
      log_msg = "%s != %s failed, Stack:\n%s" % \
        (str(expr1), str(expr2), stack_str)
    kwargs = { "file_line" : _compute_file_line() }
    FATAL(log_msg, **kwargs)

def CHECK_LT(expr1, expr2, msg=""):
  if not expr1 < expr2:
    stack_frames = traceback.format_stack()
    stack_str = "".join(stack_frames[0:len(stack_frames) - 1]).strip()
    if msg:
      log_msg = "%s < %s failed, %s, Stack:\n%s" % \
        (str(expr1), str(expr2), msg, stack_str)
    else:
      log_msg = "%s < %s failed, Stack:\n%s" % \
        (str(expr1), str(expr2), stack_str)
    kwargs = { "file_line" : _compute_file_line() }
    FATAL(log_msg, **kwargs)

def CHECK_LE(expr1, expr2, msg=""):
  if not expr1 <= expr2:
    stack_frames = traceback.format_stack()
    stack_str = "".join(stack_frames[0:len(stack_frames) - 1]).strip()
    if msg:
      log_msg = "%s <= %s failed, %s, Stack:\n%s" % \
        (str(expr1), str(expr2), msg, stack_str)
    else:
      log_msg = "%s <= %s failed, Stack:\n%s" % \
        (str(expr1), str(expr2), stack_str)
    kwargs = { "file_line" : _compute_file_line() }
    FATAL(log_msg, **kwargs)

def CHECK_GT(expr1, expr2, msg=""):
  if not expr1 > expr2:
    stack_frames = traceback.format_stack()
    stack_str = "".join(stack_frames[0:len(stack_frames) - 1]).strip()
    if msg:
      log_msg = "%s > %s failed, %s, Stack:\n%s" % \
        (str(expr1), str(expr2), msg, stack_str)
    else:
      log_msg = "%s > %s failed, Stack:\n%s" % \
        (str(expr1), str(expr2), stack_str)
    kwargs = { "file_line" : _compute_file_line() }
    FATAL(log_msg, **kwargs)

def CHECK_GE(expr1, expr2, msg=""):
  if not expr1 >= expr2:
    stack_frames = traceback.format_stack()
    stack_str = "".join(stack_frames[0:len(stack_frames) - 1]).strip()
    if msg:
      log_msg = "%s >= %s failed, %s, Stack:\n%s" % \
        (str(expr1), str(expr2), msg, stack_str)
    else:
      log_msg = "%s >= %s failed, Stack:\n%s" % \
        (str(expr1), str(expr2), stack_str)
    kwargs = { "file_line" : _compute_file_line() }
    FATAL(log_msg, **kwargs)

def debug_enabled():
  """
  Check if the logger level DEBUG is enabled or not.

  Returns:
    (boolean): True if DEBUG level is enabled.
  """
  return _PiLogger._min_log_level <= logging.DEBUG

def _compute_file_line():
  """
  Internal method to compute the file name and line number of the caller on
  various methods in this module.

  Example:

    [-1] <caller>
    [-2] INFO
    [-3] _compute_file_name
  """
  frame = traceback.extract_stack()[-3]
  file_name = frame[0].split("/")[-1]
  line_num = frame[1]
  return "%s:%d" % (file_name, line_num)

def update_min_log_level():
  """
  Update logger level to debug or info
  based on gFlags.

  """
  if FLAGS.debug:
    min_log_level = logging.DEBUG
  else:
    min_log_level = logging.INFO
  _PiLogger._pi_logger.setLevel(min_log_level)
  _PiLogger._min_log_level = min_log_level
