[![Build Status](https://travis-ci.org/jctt1983/HeadsUp.svg?branch=master)](https://travis-ci.org/jctt1983/HeadsUp)

# HeadUp (Web)

Web Application built with python and Flask Framework to host a super awesome Blogging site.

## Getting Started

### Prerequisites

Install the following software on your PC

- Python 3.X.X & pip3
- [mysqlclient 1.4.6](https://pypi.org/project/mysqlclient/)
	```
	> sudo apt-get install python-dev default-libmysqlclient-dev # Debian / Ubuntu
	> sudo yum install python-devel mysql-devel # Red Hat / CentOS
	> brew install mysql-client # macOS (Homebrew)
	```
- Node.js and NPM

### Installation

1. Clone the repository `$ git clone <path to repository>` and `$ cd` into it
2. Set a virtual environment
```
pip install virtualenv
virtualenv -p /usr/bin/python3.6 venv_headsup_3.6
source venv_headsup/bin/activate
```
3. Run `$ pip3 install -r requirements.txt`
4. Run `$ npm install`
5. Locate the file config.py.txt and save as config.py, and configure its properties
```
SECRET_KEY = "Some random secret string"
```
6. Execute the following NPM task, to compile the JS and CSS bundles development (unminified)
```
npm run build:dev
```
7. Create the `logs` directory
7. Run `python wsgi.py`
8. Open your browser on localhost:5000


### Other NPM task

To compile the JS and CSS bundles and watch the changes in any of the bundles

```
npm run dev:watch
```

To compile the JS and CSS bundles for a production environment

```
npm run build:prd
```
