from .asyncnotify import AsyncNotify
from twisted.internet import reactor

dbname = 'try_app1'
host = 'localhost'
user = 'postgres'
password = 'megha123'

dsn = 'dbname=%s host=%s user=%s password=%s' % (dbname, host, user, password)

def errorHandler(error):
    print(str(error))
    notifier.stop()
    reactor.stop()

def shutdown(notifier):
    print('Shutting down the reactor')
    reactor.stop()

def tableUpdated(notify, pid):
    # This function is called by magic.
    tablename, op = notify.split('_')
    print('%s just occured on %s from process ID %s' % (op, tablename, pid))

class myAsyncNotify(AsyncNotify):
    # gotNotify is called with the notification and pid.
    # Override it and do something great.
    def gotNotify(self, pid, notify):
        if notify == 'quit':
            # The stop method will end the deferred thread
            # which is listening for notifications.
            print('Stopping the listener thread.')
            self.stop()
        elif notify.split('_')[0]  in ('students', 'marks'):
            tableUpdated(notify, pid)
        else:
            print("got asynchronous notification '%s' from process id '%s'" % (notify, pid))

notifier = myAsyncNotify(dsn)

# Start listening for subscribed notifications in a deferred thread.
listener = notifier.run()

# What to do when the AsyncNotify stop method is called to
listener.addCallback(shutdown)
listener.addErrback(errorHandler)

# Call the gotNotify method when any of the following notifies are detected.
notifier.addNotify('test1')
notifier.addNotify('test2')
notifier.addNotify('students_insert')
notifier.addNotify('students_update')
notifier.addNotify('students_delete')
notifier.addNotify('marks_insert')
notifier.addNotify('marks_update')
notifier.addNotify('marks_delete')
notifier.addNotify('quit')

# Unsubscribe from one
reactor.callLater(60, notifier.removeNotify, 'test2')

reactor.run()
