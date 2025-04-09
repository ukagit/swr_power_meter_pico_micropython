from machine import Pin, I2C
import ssd1306

import freesans20
import writer
from time import sleep

from ads1115 import *
# SSD1306 initialisieren
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

ADS1115_ADDRESS = 0x48
adc = ADS1115(ADS1115_ADDRESS, i2c=i2c)
adc.setVoltageRange_mV(ADS1115_RANGE_4096)
adc.setCompareChannels(ADS1115_COMP_0_GND)
adc.setMeasureMode(ADS1115_SINGLE)


# Bildschirm löschen und Text anzeigen
oled.fill(0)
oled.text("Power Meter", 0, 0)
oled.text("           ", 0, 8)
oled.text("Watt", 0, 16)
font_writer = writer.Writer(oled, freesans20,False)
font_writer.set_textpos(5,25)
font_writer.printstring("ABC")
oled.show()


def readChannel(channel):
    adc.setCompareChannels(channel)
    adc.startSingleMeasurement()
    while adc.isBusy():
        pass
    voltage = adc.getResult_V()
    return voltage

print("ADS1115 Example Sketch - Single Shot Mode")
print("Channel / Voltage [V]: ")
print(" ")


while True:
    voltage_0 = readChannel(ADS1115_COMP_0_GND)
    print("Channel 0: {:<4.3f}".format(voltage_0))
    #print("{:<4.3f}".format(voltage_0))
    
    voltage_1 = readChannel(ADS1115_COMP_1_GND)
    print("Channel 1: {:<4.3f}".format(voltage_1))
    #print("{:<4.3f}".format(voltage_0),"{:<4.3f}".format(voltage_1))
    
    voltage_2 = readChannel(ADS1115_COMP_2_GND)
    print("Channel 2: {:<4.3f}".format(voltage_2))
    #print("{:<4.3f}".format(voltage_0),"{:<4.3f}".format(voltage_2))
  
    voltage_3 = readChannel(ADS1115_COMP_3_GND)
    print("Channel 3: {:<4.3f}".format(voltage_3))
    #print("{:<4.3f}".format(voltage_0),"{:<4.3f}".format(voltage_3))
    print("---------------")
    font_writer = writer.Writer(oled, freesans20,False)
    font_writer.set_textpos(5,25)
    font_writer.printstring("C 0: {:<4.3f}".format(voltage_0))
    
    oled.show()
    sleep(1)
