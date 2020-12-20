FROM supla/supla-cloud:2.3.25

ENV SERVER_VERSION=v2.3.27
#ENV SERVER_VERSION=master

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        make \
        gcc \
        g++ \
        default-libmysqlclient-dev \
        libssl-dev \
        wget \
        supervisor \
        ca-certificates \
        ssl-cert \
    && apt-get autoremove \
    && rm -r /var/lib/apt/lists/* \
    && mkdir -p /var/log/supervisor

RUN git clone https://github.com/SUPLA/supla-core.git --branch ${SERVER_VERSION} /src \
    && cd /src/supla-scheduler/Release && make all \
    && cd /src/supla-server/Release && make all \
    && cp /src/supla-scheduler/Release/supla-scheduler /src/supla-server/Release/supla-server /usr/local/bin \
    && rm -fr /src \
    && mkdir -p /etc/supla-server

RUN apt-get update && \
    apt-get install -y jq && \
    rm -rf /var/lib/apt/lists

COPY cloud-entrypoint.sh /usr/local/bin/docker-php-entrypoint
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY supla.cfg /etc/supla-server/supla.cfg