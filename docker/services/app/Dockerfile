FROM python:2.7.17

ENV DEBIAN_FRONTEND noninteractive

WORKDIR /usr/headup/app
COPY ./requirements.txt /tmp/requirements.txt
COPY ./docker/services/app/start.sh /var/headup/start.sh

RUN apt-get update \
	&& apt-get clean \
	&& pip install --no-cache-dir -r /tmp/requirements.txt \
	&& pip install gevent==1.4.0 \
	&& pip install gevent-websocket==0.10.1 \
	&& pip install greenlet==0.4.15 \
  	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD ["/var/headup/start.sh"]
