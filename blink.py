from machine import Pin
from time import sleep

led1 = Pin(25, Pin.OUT)

# loop forever
while True:
    led1.toggle()
    sleep(0.1)