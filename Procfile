web: gunicorn run-heroku:app
init: python db_create.py && pybabel compile -f -d app/translations
upgrade: pybabel compile -f -d app/translations