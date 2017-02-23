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

----------------------------------------------------------------------------------------------------------

## Security risks

Here we briefly discuss possible security risks associated with this monitor and with LVAlert in general.

### Authentication

LVAlert authenticates with username/password pairs stored within .netrc files locally.
Specifically, a connection is established with the server using Python xmpp.JID objects instantiated with `username@server/resource` and verified with a `password`.
These username/password pairs are extracted using the standard Python netrc library

    >> username, _, password = netrc.netrc('path/to/netrc').authenticators('server')

Read/write permissions on these files are managed at the system level with standard Unix tools. 

For the current implementation to work, netrc files will need to be shared between the client-side user and the server-side request.
This is required for multiple processes to publish to the same node; currently only the node's owner can publish to it and therefore both the client-side and server-side processes must authenticate as the owner of a node.
Neither the content nor location of the netrc files will be shared over the LVAlert network.
Only the server's name (e.g.; lvalert.cgca.uwm.edu) is distributed along with the request/response messages.

We expect the only additional security risk associated with lvalertHeartbeat above what is standard for all LVAlert listeners is the one-time risk associated with moving netrc files between machines and the additional risk associated with storing multiple copies of a username/password.

### Consequences of security leaks

The main threat of a compromised username/password pair is a DOS attack on the LVAlert server. 
This would prevent GraceDb from issuing announcements about events and would effectively shut down all automated follow-up.
In particular, it is unlikely that many humans would be woken up for interesting events because that action is prompted by the application of a particular label within GraceDb and the software that applies that label receives information from GraceDb via LVAlert.

Another possible concern is a non-LVC member listening in on alerts which could contain information that is currently not released to electromagnetic observers (e.g.; component masses).
This would not prevent us from actually performing our science but could cause embarrassment.

### Alternate architectures

We may also consider defining the concept of a public LVAlert node.
This would allow multiple username/password pairs to publish to the same node and remove the need to share netrc files between the client and server.
It is unclear whether this is supported within LVAlert at this time.

We could also manage the "response" messages outside of LVAlert, again removing the need to share netrc files.
In particular, if the client-side executable annotated/touched a web-page stored under that user's `public_html`, a Nagios monitor could scrape these web pages and check for updated information.
This invovles more "moving pieces" and it is not clear whether it would be better than the current implementation in the long-run.
