from machine import I2C, Pin
from time import sleep
from ads1115 import *
from cal_table import KalibrierTabelle

# ========== ADS1115 Setup ==========
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
ADS1115_ADDRESS = 0x48
adc = ADS1115(ADS1115_ADDRESS, i2c=i2c)

adc.setVoltageRange_mV(ADS1115_RANGE_4096)
adc.setMeasureMode(ADS1115_SINGLE)

# ========== KalibrierTabellen ==========
table_1w = KalibrierTabelle("cal_1w.json")
table_10w = KalibrierTabelle("cal_10w.json")
table_100w = KalibrierTabelle("cal_100w.json")

# ========== Letzte Spannungen pro Kanal ==========
last_voltage_1w = 0.0
last_voltage_10w = 0.0
last_voltage_100w = 0.0

# ========== Messfunktionen ==========
def read_adc_voltage(channel):
    adc.setCompareChannels(channel)
    adc.startSingleMeasurement()
    while adc.isBusy():
        pass
    return adc.getResult_V()

def read_adc_power_1w(return_dbm=False):
    global last_voltage_1w
    v = read_adc_voltage(ADS1115_COMP_0_GND)  # z. B. Kanal A0
    last_voltage_1w = v
    p = table_1w.get_power(v, return_dbm)
    print(f"[1W] {v:.3f} V → {p:.2f} {'dBm' if return_dbm else 'W'}")
    return p

def read_adc_power_10w(return_dbm=False):
    global last_voltage_10w
    v = read_adc_voltage(ADS1115_COMP_1_GND)  # z. B. Kanal A1
    last_voltage_10w = v
    p = table_10w.get_power(v, return_dbm)
    print(f"[10W] {v:.3f} V → {p:.2f} {'dBm' if return_dbm else 'W'}")
    return p

def read_adc_power_100w(return_dbm=False):
    global last_voltage_100w
    v = read_adc_voltage(ADS1115_COMP_2_GND)  # z. B. Kanal A2
    last_voltage_100w = v
    p = table_100w.get_power(v, return_dbm)
    print(f"[100W] {v:.3f} V → {p:.2f} {'dBm' if return_dbm else 'W'}")
    return p

# ========== Punkte speichern ==========
def add_last_point_1w(watt):
    table_1w.add_point(last_voltage_1w, watt)

def add_last_point_10w(watt):
    table_10w.add_point(last_voltage_10w, watt)

def add_last_point_100w(watt):
    table_100w.add_point(last_voltage_100w, watt)

# ========== Tabellen anzeigen ==========
def show_all_tables():
    table_1w.show_table()
    table_10w.show_table()
    table_100w.show_table()

# ========== Hilfe anzeigen ==========
def show_help():
    print("\n🔧 Verfügbare REPL-Befehle:")
    print("📏 Messen:")
    print("  read_adc_power_1w()      → 1W-Kanal messen")
    print("  read_adc_power_10w()     → 10W-Kanal messen")
    print("  read_adc_power_100w()    → 100W-Kanal messen")
    print("  read_adc_power_Xw(True)  → ...mit dBm-Ausgabe")

    print("\n📥 Kalibrierpunkt hinzufügen:")
    print("  add_last_point_1w(watt)     → Letzten gemessenen 1W-Wert speichern")
    print("  add_last_point_10w(watt)    → ...für 10W")
    print("  add_last_point_100w(watt)   → ...für 100W")

    print("\n📋 Kalibriertabelle anzeigen:")
    print("  table_1w.show_table()       → Tabelle 1W anzeigen")
    print("  table_10w.show_table()      → Tabelle 10W anzeigen")
    print("  table_100w.show_table()     → Tabelle 100W anzeigen")
    print("  show_all_tables()           → alle drei Tabellen gleichzeitig")

    print("\n🗑 Kalibrierpunkt löschen:")
    print("  table_1w.delete_point(index)")
    print("  table_10w.delete_point(index)")
    print("  table_100w.delete_point(index)")

    print("\n✏️ Kalibrierpunkt ändern:")
    print("  table_1w.change_point(index, new_voltage, new_power)")
    print("  table_10w.change_point(...) usw.")

    print("\n❓ Hilfe anzeigen:")
    print("  show_help()\n")

# ========== Startanzeige ==========
show_help()
