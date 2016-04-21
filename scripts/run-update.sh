git pull --rebase -p
pip install -r requirements.txt -U
find $PWD -name \*.pyc -delete
python run.py
