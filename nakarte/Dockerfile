FROM node:alpine
WORKDIR /nakarte

RUN apk update 
RUN apk add git

RUN git clone https://github.com/chepil/nakarte.git /nakarte
RUN cd /nakarte
RUN git pull
RUN yarn
RUN cp src/secrets.js.template src/secrets.js

EXPOSE 80
EXPOSE 8080

CMD ["yarn", "start"]

