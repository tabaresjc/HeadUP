[![Build Status](https://travis-ci.org/jctt1983/HeadsUp.svg?branch=master)](https://travis-ci.org/jctt1983/HeadsUp)

# HeadUp (Web)

Web Application built with python and Flask Framework to host a super awesome Blogging site.

## Setup development environment

### Prerequisites

Install the following software on your PC

- Docker CE (19.03.8)
- Node.js and NPM

### Setup Environment
1. Take `.env.txt` as a reference, and create a file name `.env`, make sure to  create and fill in the following folders. Everything else can be seasoned to taste :)

```
# Specify path to the source code of project
APP_BASE_PATH=/path/to/app/source

# Specify path to data folder (will contain Media, Pictures, logs)
APP_DATA_PATH=/path/to/app/data

# Specify path to the source code of project
CELERY_BASE_PATH=/path/to/app/source

# Specify path to data folder for celery (contain logs)
CELERY_DATA_PATH=/path/to/celery/data
```

2. Take `config.py.txt` as a reference, and create a file named `config.py`. The config fiels are divided into sections.

The following sections might depend on one of docker environment variables
- Folders
- Media
- Logger
- Session Configuration
- Cache Configuration
- SQLAlchemy Configuration
- Rabbit MQ Service

The following sections are not dependent on docker envrionment.
- CSRF
- Site Configuration
- Flask Configuration
- Facebook Pixel ID
- Addthis
- Domain Replacement
- Mail Function
- Google Analytics
- Google tag managerS
- Patreon ID
- HubSpot ID
- Mailchimp

### Getting started

1. Clone the repository `$ git clone <path to repository>` and `$ cd` into it
2. Execute the following docker commands
```bash
# build docker images of the project
$ docker-compose build
# boot up the containers
$ docker-compose up -d
```
3. Once the containers are up and running, check that all containers are up and running.
```bash
# check status
$ docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Status}}"
# should roughly look like this
CONTAINER ID        NAMES               STATUS
cfa8d8e22d0d        headup_web_server   Up 17 minutes
48d3dca91765        headup_celery       Up 17 minutes
7a77b9aa4b7f        headup_app          Up 17 minutes
0616ae70023e        headup_rabbitmq     Up 17 minutes
14edaee93f97        headup_mysql        Up 17 minutes
```

### Provision first admin account

The first run will create an empty database so we need to run the database migration and create an admin user to access the admin site.

```bash
# run schema migrations with headup_app container
$ docker exec -it headup_app python command.py migration upgrade

# init the database with some dummy data
$ docker exec -it headup_app python command.py start db-init

# create admin user
$ docker exec -it headup_app python command.py start init-user --nickname {NAME} --email {EMAIL} --password {PASSWORD}
```

### Build templates

Note: In this step we don't require to execute the below steps within the containers, we can run the following commands in the host machine.

To compile the JS and CSS bundles and watch the changes in any of the bundles

```bash
$ npm run dev:watch
```

To compile the JS and CSS bundles for a production environment

```bash
$ npm run build:prd
```


### Launch website

The project exposes a website in port 80, so you can simply access the website

```
http://localhost
```