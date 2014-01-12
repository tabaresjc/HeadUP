import sys
from app.db_init import DbInit


if len(sys.argv) == 2 and sys.argv[1] == 'cp':
    DbInit.create_posts()
if len(sys.argv) == 2 and sys.argv[1] == 'rm':
    DbInit.remove_table_categories()
if len(sys.argv) == 2 and sys.argv[1] == 'ne':
    DbInit.normalize_posts_url()
else:
    DbInit.create_db()
