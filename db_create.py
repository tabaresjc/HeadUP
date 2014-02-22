import sys
from app.db_init import DbInit

lenargs = len(sys.argv) 
if  2 == lenargs and sys.argv[1] == 'init':
    DbInit.init_db()
    DbInit.init_categories()
elif 2 == lenargs and sys.argv[1] == 'create-posts'
    DbInit.create_posts()