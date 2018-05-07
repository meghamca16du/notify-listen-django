import select
import psycopg2
import psycopg2.extensions
def create_trigger():
    sql = """

    CREATE FUNCTION notify_trigger() RETURNS trigger AS $$

    DECLARE

    BEGIN
    -- TG_TABLE_NAME is the name of the table who's trigger called this function
    -- TG_OP is the operation that triggered this function: INSERT, UPDATE or DELETE.
    execute 'NOTIFY ' || TG_TABLE_NAME || '_' || TG_OP;
    PERFORM pg_notify('test','high');
    return new;
    END;

    $$ LANGUAGE plpgsql;

    CREATE TRIGGER students_triggers BEFORE insert or update or delete on students execute procedure notify_trigger();
    CREATE TRIGGER marks_triggers BEFORE insert or update or delete on try_app1_marks execute procedure notify_trigger();
    """
    
def mainfunc():
    dbname = 'trial1'
    host = 'localhost'
    user = 'postgres'
    password = 'postgres123'

    DSN = 'dbname=%s host=%s user=%s password=%s' % (dbname, host, user, password)
    conn = psycopg2.connect(DSN)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    curs = conn.cursor()
    #curs.execute(sql)
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