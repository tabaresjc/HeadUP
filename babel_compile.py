import os
import sys
pybabel = 'venv/bin/pybabel'
os.system(pybabel + ' compile -f -d app/translations')

