description = "a module housing useful functions for the heartbeat monitoring of lvalert_listenMP processes"
author = "Reed Essick (reed.essick@ligo.org)"

#-------------------------------------------------

from numpy import infty
from lvalertHeartbeat import lvalert_heartbeat

from lvalertMP.lvalert import lvalertMPutils

#-------------------------------------------------

class HeartbeatItem(lvalertMPutils.QueueItem):
    '''
    a wrapper around heartbeat functionality for lvalertMP
    '''
    name = 'heartbeat'
    description = 'a response to heartbeat queries'

    def __init__(self, t0, name, alert, logTag='iQ'):
        tasks = [HeartbeatTask(name, alert, logTag=logTag)]
        super(HeartbeatItem, self).__init__(t0, tasks, logTag=logTag)

class HeartbeatTask(lvalertMPutils.Task):
    '''
    a wrapper around heartbeat functionality for lvalertMP
    '''
    name = 'heartbeat'
    description = 'a response to heartbeat queries'

    def __init__(self, name, alert, logTag='iQ'):
        self.name = name
        self.alert = alert
        timeout = -infty ### do this immediately, always
        super(HeartbeatTask, self).__init__(timeout, logTag=logTag)

    def heartbeat(self, verbose=False):
        '''
        delegate to a helper function
        '''
        lvalert_heartbeat.respond( self.name, self.alert, verbose=verbose )

#-------------------------------------------------

def parse_heartbeat( queue, queueByGraceID, alert, t0, config, logTag='iQ' ):
    '''
    a function that parses alerts specifically for heartbeat packets.
    should be called within parse_alert as needed
    '''
    assert alert['uid']=='heartbeat', 'I only know how to parse alerts with uid="heartbeat"'
    queue.insert( HeartbeatItem( t0, config.get('general','process_type'), alert, logTag=logTag) )
    return 0
