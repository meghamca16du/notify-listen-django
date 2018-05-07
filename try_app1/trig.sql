
CREATE LANGUAGE plpgsql;

CREATE FUNCTION notify_trigger() RETURNS trigger AS $$

DECLARE

BEGIN
 -- TG_TABLE_NAME is the name of the table who's trigger called this function
 -- TG_OP is the operation that triggered this function: INSERT, UPDATE or DELETE.
 execute 'NOTIFY ' || TG_TABLE_NAME || '_' || TG_OP;
 PERFORM pg_notify('chan1','hello');
 return new;
END;

$$ LANGUAGE plpgsql;

CREATE TRIGGER students_trigger BEFORE insert or update or delete on students execute procedure notify_trigger();
CREATE TRIGGER marks_trigger BEFORE insert or update or delete on marks execute procedure notify_trigger();