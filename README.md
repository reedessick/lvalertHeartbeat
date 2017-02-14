# lvalertHeartbeat

This module implements a basic functionality monitor for lvalert_listen instances via the LVAlert system itself. 
Specifically, this is meant to identify cases when listeners become wedged and are no longer responsive but nonetheless persist in the process table, thereby fooling the current Nagios monitors and failing silently.

The scope is to make this a callable service that can be plugged into Nagios, possibly replacing the current monitors completely.

## executables

We provide 3 executables

  - lvalert_heartbeat-server
      - a server-side executable that sends json packets, listens for responses, and determines whether the behavior is expected.
  - lvalert_heartbeat-client
      - a client-side executable that knows how to parse and respond to requests.
  - lvalert_heartbeat-test
      - a simple testing suite that ensures the libraries work as expected.

## libraries

There are 2 modules included 

  - lvalert_heartbeat.py
      - the workhorse module containing class definitions and utility functions for interfacing with the LVAlert system as a whole as well as formatting, sending, parsing, and generally dealing with heartbeat requests and responses. The executables provided are essentially wrappers around the functions defined herein.
  - lvalertMP_heartbeat.py
      - provides extensions to lvalertMP classes necessary for responding to heartbeat requests. Also provides a simple function that can be called within parse_alert if other libraries wish to implement this.

## dependencies

This package depends on some standard Python libraries in addition to LVAlert and lvalertMP.
