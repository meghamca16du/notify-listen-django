import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import eventlet
from eventlet import wsgi
from eventlet import websocket
from eventlet.hubs import trampoline
from .models import *
from django.db.models import Avg

dbname = 'trial1'
host = 'localhost'
user = 'postgres'
password = 'postgres123'
dsn = 'dbname=%s host=%s user=%s password=%s' % (dbname, host, user, password)

def create_trigger():
    sql = """


        CREATE FUNCTION notify_trigger() RETURNS trigger AS $$

        DECLARE

        BEGIN
        -- TG_TABLE_NAME is the name of the table who's trigger called this function
        -- TG_OP is the operation that triggered this function: INSERT, UPDATE or DELETE.
        execute 'NOTIFY ' || TG_TABLE_NAME || '_' || TG_OP;
        PERFORM pg_notify('test','hello');
        return new;
        END;

        $$ LANGUAGE plpgsql;

        CREATE TRIGGER students_trigger BEFORE insert or update or delete on students execute procedure notify_trigger();
        CREATE TRIGGER marks_trigger BEFORE insert or update or delete on tryapp_marks execute procedure notify_trigger();

        """ 

    conn = psycopg2.connect(dsn)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    curs = conn.cursor()
    curs.execute(sql)

def dblisten(q):
    """
    Open a db connection and add notifications to *q*.
    """
    #print()
    cnn = psycopg2.connect(dsn)
    cnn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = cnn.cursor()
    cur.execute("LISTEN test;")
    while 1:
        print('in trampoline')
        trampoline(cnn, read=True)          
        '''Suspend the current coroutine until the given socket object or
        file descriptor is ready to read, ready to write, or the 
        specified timeout elapses, depending on arguments specified.'''
        print('before poll')
        cnn.poll()
        print('after poll')
        while cnn.notifies:
            n = cnn.notifies.pop()
            print('notifications')
            q.put(n)

@websocket.WebSocketWSGI     #creating a websocket in wsgi application
def handle(ws):
    """
    Receive a connection and send it database notifications.
    """
    print("4")
    q = eventlet.Queue()
    eventlet.spawn(dblisten, q)   #creating a greenthread
    
    while 1:
        n = q.get()
        print('5')
        print(n)
        eng_avg = Marks.objects.all().aggregate(Avg('english'))['english__avg']
        print(eng_avg)
        print(n.payload)
        ws.send(n.payload)        #sending message to the browser

def dispatch(environ, start_response):
    if environ['PATH_INFO'] == '/tester':
        print("3")
        return handle(environ, start_response)
    else:
        start_response('200 OK',
            [('content-type', 'text/html')])
        #return [templating.load_page('content': 'The Content Of Page One',"eventlet1.html"),]
        return [page]


def run():
    listener = eventlet.listen(('127.0.0.1', 8080))      # returns - The listening green socket object.
    print("1") 
    wsgi.server(listener, dispatch)                      # launches wsgi server which runs in a loop untill server exits
    print("2")


page = """
<html>
  <head><title>pushdemo</title>
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.1/jquery.min.js"></script>
    <style type="text/css">
      .bar {width: 20px; height: 20px;}
    </style>
    <script>
      window.onload = function() {
        ws = new WebSocket("ws://localhost:8080/test");
        ws.onmessage = function(msg) {
          bar = $('#' + msg.test);
          bar.width(bar.width() + 10);
        }
      }
    </script>
  </head>
  <body>
    <div style="width: 400px;">
      <div id="red" class="bar"
          style="background-color: red;">&nbsp;</div>
      <div id="green" class="bar"
          style="background-color: green;">&nbsp;</div>
      <div id="blue" class="bar"
          style="background-color: blue;">&nbsp;</div>
    </div>
  </body>
</html>
"""