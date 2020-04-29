FROM python:2.7.17

ENV DEBIAN_FRONTEND noninteractive

RUN addgroup --system celery && \
	adduser --system --no-create-home --group celery

WORKDIR /usr/celery/app
COPY ./requirements.txt /tmp/requirements.txt
COPY ./docker/services/celery/start.sh /var/celery/start.sh

RUN apt-get update \
  && apt-get clean \
  && pip install --no-cache-dir -r /tmp/requirements.txt \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD ["/var/celery/start.sh"]
