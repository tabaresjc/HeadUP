from hashlib import md5
from app import database, store
from storm.locals import *
import datetime

"""
Prototype of the table users
-- DROP TABLE users;

CREATE TABLE users
(
  id serial NOT NULL,
  email character varying(120) NOT NULL,
  nickname character varying(64),
  role smallint NOT NULL DEFAULT 1,
  last_seen timestamp without time zone,
  created_at timestamp without time zone,
  modified_at timestamp without time zone,
  CONSTRAINT user_id_pk PRIMARY KEY (id )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE users
  OWNER TO postgres;

-- Index: users_email_index

-- DROP INDEX users_email_index;

CREATE INDEX users_email_index
  ON users
  USING btree
  (email COLLATE pg_catalog."default" );
"""
class User(Storm):
    __storm_table__ = "users"
    __storm_primary__ = "id"
    id = Int()
    email = Unicode(default=u'')
    nickname = Unicode(default=u'')
    role = Int()
    last_seen = DateTime(default_factory = lambda: datetime.datetime(1970, 1, 1))
    created_at = DateTime(default_factory = lambda: datetime.datetime(1970, 1, 1))
    modified_at = DateTime(default_factory = lambda: datetime.datetime(1970, 1, 1))
     
 