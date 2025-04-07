# OrangePiLa Project

## 1) Setup Wifi Access Point
### 1.1. make config file for WiFi
set wifi network with name "orangepila" with password "lizaalert":
```
create_ap -m nat wlan0 end0 orangepila lizaalert --no-virt  --mkconfig /etc/create_ap.conf
```
### 1.2. make and start system service:
make and edit new file:
```
vi /etc/systemd/system/create_ap.service
```
past next code into new file and save it:
```
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
```
### 1.3. then enable and start system service
```
systemctl enable create_ap
systemctl start create_ap
```
Now you can connect to the orange pi over wifi network "orangepila" with password "lizaalert"

## 2) Connect Radio with usb port
check that /dev/ttyACM0 exists
```
ls -la /dev/ttyACM0
```

## 3) Copy project to /root/src folder
```
mkdir /root/src
cd /root/src
git clone https://github.com/chepil/orangepila.git
```

### _Prepare project for start containers:_
```
cd /root/src/orangepila
```

### first time build
```
docker compose build
docker compose up -d
```
### or update build
```
git pull 
docker compose build --no-cache
docker compose up -d --build
```

### check that docker containers run
check log from serial container:
```
docker logs -f serial
```
test mqtt broker:
connect from any local pc to mqtt broker with 192.168.12.1:1883

check that serial data duplicates to mqtt brokker
mqtt topic is gpsloc
you can try to open "nakarte project" via browser with
- [http://192.168.12.1](http://192.168.12.1)

## 4) Edit crontab file from root _(*optional)_
add this line to the root crontab, start from console:
```
crontab -e
```
add this line to you root crontab file:
```
* * * * * /root/src/orangepila/healthcheck.sh >> /dev/null 2>&1
```

## 5) Test Nakarte Project

To access map: http://192.168.12.1
To upload local maps: http://192.168.12.1:8081/upload

Questions ?
telegram: [@denchepil](https://t.me/denchepil)
