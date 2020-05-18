FROM python:2.7.18-alpine

WORKDIR /usr/headup/app
COPY ./requirements.txt /tmp/requirements.txt
COPY ./docker/services/app/start.sh /var/headup/start.sh

RUN apk update \
	&& apk --no-cache --update add build-base libffi-dev python-dev py-pip jpeg-dev zlib-dev musl-dev openssl-dev bash \
	&& pip install --no-cache-dir -r /tmp/requirements.txt \
	&& pip install --no-cache-dir gevent==1.4.0  gevent-websocket==0.10.1 greenlet==0.4.15 \
  	&& apk del build-base libffi-dev python-dev py-pip zlib-dev musl-dev openssl-dev

CMD ["/var/headup/start.sh"]
