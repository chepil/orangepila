# OrangePiLa

##crontab from root
add this line to the root crontab (crontab -e)
* * * * * /root/src/orangepila/healthcheck.sh >> /dev/null 2>&1

#connect usb serial, check that /dev/ttyACM0 exists ( ls -la /dev/ttyACM0 )

#copy this project to /root/src folder

mkdir /root/src

cd /root/src

git clone git@github.com:chepil/orangepila.git

#start containers
cd orangepila

docker compose up -d --build

check that docker containers run

check log from serial container

docker logs -f serial

connect from any local pc to mqtt broker with orangepi_ip_address:1883

check that serial data duplicates to mqtt brokker

mqtt topic is gpsloc

that's all

