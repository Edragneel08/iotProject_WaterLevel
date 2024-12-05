from machine import Pin, I2C
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
from time import sleep_us, ticks_us, sleep

# Initialize I2C for the LCD
I2C_ADDR = 0x27
totalRows = 2
totalColumns = 16
i2c = I2C(scl=Pin(22), sda=Pin(23), freq=10000)  # initializing the I2C method for ESP32
lcd = I2cLcd(i2c, I2C_ADDR, totalRows, totalColumns)

# Define GPIO pins connected to the ultrasonic sensor
trig_pin = Pin(13, Pin.OUT)
echo_pin = Pin(12, Pin.IN)

# Define the minimum and maximum distances for the percentage calculation
min_distance = 5  # Minimum distance in cm
max_distance = 50  # Maximum distance in cm

# Function to calculate percentage
def calculate_percentage(distance):
    if distance <= min_distance:
        return 0
    elif distance >= max_distance:
        return 100
    else:
        return ((distance - min_distance) / (max_distance - min_distance)) * 100

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

# Main loop
while True:
    distance = measure_distance()
    percentage = calculate_percentage(distance)
    lcd.clear()
    lcd.putstr("Distance: {:.2f}%".format(percentage))
    print("Distance: {:.2f}%".format(percentage))
    sleep(2)


