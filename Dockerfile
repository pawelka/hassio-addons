FROM python:2.7

ADD inverter /inverter

RUN pip install paho-mqtt

CMD [ "python", "./inverter" ]