FROM python:2.7

ADD inverter /inverter
ADD run.sh /

RUN pip install paho-mqtt anyconfig

CMD [ "/run.sh" ]