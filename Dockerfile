FROM python:2.7

ADD inverter /

RUN pip install pystrich

CMD [ "python", "inverter" ]