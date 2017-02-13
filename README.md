# lvalertHeartbeat

This module implements a basic functionality monitor for lvalert_listen instances via the LVAlert system itself. 
We provide 2 executables

  - a client-side executable that knows how to parse and respond to json packets.
  - a server-side executable that sends json packets, listens for responses, and determines whether the behavior is expected.

The scope is to make this a callable service that can be plugged into Nagios.

## prerequisites

this package depends on some standard libraries in addition to LVAlert.
