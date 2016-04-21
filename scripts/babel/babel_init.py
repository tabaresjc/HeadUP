import os
import sys
pybabel = 'pybabel'
if len(sys.argv) != 2:
    print "usage: tr_init <language-code>"
    sys.exit(1)
os.system(pybabel + ' extract -F scripts/babel/babel.cfg -k lazy_gettext -o scripts/babel/messages.pot app')
os.system(pybabel + ' init -i scripts/babel/messages.pot -d app/translations -l ' + sys.argv[1])
# os.unlink('messages.pot')
