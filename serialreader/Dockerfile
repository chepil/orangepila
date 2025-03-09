FROM python:3.11-slim

COPY script.py /app/script.py

RUN pip3 install pyserial
RUN pip3 install paho-mqtt
RUN pip3 install mysql-connector-python

CMD ["python3", "-u", "/app/script.py"]
