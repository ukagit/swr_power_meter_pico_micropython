from machine import Pin, I2C
import ssd1306
import freesans20
import writer
from time import sleep
from ads1115 import *
import ujson as json
import math
import time


# ==== OLED Setup ====
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# ==== ADS1115 Setup ====
ADS1115_ADDRESS = 0x48
adc = ADS1115(ADS1115_ADDRESS, i2c=i2c)
adc.setVoltageRange_mV(ADS1115_RANGE_4096)
adc.setMeasureMode(ADS1115_SINGLE)

# Globale Variablen
peak_value = 0
peak_time = 0

# ==== Kalibriertabelle-Klasse (nur für 1W in diesem Fall) ====
class CalTable:
    def __init__(self, name, filename):
        self.name = name
        self.filename = filename
        self.table = []
        self.last_voltage = 0.0
        self.load_table()

    def save_table(self):
        with open(self.filename, "w") as f:
            json.dump(self.table, f)

    def init_default_table(self, default_points):
        self.table = default_points
        self.table.sort()
        self.save_table()

    def load_table(self):
        try:
            with open(self.filename, "r") as f:
                self.table = json.load(f)
            self.table = [tuple(x) for x in self.table]
            self.table.sort()
        except:
            self.init_default_table([
                (2.0, 1.0),
                (6.32, 10.0),
                (20.0, 100.0)
            ])

    def get_power(self, voltage, return_dbm=False):
        if not self.table:
            return None
        if voltage <= self.table[0][0]:
            power = self.table[0][1]
        elif voltage >= self.table[-1][0]:
            power = self.table[-1][1]
        else:
            for i in range(1, len(self.table)):
                v1, p1 = self.table[i - 1]
                v2, p2 = self.table[i]
                if v1 <= voltage <= v2:
                    ratio = (voltage - v1) / (v2 - v1)
                    power = p1 + ratio * (p2 - p1)
                    break
        if return_dbm:
            if power <= 0:
                return -float('inf')
            return 10 * math.log10(power * 1000)
        return power

# ==== 1W-Kalibrierung laden ====
cal_1w = CalTable("1W-Bereich", "cal_1w.json")

# ==== readChannel() für A0 ====
def readChannel(channel):
    adc.setCompareChannels(channel)
    adc.startSingleMeasurement()
    while adc.isBusy():
        pass
    voltage = adc.getResult_V()
    return voltage

def test_cal_1w_linear_steps():
    print("\nTest: cal_1w.get_power(v) bei 0–3 V (20 Schritte)")
    print("Spannung (V)   →   Leistung (W)")
    print("-" * 30)
    steps = 20
    for i in range(steps + 1):
        voltage = 3.0 * i / steps
        power = cal_1w.get_power(voltage)
        print("{:2.4f} V       →   {:7.5f} W".format(voltage, power))
def bars(x, max_value, x0=0, y0=50, width=128, height=10):
    """
    Zeichnet einen Balken (horizontal) auf dem OLED.
    - x         : aktueller Wert
    - max_value : Maximalwert
    - x0, y0    : Startposition (links oben)
    - width     : Max. Breite des Balkens (Pixel)
    - height    : Höhe des Balkens (Pixel)
    """
    # Verhältnis berechnen
    ratio = min(max(x / max_value, 0), 1)  # clamp 0–1
    bar_length = int(width * ratio)

    # Balkenhintergrund löschen
    oled.fill_rect(x0, y0, width, height, 0)
    # Balken zeichnen
    oled.fill_rect(x0, y0, bar_length, height, 1)


def track_peak(x, hold_time=1.5):
    """
    Gibt den aktuellen x-Wert zurück + den gehaltenen Maximalwert.
    Hält den Peak für 'hold_time' Sekunden.
    """
    global peak_value, peak_time

    now = time.ticks_ms()

    if x > peak_value:
        peak_value = x
        peak_time = now

    # Prüfen ob Peak-Haltezeit abgelaufen ist
    if time.ticks_diff(now, peak_time) > (hold_time * 1000):
        peak_value = x  # zurücksetzen auf aktuellen Wert

    return peak_value

def bars_with_peak(x, peak, max_value, x0=0, y0=50, width=128, height=10):
    x_ratio = min(max(x / max_value, 0), 1)
    peak_ratio = min(max(peak / max_value, 0), 1)

    bar_len = int(width * x_ratio)
    peak_x = int(width * peak_ratio)

    oled.fill_rect(x0, y0, width, height, 0)
    oled.fill_rect(x0, y0, bar_len, height, 1)

    if peak_x >= 1:
        oled.fill_rect(x0 + peak_x - 1, y0, 4
                       , height, 2)
def autorange_read(channel=ADS1115_COMP_0_GND):
    """
    Liest eine Spannung vom angegebenen Kanal und passt Gain automatisch an.
    Nutzt vorhandene 'setAutoRange()'-Funktion aus der Bibliothek.
    """
    # Kanal setzen & Messung starten
    adc.setCompareChannels(channel)
    adc.startSingleMeasurement()
    while adc.isBusy():
        pass

    # Rohwert checken
    raw = adc.getRawResult()

    # Auto-Gain aktivieren, wenn Signal zu klein/groß
    if abs(raw) > 26000 or abs(raw) < 3000:
        adc.setAutoRange()

    # Nach Gain-Wechsel neu messen
    adc.setCompareChannels(channel)
    adc.startSingleMeasurement()
    while adc.isBusy():
        pass

    voltage = adc.getResult_V()
    return voltage

def print_gain_ranges(teiler_faktor=34):
    print("Gain        | Max ADC V | Max Input V (geteilt) | Max Eingang")
    print("-" * 60)
    gain_ranges = [
        ("±0.256 V", 0.256),
        ("±0.512 V", 0.512),
        ("±1.024 V", 1.024),
        ("±2.048 V", 2.048),
        ("±4.096 V", 3.3),    # begrenzt durch VDD = 3.3V
        ("±6.144 V", 3.3)     # begrenzt durch VDD = 3.3V
    ]
    for label, v_adc in gain_ranges:
        v_in = v_adc * teiler_faktor
        print(f"{label:<10} | {v_adc:>8.3f} V | {v_adc:>8.3f} V         | {v_in:>8.2f} V")



# ==== Startmeldung auf dem OLED ====
print_gain_ranges()
oled.fill(0)
oled.text("HF Power Meter", 0, 0)
oled.text("Bereich: 1W", 0, 16)
oled.show()
sleep(1)




def loop():
# ==== Hauptloop ====
    while True:
        voltage_0 = readChannel(ADS1115_COMP_0_GND)
        voltage_1 = readChannel(ADS1115_COMP_1_GND)
        #voltage_0 = autorange_read(ADS1115_COMP_0_GND)
        power = cal_1w.get_power(voltage_0)
        peak = track_peak(power, hold_time=4.0)
        gain = adc.getVoltageRange_mV()
        print("Aktiver Gain-Bereich: ±{} mV".format(gain))


       # print("Spannung: {:.3f} V → {:.3f} W".format(voltage_0, power))

        oled.fill(0)
        oled.text("V:", 0, 0)
        oled.text("{:.2f} V".format(voltage_0), 20, 0)
        oled.text("{:.2f} V".format(voltage_1), 70, 0)
        
        oled.text("Gain:", 0, 16)
        oled.text("{:.2f} W".format(gain), 70, 16)
        

        # Große Schrift für Watt-Zahl
        font_writer = writer.Writer(oled, freesans20, False)
        font_writer.set_textpos(5, 30)
        font_writer.printstring("{:.3f} W".format(power))
        
        oled.text("max", 80, 30)
        oled.text("{:.2f}".format(peak), 80, 39)
        
        #bars(power, 0.18)  # z. B. max 1 W im 1W-Bereich
        bars_with_peak(power, peak, max_value=0.18, y0=50,height=5)
        bars_with_peak(power, peak, max_value=0.18, y0=56,height=5)
        oled.show()


        oled.show()
        sleep(0.1)
        
        
#test_cal_1w_linear_steps()
loop()
