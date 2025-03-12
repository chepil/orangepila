FROM node:alpine

RUN apk add gcc

RUN apk add --no-cache python3 py3-pip

COPY api.py /app/api.py

RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add --no-cache mariadb-dev

RUN apk add python3-dev mysql-dev pkgconfig

RUN pip3 install mysqlclient --break-system-packages
RUN pip3 install flask --break-system-packages
RUN pip3 install flask_mysqldb --break-system-packages

RUN apk del build-deps
EXPOSE 8081

ENV FLASK_APP /app/api.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 8081

CMD ["flask", "run"]
