#!/usr/bin/env bash

LOG_FILE_NAME=${APP_DATA_PATH}/logs/celery.log

mkdir -p ${APP_DATA_PATH}/logs/

chown -R :celery ${APP_BASE_PATH}
chown -R :celery ${APP_DATA_PATH}

celery --app=app.mq worker \
	--loglevel=DEBUG --logfile=${LOG_FILE_NAME} \
	--uid=celery --gid=celery
