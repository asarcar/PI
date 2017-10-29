#
# Copyright (c) 2016 Pi Inc. All rights reserved.
#
# Author: asarcar@piekul.com
#
# A singleton-like manager for external and internal interfaces.
#
# We do not typically want to have multiple interface instances for the same
# service. Although we could use a singleton to accomplish this goal, the
# singleton pattern comes with its own bag of problems. In particular, it
# makes it difficult to dynamically stub out interfaces for unit tests.
#
# Usage:
#
#   interfaces = BotInterfaces()
#   bot = interfaces.bot_manager.lookup(bot_uuid)
#

import gflags

from util.interfaces.interfaces import PiInterfaces

FLAGS = gflags.FLAGS

class BotInterfaces(PiInterfaces):
  def __init__(self):
    PiInterfaces.__init__(self)
