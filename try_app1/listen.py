import select
import psycopg2
import psycopg2.extensions
dbname = 'trial1'
host = 'localhost'
user = 'postgres'
password = 'postgres123'

DSN = 'dbname=%s host=%s user=%s password=%s' % (dbname, host, user, password)
conn = psycopg2.connect(DSN)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

curs = conn.cursor()
curs.execute("LISTEN test;")

print ("Waiting for notifications on channel 'test'")
while 1:
    if select.select([conn],[],[],5) == ([],[],[]):
        print ("Timeout")
    else:
        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop(0)
            print ("Got NOTIFY:", notify.pid, notify.channel, notify.payload)