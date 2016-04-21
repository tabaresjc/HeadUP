import os
import sys
pybabel = 'pybabel'
os.system(pybabel + ' extract -F scripts/babel/babel.cfg -k lazy_gettext -o scripts/babel/messages.pot app')
os.system(pybabel + ' update -i scripts/babel/messages.pot -d app/translations')
# os.unlink('messages.pot')
