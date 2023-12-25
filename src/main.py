from machine import Pin, I2C
import network
import BlynkLib
import utime
import math
from mpu6050 import init_mpu6050, get_mpu6050_data

i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=400000)
init_mpu6050(i2c)
buzzer = machine.Pin(15, machine.Pin.OUT)

# WiFi credentials
WIFI_SSID = "jiofib2.4"
WIFI_PASSWORD = "7382640067"
 
# Blynk authentication token
BLYNK_AUTH = "kbKxwNQOhOZTRhze-ONjWMGsuBqOhM_R"
 
 
# Connect to WiFi network
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASSWORD)
 
# Wait for the connection to be established
while not wifi.isconnected():
    sleep(1)
 
# Initialize Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH)
 
def calculate_tilt_angles(accel_data):
    x, y, z = accel_data['x'], accel_data['y'], accel_data['z']
 
    tilt_x = math.atan2(y, math.sqrt(x * x + z * z)) * 180 / math.pi
    tilt_y = math.atan2(-x, math.sqrt(y * y + z * z)) * 180 / math.pi
    tilt_z = math.atan2(z, math.sqrt(x * x + y * y)) * 180 / math.pi
 
    return tilt_x, tilt_y, tilt_z
 
def complementary_filter(pitch, roll, gyro_data, dt, alpha=0.98):
    pitch += gyro_data['x'] * dt
    roll -= gyro_data['y'] * dt
 
    pitch = alpha * pitch + (1 - alpha) * math.atan2(gyro_data['y'], math.sqrt(gyro_data['x'] * gyro_data['x'] + gyro_data['z'] * gyro_data['z'])) * 180 / math.pi
    roll = alpha * roll + (1 - alpha) * math.atan2(-gyro_data['x'], math.sqrt(gyro_data['y'] * gyro_data['y'] + gyro_data['z'] * gyro_data['z'])) * 180 / math.pi
 
    return pitch, roll
 
pitch = 0
roll = 0
prev_time = utime.ticks_ms()
 
while True:
    data = get_mpu6050_data(i2c)
    curr_time = utime.ticks_ms()
    dt = (curr_time - prev_time) / 1000
 
    tilt_x, tilt_y, tilt_z = calculate_tilt_angles(data['accel'])
    pitch, roll = complementary_filter(pitch, roll, data['gyro'], dt)
    
    if (tilt_y > 15 or tilt_y < -15) and (data['accel']['y'] > 0.05 or data['accel']['y'] < -0.05):
        buzzer.value(1)
    else:
        buzzer.value(0)
    prev_time = curr_time
 
    print("Temperature: {:.2f} °C".format(data['temp']))
    print("Tilt angles: X: {:.2f}, Y: {:.2f}, Z: {:.2f} degrees".format(tilt_x, tilt_y, tilt_z))
    print("Pitch: {:.2f}, Roll: {:.2f} degrees".format(pitch, roll))
    print("Acceleration: X: {:.2f}, Y: {:.2f}, Z: {:.2f} g".format(data['accel']['x'], data['accel']['y'], data['accel']['z']))
    print("Gyroscope: X: {:.2f}, Y: {:.2f}, Z: {:.2f} °/s".format(data['gyro']['x'], data['gyro']['y'], data['gyro']['z']))
    
    # Send sensor data to Blynk
    blynk.virtual_write(0, (data['accel']['y']))     # virtual pin for acceleration
    blynk.virtual_write(3, tilt_x)   # virtual pin for Tilt angles X-axis
    blynk.virtual_write(4, tilt_y)   # virtual pin for Tilt angles Y-axis
    blynk.virtual_write(1, tilt_z)   # virtual pin for Tilt angles Z-axis
    blynk.run()

    utime.sleep(1)