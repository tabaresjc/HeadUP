[![Build Status](https://travis-ci.org/jctt1983/HeadsUp.svg?branch=master)](https://travis-ci.org/jctt1983/HeadsUp)

# HeadUp (Web)

Web Application built with python and Flask Framework to host a super awesome Blogging site.

## Getting Started

### Prerequisites

Install the following software on your PC

- Python 2.7.X & pip
- MySQL & MySQL Python Lib
	```
	> sudo apt-get install python-dev libmysqlclient-dev
	```
- Node.js and NPM (It's required by Bower, Grunt)
- Ruby (Required by Compass)
- Git (duh!)

### Installation 

1. Clone the repository `$ git clone <path to repository>` and `$ cd` into it
2. Set a virtual environment
```
pip install virtualenv`
virtualenv -p /usr/bin/python2.7 venv_headsup
source venv_headsup/bin/activate
```
3. Run `$ pip install -r requeriments.txt`
4. Run `$ npm install`
5. Run `$ bower install`
6. Run `$ grunt --help` to see list of available tasks
7. Locate the file config.py.txt and save as config.py, and configure its properties accordingly
8. Run `$ grunt` to setup the development environment or `$ grunt dist` to setup the production environment

### NPM Tasks
+ `npm run build:dev`: build development environment
+ `npm run build:prd`: build production environment
+ `npm run dev:watch`: watch changes in the assets files (js, css, html)
