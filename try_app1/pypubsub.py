"""
One listener is subscribed to a topic called 'rootTopic'.
One 'rootTopic' message gets sent. 
"""


"""
:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.
"""

from pubsub import pub


# ------------ create some listeners --------------

class Listener:
    def onTopic11(self, msg, extra=None):
        print('Method Listener.onTopic11 received: ', repr(msg), repr(extra))

    def onTopic1(self, msg, topic=pub.AUTO_TOPIC):
        info = 'Method Listener.onTopic1 received "%s" message: %s'
        print(info % (topic.getName(), repr(msg)))

    def __call__(self, **kwargs):
        print('Listener instance received: ', kwargs)


listenerObj = Listener()


def listenerFn(msg, extra=None):
    print('Function listenerFn received: ', repr(msg), repr(extra))


# ------------ subscribe listeners ------------------

pub.subscribe(listenerObj, pub.ALL_TOPICS)  # via its __call__

pub.subscribe(listenerFn, 'topic1.subtopic11')
pub.subscribe(listenerObj.onTopic11, 'topic1.subtopic11')

pub.subscribe(listenerObj.onTopic1, 'topic1')



'''
"""
One listener is subscribed to a topic called 'rootTopic'.
One 'rootTopic' message gets sent. 
"""

from pubsub import pub


# ------------ create a listener ------------------

def listener1(arg1, arg2=None):
    print('Function listener1 received:')
    print('  arg1 =', arg1)
    print('  arg2 =', arg2)


# ------------ register listener ------------------

pub.subscribe(listener1, 'rootTopic')

# ---------------- send a message ------------------

print('Publish something via pubsub')
anObj = dict(a=456, b='abc')
pub.sendMessage('rootTopic', arg1=123, arg2=anObj)
'''