[![Build Status](https://travis-ci.org/jctt1983/HeadsUp.svg?branch=master)](https://travis-ci.org/jctt1983/HeadsUp)

# HeadUp (Web)

Web Application built with python and Flask Framework to host a super awesome Blogging site.

## Getting Started

### Prerequisites

Install the following software on your PC

- Python 2.7.X
- MySQL & MySQL Python Lib
- Node.js and NPM (It's required by Bower, Grunt)
- Ruby (Required by Compass)
- Git (duh!)

### Installation 

1. Clone the repository `$ git clone <path to repository>` and `$ cd` into it
2. Run `$ pip install -r requeriments.txt`
3. run `$ npm install`
4. run `$ bower install`
5. run `$ grunt --help` to see list of available tasks
6. Locate the file config.py.txt and save as config.py, and configure its properties accordingly
7. run `$ grunt` to setup the development environment or `$ grunt dist` to setup the production environment

### Grunt Tasks
Tasks are configured per package basis on **grunt-tasks** and are defined at the file **grunt-tasks/aliases.js**, here is the list of tasks that are specifically defined for this project.

- `grunt` : Generate the assets files for Development mode (Default). Is a combination of the tasks **frontend-dev** and **backend-dev**.
- `grunt frontend-dev` : Build the assets for the frontend side of the project for Development mode
- `grunt backend-dev` : Build the assets for the backend side of the project for Development mode
- `grunt dist` : Generate the assets files for Production mode. Is a combination of the tasks **frontend-dist** and **backend-dist**.
- `grunt frontend-dist` : Build the assets for the frontend side of the project for Production
- `grunt backend-dist` : Build the assets for the backend side of the project for Production
