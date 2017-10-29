#
# Copyright (c) 2016 PieKul Inc. All rights reserved.
#
# Author: asarcar@piekul.com
#
# Module defines a singleton that will dynamically create clients/resolvers.
#
# Usage:
#
#   interfaces = PiInterfaces()
#   zk_session = interfaces.zk_session

import threading

from util.base import log

__all__ = [
    "PiInterfaces",
    "PiInterfacesError",
]

class PiInterfacesError(Exception):
  pass

class PiInterfaces(object):
  def __init__(self):
    self._lock = threading.RLock()

  def __getattr__(self, name):
    log.CHECK(not (name.startswith("_") and not name.startswith("__")), name)
    # Threads may race to instantiate an interface. Check the object dictionary
    # first to determine whether the current thread lost the race.
    with self._lock:
      try:
        return self.__dict__[name]
      except KeyError:
        method_name = "_%s" % (name,)
        instance = getattr(self, method_name)()
        setattr(self, name, instance)
        return instance

  # Clients.
  def _agent_client(self):
    from agent.client.client import AgentClient
    return AgentClient()
