#!/usr/bin/env bash

PICTURE_PATH=${APP_DATA_PATH}/media/pictures
LOGS_PATH=${APP_DATA_PATH}/logs

mkdir -p ${PICTURE_PATH}
mkdir -p ${LOGS_PATH}

python run.py
