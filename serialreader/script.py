"""
Dependencies:
- pyserial
"""

import serial
from paho.mqtt import client as mqtt_client
import random
import time
from datetime import datetime
from mysql.connector import connect, Error

# This is the default serial port
SERIAL_PORT = '/dev/ttyACM0'
SPEED = 115200

broker = 'mosquitto'
mqtt_port = 1883
topic = "gpsloc"
client_id = f'serial-{random.randint(0, 1000)}'

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 120
MAX_RECONNECT_DELAY = 60

MYSQL_HOST = "mysql"
MYSQL_DATABASE = "pila"
MYSQL_USER = "pila"
MYSQL_PASSWORD = "pila"
MYSQL_PORT = 3306

# You may need to further configure settings
# See the pyserial documentation for more info
# https://pythonhosted.org/pyserial/pyserial_api.html#classes

#cnx: mysql.connector

def getMysql():
    # Connect to server
    #cnx = mysql.connector.connect(
    cnx = connect(
        host = MYSQL_HOST,
        port = MYSQL_PORT,
        user = MYSQL_USER,
        database = MYSQL_DATABASE,
        password = MYSQL_PASSWORD
    )
    return cnx

ser: serial.Serial

try:
    ser = serial.Serial(port=SERIAL_PORT,
                        baudrate=SPEED,
                        timeout=1)
except Exception as e:
    print(e)
    pass

try:
    cnx = getMysql()
    cur = cnx.cursor()
    cur.execute("create table if not exists `" + MYSQL_DATABASE + "`.`locations` (`date` DATETIME,`id` VARCHAR(7),`type` INT,`lat` FLOAT,`lng` FLOAT);")
#    message = "+GPSLOC:1,2500251,0,1,43.958046,56.282513,5"
#    arr = message.split(",")
#    stationId = arr[1]
#    lat = arr[5]
#    lng = arr[4]
#    statioType = arr[6]
#    now = datetime.now()
#    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
#    #(`date` DATETIME,`id` VARCHAR(7),`type` INT,`lat` FLOAT,`lng` FLOAT)
#    cur.execute("insert into `locations` values ('" + formatted_date + "', " + stationId + ", " + statioType + ", " + lat + ", " + lng + ")")

except Exception as e:
    print(e)
    pass

#cnx = connect(
#    host = MYSQL_HOST,
#    port = MYSQL_PORT,
#    user = MYSQL_USER,
#    password = MYSQL_PASSWORD
#)

def on_disconnect(client, userdata, rc):
    #print("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        #print("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            #print("Reconnected successfully!")
            return
        except Exception as err:
            print("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    print("Reconnect failed after %s attempts. Exiting...", reconnect_count)

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        # For paho-mqtt 2.0.0, you need to add the properties parameter.
        # def on_connect(client, userdata, flags, rc, properties):
        if rc != 0:
            #print("Connected to MQTT Broker!")
            #else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)

    # For paho-mqtt 2.0.0, you need to set callback_api_version.
    # client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)

    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(broker, mqtt_port)
    return client

def publish(client, msg):
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status != 0:
        #print(f"Send `{msg}` to topic `{topic}`")
        #else:
        print(f"Failed to send message to topic {topic}")


client = connect_mqtt()
# Get a cursor
#cur = cnx.cursor()
#cur.execute("create table if not exists `" + MYSQL_DATABASE + "`.`locations` (`date` DATETIME,`id` VARCHAR(7),`type` INT,`lat` FLOAT,`lng` FLOAT);")

while True:
    # Read raw data from the stream
    # Convert the binary string to a normal string
    # Remove the trailing newline character
    is_exception = False
    try:
        if 'ser' in locals():
            message = ser.readline().decode().rstrip()
            if len(message) > 0:
                print(f'{message}')
                client.loop_start()
                publish(client, message)
                client.loop_stop()

                #сохранить в базе данных
                # Execute a query
                arr = message.split(",")
                if (len(arr) > 6):
                    if (arr[0] == '+GPSLOC:1'):
                        stationId = arr[1]
                        lat = arr[5]
                        lng = arr[4]
                        statioType = arr[6]
                        now = datetime.now()
                        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
                        #(`date` DATETIME,`id` VARCHAR(7),`type` INT,`lat` FLOAT,`lng` FLOAT)
                        cur = cnx.cursor()
                        cur.execute("insert into `locations` values ('" + formatted_date + "', " + stationId + ", " + statioType + ", " + lat + ", " + lng + ")")
                        cnx.commit()
        else:
            is_exception = True
    except Exception as e:
        print(e)
        if 'ser' in locals():
            ser.close()
        is_exception = True
        time.sleep(5)  # Задержка на 5 секунд

    if (is_exception == True):
        try:
            ser = serial.Serial(port=SERIAL_PORT,
                                baudrate=SPEED,
                                timeout=1)
            is_exception == False
        except Exception as e:
            print(e)
            if 'ser' in locals():
                ser.close()
            is_exception = True
            time.sleep(5)  # Задержка на 5 секунд
