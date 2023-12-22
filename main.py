from imu import MPU6050
from time import sleep
from machine import Pin, I2C


i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
imu = MPU6050(i2c)
buzzer = machine.Pin(15, machine.Pin.OUT)

while True:
    ax=round(imu.accel.x,2)
    ay=round(imu.accel.y,2)
    az=round(imu.accel.z,2)
    gx=round(imu.gyro.x)
    gy=round(imu.gyro.y)
    gz=round(imu.gyro.z)
    tem=round(imu.temperature,2)
    
    if (az > 1 or az < -1) and (gy >30 or gy < -30):
        buzzer.value(1)
    else:
        buzzer.value(0)
    
    print("ax:",ax,", ","ay:",ay,", ","az:",az,", ","gx:",gx,", ","gy:",gy,", ","gz:",gz,", ","Temperature:",tem,", ",end="\r")
    sleep(0.2)
