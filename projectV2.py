from machine import Pin, I2C
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
from time import ticks_us, sleep_us, sleep
import umail
import network

# Initialize I2C for the LCD
I2C_ADDR = 0x27
totalRows = 2
totalColumns = 16
i2c = I2C(scl=Pin(22), sda=Pin(23), freq=10000)  # Replace with your I2C pins and frequency
lcd = I2cLcd(i2c, I2C_ADDR, totalRows, totalColumns)

# Define GPIO pins connected to the ultrasonic sensor
trig_pin = Pin(13, Pin.OUT)
echo_pin = Pin(12, Pin.IN)

# Your network credentials
ssid = 'Nak mintak gue bagi'
password = 'ManHohoho123!!!'

# Email details
sender_email = 'irumankun88@gmail.com'
sender_name = 'ESP32 NI BOSS' #sender name
sender_app_password = 'yzln lmsd lzqg mflx'
recipient_email ='edragneel678@gmail.com' #nusyrfnsyah@gmail.com

email_subject = 'Water Level Alert'

def connect_wifi(ssid, password):
    # Connect to your network
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(ssid, password)
    while not station.isconnected():
        pass
    print('Connection successful')
    print(station.ifconfig())

def send_email(distance):
    smtp = umail.SMTP('smtp.gmail.com', 465, ssl=True)  # Gmail's SSL port
    smtp.login(sender_email, sender_app_password)
    smtp.to(recipient_email)
    smtp.write("From:" + sender_name + "<" + sender_email + ">\n")
    smtp.write("Subject:" + email_subject + "\n")
    smtp.write("HI, Distance: {} cm\n".format(distance))  # Corrected line
    smtp.send()
    smtp.quit()

# Connect to your network
connect_wifi(ssid, password)

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
while True:
    distance = measure_distance()
    inverted_percentage = calculate_inverted_percentage(distance)
    lcd.clear()
    lcd.putstr("Water Level: {:.0f}%".format(inverted_percentage))
    print("Water Level: {:.0f}%".format(inverted_percentage))

    if inverted_percentage >= 90:
        send_email(distance)
        email_count += 1
        if email_count == 3:
          break


    sleep(4)

