#
# Copyright (c) 2016 Pi Inc. All rights reserved.
#
# Author: asarcar@piekul.com
#
# This module defines some useful decorators.
#

from functools import wraps

def optional_arg_decorator(decorator):
  """
  This decorator allows other decorators to optionally take arguments.
  """
  @wraps(decorator)
  def wrapped_decorator(*args, **kwargs):
    if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
      return decorator(args[0])
    else:
      return lambda func: decorator(func, *args, **kwargs)

  return wrapped_decorator

@optional_arg_decorator
def fatal_on_exception(func, exc_white_list=()):
  """
  Decorator that makes sure that all exceptions raised by func() will be
  caught with log.FATAL(). This decorator is useful for functions which are
  meant to be called in a separate thread or a subprocess.

  Args:
    func (callable): function to wrap.
    exc_white_list (iterable): List of exceptions which need to be re-raised
      instead of killing the process with log.FATAL().

  """
  @wraps(func)
  def wrapper(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except exc_white_list:
      raise
    except:
      import traceback
      import util.base.log as log
      log.FATAL(traceback.format_exc())

  return wrapper
