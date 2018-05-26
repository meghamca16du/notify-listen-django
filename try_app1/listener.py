from pubsub import pub
# ------------ create a listener ------------------

def listener1(arg1, arg2=None):
    print('Function listener1 received:')
    print('  arg1 =', arg1)
    print('  arg2 =', arg2)

def myfunc():
    print('heloooooo')


# ------------ register listener ------------------

pub.subscribe(listener1, 'rootTopic')

pub.subscribe(myfunc,'topic2')