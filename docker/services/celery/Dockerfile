FROM python:2.7.18-alpine

WORKDIR /usr/celery/app
COPY ./requirements.txt /tmp/requirements.txt
COPY ./docker/services/celery/start.sh /var/celery/start.sh

RUN apk update \
	&& apk --no-cache --update add build-base libffi-dev python-dev py-pip jpeg-dev zlib-dev musl-dev openssl-dev bash \
	&& pip install --no-cache-dir -r /tmp/requirements.txt \
  	&& apk del build-base libffi-dev python-dev py-pip zlib-dev musl-dev openssl-dev

RUN addgroup -S celery
RUN adduser -S -H -G celery celery

CMD ["/var/celery/start.sh"]
