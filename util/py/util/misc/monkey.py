#
# Copyright (c) 2016 Pi Inc. All rights reserved.
#
# Author: asarcar@piekul.com
#
# Monkey patch python modules or methods.
#
from __future__ import absolute_import
import gflags
from gflags import BooleanFlag
import sys

__all__ = ['patch_all',
           'patch_gflags']

FLAGS = gflags.FLAGS

def patch_all(gflags=True):
  """
  Dl all of the default monkey patching (calls every other function in this
  module.
  """
  if gflags:
    patch_gflags()

class HelpFlag(BooleanFlag):
  """
  HelpFlag is a special boolean flag that prints usage information and
  raises a SystemExit exception if it is ever found in the command
  line arguments.  Note this is called with allow_override=1, so other
  apps can define their own --help flag, replacing this one, if they want.
  """
  def __init__(self):
    BooleanFlag.__init__(self, "help", 0, "show this help",
                         short_name="?", allow_override=True)
  def Parse(self, arg):
    if arg:
      doc = sys.modules["__main__"].__doc__
      flags = str(FLAGS)
      print doc or ("\nUSAGE: %s [flags]\n" % sys.argv[0])
      if flags:
        print "flags:"
        print flags
      sys.exit(1)
class HelpXMLFlag(BooleanFlag):
  """Similar to HelpFlag, but generates output in XML format."""
  def __init__(self):
    BooleanFlag.__init__(self, 'helpxml', False,
                         'like --help, but generates XML output',
                         allow_override=True)
  def Parse(self, arg):
    if arg:
      FLAGS.WriteHelpInXMLFormat(sys.stdout)
      sys.exit(1)
class HelpshortFlag(BooleanFlag):
  """
  HelpshortFlag is a special boolean flag that prints usage
  information for the "main" module, and rasies a SystemExit exception
  if it is ever found in the command line arguments.  Note this is
  called with allow_override=1, so other apps can define their own
  --helpshort flag, replacing this one, if they want.
  """
  def __init__(self):
    BooleanFlag.__init__(self, "helpshort", 0,
                         "show usage only for this module", allow_override=True)
  def Parse(self, arg):
    if arg:
      doc = sys.modules["__main__"].__doc__
      flags = FLAGS.MainModuleHelp()
      print doc or ("\nUSAGE: %s [flags]\n" % sys.argv[0])
      if flags:
        print "flags:"
        print flags
      sys.exit(1)
  
def patch_gflags():
  """
  Added special flags:
   --help          prints a list of all the flags in a human-readable fashion
   --helpshort     prints a list of all key flags (see below).
   --helpxml       prints a list of all flags, in XML format.  DO NOT parse
                   the output of --help and --helpshort.  Instead, parse
                   the output of --helpxml.  For more info, see
                   "OUTPUT FOR --helpxml" below.
  """
  if "HelpFlag" not in dir( gflags ):
    gflags.DEFINE_flag(HelpFlag())
  if "HelpXMLFlag" not in dir( gflags ):
    gflags.DEFINE_flag(HelpXMLFlag())
  if "HelpshortFlag" not in dir( gflags ):
    gflags.DEFINE_flag(HelpshortFlag())
