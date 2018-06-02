import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from .models import *
from django.db.models import Avg
import eventlet
from eventlet import wsgi
from eventlet import websocket
from eventlet.hubs import trampoline
import codecs

f=codecs.open("templates/home.html", 'r')
mylist = f.read()

dbname = 'trial1'
host = 'localhost'
user = 'postgres'
password = 'postgres123'

dsn = 'dbname=%s host=%s user=%s password=%s' % (dbname, host, user, password)

def func1():
    return Marks.objects.all().aggregate(Avg('english'))['english__avg']

def dblisten(q):
    """
    Open a db connection and add notifications to *q*.
    """
    cnn = psycopg2.connect(dsn)
    cnn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = cnn.cursor()
    cur.execute("LISTEN tester;")
    while 1:
        trampoline(cnn, read=True)
        cnn.poll()
        while cnn.notifies:
            n = cnn.notifies.pop()
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
        eng_avg=Marks.objects.all().aggregate(Avg('english'))['english__avg']
        temp_dict={'eng':46.3}
        print(eng_avg)
        print(n.payload)
        temp=json.dumps(temp_dict)
        ws.send(temp)        #sending message to the browser
        #ws.send(str(eng_avg))
        print("payload sent")

def dispatch(environ, start_response):
    if environ['PATH_INFO'] == '/tester':
        return handle(environ, start_response)
    else:
        start_response('200 OK',
            [('content-type', 'text/html')])
        return [mylist]

def run():
    listener = eventlet.listen(('127.0.0.1', 8000))
    wsgi.server(listener, dispatch)


