import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import eventlet
from eventlet import wsgi
from eventlet import websocket
from eventlet.hubs import trampoline

dbname = 'trydb'
host = 'localhost'
user = 'postgres'
password = 'megha123'

dsn = 'dbname=%s host=%s user=%s password=%s' % (dbname, host, user, password)

def dblisten(q):
    """
    Open a db connection and add notifications to *q*.
    """
    cnn = psycopg2.connect(dsn)
    cnn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = cnn.cursor()
    cur.execute("LISTEN data;")
    while 1:
        trampoline(cnn, read=True)
        cnn.poll()
        while cnn.notifies:
            n = cnn.notifies.pop()
            q.put(n)

@websocket.WebSocketWSGI
def handle(ws):
    """
    Receive a connection and send it database notifications.
    """
    q = eventlet.Queue()
    eventlet.spawn(dblisten, q)
    while 1:
        n = q.get()
        print(n)
        ws.send(n.payload)

def dispatch(environ, start_response):
    if environ['PATH_INFO'] == '/data':
        return handle(environ)
    else:
        start_response('200 OK',
            [('content-type', 'text/html')])
        return [page]


def run():
    listener = eventlet.listen(('127.0.0.1', 7000))
    wsgi.server(listener, dispatch)


page = """
<html>
  <head><title>pushdemo</title>
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.1/jquery.min.js"></script>
    <style type="text/css">
      .bar {width: 20px; height: 20px;}
    </style>
    <script>
      window.onload = function() {
        ws = new WebSocket("ws://localhost:7000/data");
        ws.onmessage = function(msg) {
          bar = $('#' + msg.data);
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