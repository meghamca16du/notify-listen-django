import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import eventlet
from eventlet import wsgi
from eventlet import websocket
from eventlet.hubs import trampoline


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
    cnn = psycopg2.connect(dsn)
    cnn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = cnn.cursor()
    cur.execute("LISTEN test;")
    while 1:
        print('inside whilee \n')
        trampoline(cnn, read=True)
        print('3 \n')
        cnn.poll()
        print('4 \n')
        while cnn.notifies:
            print('inside cnn.notifies  ','cnn.notifies',' \n')
            n = cnn.notifies.pop()
            print('n   ',n,'   done\n')
            q.put(n)

@websocket.WebSocketWSGI
def handle(ws):
    """
    Receive a connection and send it database notifications.
    """
    q = eventlet.Queue()
    print('1 \n')
    eventlet.spawn(dblisten, q)
    print('2 \n')
    while 1:
        n = q.get()
        print(n)
        #ws.send(n.payload)

def dispatch(environ, start_response):
    if environ['PATH_INFO'] == '/test':
        print("3")
        return handle(environ, start_response)
    else:
        start_response('200 OK',
            [('content-type', 'text/html')])
        #return [templating.load_page('content': 'The Content Of Page One',"eventlet1.html"),]
        return ['home.html']


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