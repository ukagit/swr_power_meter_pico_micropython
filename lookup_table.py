from machine import I2C, Pin
from time import sleep
from ads1115 import *
import ujson as json
import math

# ========== OLED (optional) ==========
# i2c = I2C(0, scl=Pin(1), sda=Pin(0))  # falls OLED genutzt wird
# oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# ========== ADS1115 Setup ==========
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
ADS1115_ADDRESS = 0x48
adc = ADS1115(ADS1115_ADDRESS, i2c=i2c)

adc.setVoltageRange_mV(ADS1115_RANGE_4096)     # ±4.096 V
adc.setCompareChannels(ADS1115_COMP_0_GND)     # Kanal A0 gegen GND
adc.setMeasureMode(ADS1115_SINGLE)             # Einzelmessung

V_PER_BIT = 0.000125  # 125 µV pro Bit bei RANGE_4096

# ========== Kalibrierdaten ==========
CAL_FILE = "cal_table.json"
lookup_table = []
last_voltage_read = 0.0  # Für Kalibrierung

# ======= Lade Kalibrierdaten =======

def save_table():
    try:
        with open(CAL_FILE, "w") as f:
            json.dump(lookup_table, f)
        print("Kalibrierwerte gespeichert.")
    except Exception as e:
        print("Fehler beim Speichern:", e)

def init_default_table():
    print("Erstelle neue Kalibriertabelle...")
    default_points = [
        (2.0, 1.0),
        (6.32, 10.0),
        (20.0, 100.0)
    ]
    for v, p in default_points:
        lookup_table.append((v, p))
    lookup_table.sort()
    save_table()

def load_table():
    global lookup_table
    try:
        with open(CAL_FILE, "r") as f:
            lookup_table = json.load(f)
        lookup_table = [tuple(x) for x in lookup_table]
        lookup_table.sort()
        print("Kalibrierwerte geladen.")
    except Exception as e:
        print("Keine Kalibrierdaten gefunden oder Fehler:", e)
        lookup_table = []
        init_default_table()

# ========== Lookup-Logik ==========

def add_point(voltage, power):
    try:
        voltage = float(voltage)
        power = float(power)
        lookup_table.append((voltage, power))
        lookup_table.sort()
        save_table()
        print(f"Punkt hinzugefügt: {voltage:.2f} V → {power:.2f} W")
    except Exception as e:
        print("Ungültige Eingabe:", e)

def show_table():
    print("\nKalibrierpunkte (V → W):")
    if not lookup_table:
        print("Tabelle ist leer.")
        return
    for v, p in lookup_table:
        print(f"{v:>6.2f} V → {p:>6.2f} W")

def get_power(voltage, return_dbm=False):
    if not lookup_table:
        return None
    if voltage <= lookup_table[0][0]:
        power = lookup_table[0][1]
    elif voltage >= lookup_table[-1][0]:
        power = lookup_table[-1][1]
    else:
        for i in range(1, len(lookup_table)):
            v1, p1 = lookup_table[i - 1]
            v2, p2 = lookup_table[i]
            if v1 <= voltage <= v2:
                ratio = (voltage - v1) / (v2 - v1)
                power = p1 + ratio * (p2 - p1)
                break
    if return_dbm:
        if power <= 0:
            return -float('inf')
        return 10 * math.log10(power * 1000)
    return power

# ========== ADC-Messung & Kalibrierhilfe ==========


# Globale letzte Spannung
last_voltage_read = 0.0

def read_adc_voltage(channel=ADS1115_COMP_0_GND):
    """Liest Spannung an ADS1115-Kanal (über Vergleich mit GND)."""
    adc.setCompareChannels(channel)
    adc.startSingleMeasurement()
    while adc.isBusy():
        pass
    voltage = adc.getResult_V()  # Spannung in Volt
    return voltage

def read_adc_power(channel=ADS1115_COMP_0_GND, return_dbm=False):
    """Liest Spannung und interpoliert Leistung."""
    global last_voltage_read
    v = read_adc_voltage(channel)
    last_voltage_read = v
    p = get_power(v, return_dbm=return_dbm)
    print(f"Spannung: {v:.3f} V → Leistung: {p:.2f} {'dBm' if return_dbm else 'W'}")
    return p

def add_last_point(watt):
    """Speichert letzten ADC-Wert mit Ziel-Watt."""
    global last_voltage_read
    try:
        watt = float(watt)
        add_point(last_voltage_read, watt)
    except Exception as e:
        print("Fehler beim Hinzufügen:", e)


def show_help():
    print("\n🔧 Verfügbare Befehle:")
    print("  read_adc_power()         → ADC-Spannung messen + Leistung anzeigen")
    print("  read_adc_voltage()         → ADC-Spannung messen")
    print("  read_adc_power(True)     → ...und zusätzlich dBm anzeigen")
    print("  add_last_point(watt)     → Letzte gemessene Spannung als Kalibrierpunkt speichern")
    print("  add_point(voltage, watt) → Manuell einen Kalibrierwert hinzufügen")
    print("  show_table()             → Alle gespeicherten Kalibrierpunkte anzeigen")
    print("  get_power(voltage)       → Leistung zu gegebener Spannung abrufen")
    print("  get_power(v, True)       → ...auch als dBm")
    print("  show_help()              → Diese Hilfe anzeigen\n")


# ========== Initiale Kalibrierung laden ==========


show_help()
load_table()
