import network
import time
from umqtt.simple import MQTTClient
from machine import Pin, I2C
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
from time import ticks_us, sleep_us, sleep
import umail

# MQTT configuration
SERVER = "mqtt.favoriot.com"
CLIENT_ID = "umqtt_client"
USER = "iH0JbVmdxP13CDgUm3jzwPtQ7dVT1Jbb"
PASSWORD = "iH0JbVmdxP13CDgUm3jzwPtQ7dVT1Jbb"
WIFI_SSID = 'Nak mintak gue bagi'
WIFI_PASSWORD = '????'
client = MQTTClient(CLIENT_ID, SERVER, user=USER, password=PASSWORD)

# LCD initialization
I2C_ADDR = 0x27
totalRows = 2
totalColumns = 16
i2c = I2C(scl=Pin(22), sda=Pin(23), freq=10000)
lcd = I2cLcd(i2c, I2C_ADDR, totalRows, totalColumns)

# Ultrasonic sensor pins
trig_pin = Pin(13, Pin.OUT)
echo_pin = Pin(12, Pin.IN)

# Your network credentials
ssid = 'Nak mintak gue bagi'
password = '????'

# Email details
sender_email = 'irumankun88@gmail.com'
sender_name = 'ESP32 NI BOSS' #sender name
sender_app_password = '????'
recipient_email ='edragneel678@gmail.com' #  edragneel678@gmail.com

email_subject = 'Water Level Alert'

# Connect to Wi-Fi
def connect_wifi(ssid, password):
    station = network.WLAN(network.STA_IF)
    station.active(True)

    station.connect(ssid, password)
    while not station.isconnected():
        pass
    print('Connection successful')
    print(station.ifconfig())

# Send email
def send_email(inverted_percentage):
    subject = f"Water Level Alert: {inverted_percentage:.0f}%"
    body = (
    f"Current Water Level: {inverted_percentage:.0f}%\n"
    "Please check the tank!!!"
    )
    message = f"Subject: {subject}\n\n{body}"

    smtp = umail.SMTP('smtp.gmail.com', 465, ssl=True)
    smtp.login(sender_email, sender_app_password)
    smtp.to(recipient_email)
    smtp.write(message)
    smtp.send()
    smtp.quit()

# MQTT publish function
def publish_mqtt(inverted_percentage):
    topic = "iH0JbVmdxP13CDgUm3jzwPtQ7dVT1Jbb/v2/streams"
    try:
        client.connect()
        print("Connected to MQTT broker")
    except Exception as e:
        print("MQTT Connection Error:", e)
        return  # Exit the function if there's an error
    
    if inverted_percentage == 90:
        status = "Critical"
        print("Critical")
        print("==============================")
    else:
        status = "Ok"
        print("Ok")
        print("==============================")
        
    payload = '{"device_developer_id": "ESP32@irmansyakir08", "data": {"Water Level": "' + str(inverted_percentage) + '%", "status": "' + status + '"}}'
    client.publish(topic, payload)
    client.disconnect()


# Function to measure distance
def measure_distance():
    trig_pin.off()
    sleep_us(2)
    trig_pin.on()
    sleep_us(10)
    trig_pin.off()

    while not echo_pin.value():
        pass
    pulse_start = ticks_us()

    while echo_pin.value():
        pass
    pulse_end = ticks_us()

    pulse_duration = pulse_end - pulse_start
    distance = (pulse_duration * 0.0343) / 2  # Convert to distance (in cm)
    return distance

# Function to calculate inverted percentage
def calculate_inverted_percentage(distance):
    min_distance = 4  # Minimum distance in cm
    max_distance = 14  # Maximum distance in cm

    if distance <= min_distance:
        return 100
    elif distance >= max_distance:
        return 0
    else:
        return 100 - (((distance - min_distance) / (max_distance - min_distance)) * 100)

# Main loop
email_count = 0
print("==============================")
while True:
    distance = measure_distance()
    inverted_percentage = calculate_inverted_percentage(distance)
    lcd.clear()
    lcd.putstr("Water Level: {:.0f}%".format(inverted_percentage))
    print("Water Level: {:.0f}%".format(inverted_percentage))

    # Publish MQTT data
    publish_mqtt(inverted_percentage)

    # Send email if condition met
    if inverted_percentage >= 90:
        send_email(inverted_percentage)
        email_count += 1
        if email_count == 3:
            break

    sleep(5)

