from sqlalchemy import event
from sqlalchemy.pool import Pool
import app

@event.listens_for(Pool, 'connect')
def set_unicode(dbapi_conn, conn_record):
    cursor = dbapi_conn.cursor()
    try:
        cursor.execute("SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci'")
    except Exception as e:
        app.logger.debug(e)
