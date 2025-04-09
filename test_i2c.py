from machine import Pin, I2C
import time

# I2C auf GP0 (SDA) und GP1 (SCL)
i2c = I2C(0, scl=Pin(1), sda=Pin(0))

# Kurze Pause
time.sleep(1)

# Geräte scannen
print("Scanne nach I2C-Geräten...")
devices = i2c.scan()

if devices:
    print("Gefundene I2C-Geräte:")
    for device in devices:
        print(" - Adresse:", hex(device))
else:
    print("Keine I2C-Geräte gefunden.")
