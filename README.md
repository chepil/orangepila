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

# =================

How to Make WiFi Access Point mode

# First - make config file for WiFi network orangepila with password lizaalert:

create_ap -m nat wlan0 end0 orangepila lizaalert --no-virt  --mkconfig /etc/create_ap.conf

# Second - make and start ssytem service:

1) make new file

vi /etc/systemd/system/create_ap.service

past next code:

[Unit]
Description=Create AP Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/create_ap --config /etc/create_ap.conf
KillSignal=SIGINT
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target

#

2) then enable and start system service

systemctl enable create_ap

systemctl start create_ap

Now you can connect to the map over wifi network

To access map: http://192.168.12.1

To upload local maps: http://192.168.12.1:8081/upload

