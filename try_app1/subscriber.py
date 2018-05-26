from pubsub import pub
# ---------------- send a message ------------------

print('Publish something via pubsub')
anObj = dict(a=456, b='abc')
pub.sendMessage('rootTopic', arg1=123, arg2=anObj)
pub.sendMessage('rootTopic', arg1=678, arg2=anObj)
pub.sendMessage('rootTopic', arg1=910, arg2=anObj)

print('\n \n')
#pub.sendMessage('topic2')