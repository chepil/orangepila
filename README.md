# OrangePiLa

##crontab from root
add this line to the root crontab (crontab -e)
* * * * * /root/src/orangepila/healthcheck.sh >> /dev/null 2>&1

#connect usb serial, check that /dev/ttyACM0 exists ( ls -la /dev/ttyACM0 )

#copy this project to /root/src folder

mkdir /root/src

cd /root/src

git clone https://github.com/chepil/orangepila.git

#start containers

cd orangepila

# first time build

docker compose build

# update build

git pull 

docker compose build --no-cache

docker compose up -d --build

check that docker containers run

check log from serial container

docker logs -f serial

connect from any local pc to mqtt broker with orangepi_ip_address:1883

check that serial data duplicates to mqtt brokker

mqtt topic is gpsloc

you can try open nakarte project via browser with http://orangepi_ip_address

that's all

