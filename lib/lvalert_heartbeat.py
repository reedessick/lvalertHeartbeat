description = "a module housing useful functions for the heartbeat monitoring of lvalert_listen processes"
author = "Reed Essick (reed.essick@ligo.org)"

#-------------------------------------------------

import os
import socket
import binascii

import multiprocessing as mp

import json

from ligo.lvalert import pubsub

from pyxmpp.all import JID
from pyxmpp.all import TLSSettings
from pyxmpp.jabber.all import Client

#-------------------------------------------------

class HeartbeatClient(Client):
    """
    lifted with some modification from lvalert_listen and lvalert_send
    """

    def __init__(self, jid, password, node, key, connection=None, retry=0, verbose=False):
        self.jid = jid
        self.node = node
        self.retry = retry
        self.counter = 0

        self.verbose=verbose
        # setup client with provided connection information and identity data
        super(HeartbeatClient, self).__init__(self, self.jid, password,
            auth_methods=["sasl:GSSAPI", "sasl:PLAIN"],
            tls_settings=TLSSettings(require=True, verify_peer=False),
            keepalive=30,
        )

        self.interface_providers = [HeartbeatHandler(self, connection, key)] ### what to do when receiving messages

    def sendMessage(self, message, recipient):
        """
        lifted with only minimal modifications from lvalert_send
        """
        ps = pubsub.PubSub(from_jid=self.jid, to_jid=recipientt, stream=self.stream, stanza_type="get")
        ps.publish(message, self.node)
        self.stream.set_response_handlers(ps, self.onSuccess, self.onError, lambda stanza: self.onTimeout(stanza, message, recipient))
        self.stream.send(ps)

    def onSuccess(self, stanza):
        """
        lifted with only minimal modifications from lvalert_send
        """
        if self.verbose:
            print( "success" )
        return True

    def onError(self, stanza):
        """
        lifted with only minimal modifications from lvalert_send
        """
        errorNode = stanza.get_error()
        if self.verbose:
            print( "error type = %s"%errorNode.get_type() )
            print( "error message = %s"%errorNode.get_message() )
        raise RuntimeError

    def onTimeout(self, stanza, message, recipient):
        """
        lifted with only minimal modifications from lvalert_send
        """
        if self.verbose:
            print("operation timed out.  Trying again...")
        if self.counter < self.retry:
            self.counter += + 1
            self.sendMessage(self.node, message, recipient)
        else:
            if self.verbose:
                print("Reached max_attempts. Disconnecting...")
            raise RuntimeError
        return True

#------------------------

class HeartbeatHandler(object):
    """
    lifted with some modification from lvalert_listen
    """

    def __init__(self, client, connection, key):
        self.client = client
        self.connection = connection
        self.key = key

    def message(self, stanza):
        """
        returns True to show that the stanza should not be processed further
        """
        ### extract the node from the stanza
        node = stanza.xmlnode.children.children
        if node:
            node = node.prop("node")
        else:
            raise RuntimeError, "could not extract node from stanza"

        if node!=client.node: ### we're not interested in this node, so we just return True
            return True

        ### extract the content from the stanza
        c = stanza.xmlnode.children
        while c:
            try:
                if c.name=="event":
                    entry = c.getContent()
                    break
            except libxml2.treeError:
                c.next
        else:
            raise RuntimeError, "could not extract entry from stanza"
        
        ### process entry
        packet = Packet(None, client.node)
        packet.loads( entry )
        if packet.isResponse() and (packet['key']==self.key): ### send this if it's interesting and we have a connection
            if connection!=None:
                connection.send( packet )
            elif self.client.verbose:
                print( "RESPONSE: "+packet.dumps() )
        elif self.client.verbose:
            print( "UNKNOWN: "+packet.dumps() )

        return True

#------------------------

class Packet(dict):
    """
    an extension of a dictionary specifically for the heartbeat functionality
    """

    def __init__(self, server, node, ptype=None, **kwargs):
        super(Packet, self).__init__([('ptype',ptype), ('server',server), ('node',node)])
        self.update(kwargs)

    def dump(self, fp, **kwargs):
        json.dump(self, fp, **kwargs)

    def dumps(self):
        return json.dumps(self)

    def loads(self, string):
        self.parse(json.loads(string))

    def parse(self, alert):
        self.update( alert )

    def isRequest(self):
        return self['ptype']=='request'

    def isResponse(self):
        return self['ptype']=='response'

#-------------------------------------------------

def randkey():
    """
    generate a random key to keep track of which alerts belong to which request
    """
    return binascii.b2a_hex(os.urandom(15))

def send( alert, server, node, netrc, retry=0 ):
    """
    actually sends the alert via the pubsub node
    """
    username, password = netrc.netrc(netrc).authenticators(server)
    client = HeatbeatClient( JID(username+"@"+server+"/"+randkey()), password, node, retry=retry )

    client.connect()
    client.sendMessage(alert.dumps(), JID("pubsub."+server))
    client.disconnect()

#---

def poll(server, node, netrc=os.getenv('NETRC', os.path.join(os.path.expanduser('~'), '.netrc')), wait=1.0, timeout=60, verbose=False):
    """
    send a request and collect the responses sent over a particular node

    creates a client instance, and forks the "loop" into a separate process via multiprocessing (because it blocks)
    reads in responses as they come (through a multiprocessing connection) and times out after a specified amount of time
    """
    ### set up key associated with this request, used in case there are multiple requests sent simulatneously (which shouldn't happen, but this is a safety net)
    key = randkey()

    ### set up listener
    if verbose:
        print( "setting up listener" )
    ### set up multiprocessing connections
    conn1, conn2 = mp.Pipe() 

    ### set up the client
    username, password = netrc.netrc(netrc).authenticators(server)
    client = HeartbeatClient( JID(username+"@"+server+"/"+randkey()), password, node, key, connection=conn2 )

    ### set up process
    proc = mp.Process(target=client.loop, args=(wait)) 
    proc.start() ### start it 
    conn2.close() ### close the forked proc's end of the connection

    ### send a request
    if verbose:
        print( "sending request" )
    request( key, server, node, netrc=netrc, verbose=verbose )

    ### read in responses in a loop
    if verbose:
        print( "listening" )
    responses = []
    end = time.time() + timeout
    while time.time() < end:
        if conn1.poll(): ### there's something to read
            responses.append( conn1.recv() )
        time.sleep(wait)

    ### kill process because we're done with it
    proc.terminate() 

    ### read in any remaining responses
    while conn1.poll():
        responses.append( conn1.recv() )
    conn1.close()

    ### return all the responses received
    if verbose:
        print( "recieved %d responses"%len(responses) )
    return responses

#------------------------

def request( key, server, node, netrc=os.getenv('NETRC', os.path.join(os.path.expanduser('~'), '.netrc')), verbose=False ):
    """
    send out request packets
    """
    ### format and send the packet
    packet = Packet(server, node, ptype='request', key=key)
    if verbose:
        print( "%s->%s : %s"%(server, node, packet.dumps()) )
    send( packet, server, node, netrc )

#---

def respond( name, alert, netrc=os.getenv('NETRC', os.path.join(os.path.expanduser('~'), '.netrc')), verbose=False ):
    """
    parses out the relevant information from the LVAlert json packet and responds as necessary
    """
    if verbose:
        print( "parsing : %s"%alert )
    packet = Packet()
    packet.parse(alert)

    if packet.isRequest():
        packet['ptype'] = 'response' ### change this packet to a "response"
        
        ### fill in pertinent information
        packet['hostname'] = socket.gethostname()
        packet['user'] = getpass.getuser()
        packet['pid'] = os.getpid()
        packet['name'] = name

        ### send the packet
        if verbose:
            print( "sending response : %s"%(packet.dumps()) )
        send( packet, packet['server'], packet['node'], netrc )

    else: ### not a request, so we do nothing
        if verbose:
            print( "ignoring alert" )
