class AsyncNotify():
        '''Class to trigger a function via PostgreSQL NOTIFY messages. 
Refer to the documentation for more information on LISTEN, NOTIFY and UNLISTEN. 
http://www.postgresql.org/docs/8.3/static/sql-notify.html

This obscure feature is very useful. You can create a trigger function on a
table that executes the NOTIFY command. Then any time something is inserted,
updated or deleted your Python function will be called using this class.

As far as I know this is unique to PostgreSQL. I have no use for any other server :-)'''

        def __init__(self, dsn):
                '''The dsn is passed here. This class requires the psycopg2 driver.'''
                import psycopg2
                self.conn = psycopg2.connect(dsn)
                self.conn.set_isolation_level(0)
                self.curs = self.conn.cursor()
                self.__listening = False

        def __listen(self):
                from select import select
                if self.__listening:
                        return 'already listening!'
                else:
                        self.__listening= True
                        while self.__listening:
                                if select([self.curs],[],[],60)!=([],[],[]) and self.curs.isready():
                                        if self.curs.connection.notifies:
                                                pid, notify = self.curs.connection.notifies.pop()
                                                self.gotNotify(pid, notify)

        def addNotify(self, notify):
                '''Subscribe to a PostgreSQL NOTIFY'''
                sql = "LISTEN %s" % notify
                self.curs.execute(sql)

        def removeNotify(self, notify):
                '''Unsubscribe a PostgreSQL LISTEN'''
                sql = "UNLISTEN %s" % notify
                self.curs.execute(sql)

        def stop(self):
                '''Call to stop the listen thread'''
                self.__listening = False

        def run(self):
                '''Start listening in a thread and return that as a deferred'''
                from twisted.internet import threads
                return threads.deferToThread(self.__listen)

        def gotNotify(self, pid, notify):
                '''Called whenever a notification subscribed to by addNotify() is detected.
Unless you override this method and do someting this whole thing is rather pointless.'''
                pass