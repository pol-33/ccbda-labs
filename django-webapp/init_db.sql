CREATE DATABASE ccbdadb;
CREATE USER ccbdauser
    WITH ENCRYPTED PASSWORD 'ccbdapassword'
    createdb
    createrole
    bypassrls;
ALTER USER ccbdauser SET TimeZone = utc;
ALTER DATABASE ccbdadb OWNER TO ccbdauser;