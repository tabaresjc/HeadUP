import sys
from app.db_init import DbInit

DbInit.create_db()

if len(sys.argv) == 2 and sys.argv[1] == 'cp':
    DbInit.create_posts()
if len(sys.argv) == 2 and sys.argv[1] == 'rm':
    DbInit.remove_table_categories()
