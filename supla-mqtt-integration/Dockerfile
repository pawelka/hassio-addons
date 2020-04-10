FROM pawel5870/supla-mqtt-client:latest

RUN apt-get update && \
    apt-get install -y jq && \
    rm -rf /var/lib/apt/lists

ADD run.sh /

CMD [ "/run.sh" ]
