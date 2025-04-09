# cal_table.py
try:
    import ujson as json
except ImportError:
    import json

import math

class KalibrierTabelle:
    def __init__(self, filename):
        self.filename = filename
        self.lookup_table = []
        self.last_voltage = 0.0
        self.load()

    def load(self):
        try:
            with open(self.filename, "r") as f:
                self.lookup_table = json.load(f)
            self.lookup_table = [tuple(x) for x in self.lookup_table]
            self.lookup_table.sort()
            print(f"[{self.filename}] Kalibriertabelle geladen.")
        except:
            print(f"[{self.filename}] Neue Kalibriertabelle wird erstellt.")
            self.init_default()

    def save(self):
        try:
            with open(self.filename, "w") as f:
                json.dump(self.lookup_table, f)
            print(f"[{self.filename}] Kalibrierwerte gespeichert.")
        except Exception as e:
            print(f"[{self.filename}] Fehler beim Speichern:", e)

    def init_default(self):
        name = self.filename.lower()
        if "1w" in name:
            default = [(2.0, 1.0)]
        elif "10w" in name:
            default = [(6.32, 10.0)]
        elif "100w" in name:
            default = [(20.0, 100.0)]
        else:
            default = [(1.0, 1.0)]
        self.lookup_table = default
        self.save()

    def add_point(self, voltage, power):
        try:
            voltage = float(voltage)
            power = float(power)
            self.lookup_table.append((voltage, power))
            self.lookup_table.sort()
            self.save()
            print(f"[{self.filename}] Punkt hinzugefügt: {voltage:.2f} V → {power:.2f} W")
        except Exception as e:
            print("Fehler beim Hinzufügen:", e)

    def get_power(self, voltage, return_dbm=False):
        self.last_voltage = voltage
        table = self.lookup_table
        if not table:
            return None

        if voltage <= table[0][0]:
            power = table[0][1]
        elif voltage >= table[-1][0]:
            power = table[-1][1]
        else:
            for i in range(1, len(table)):
                v1, p1 = table[i - 1]
                v2, p2 = table[i]
                if v1 <= voltage <= v2:
                    ratio = (voltage - v1) / (v2 - v1)
                    power = p1 + ratio * (p2 - p1)
                    break

        if return_dbm:
            if power <= 0:
                return -float('inf')
            return 10 * math.log10(power * 1000)

        return power

    def add_last_point(self, power):
        """Verwendet zuletzt gemessene Spannung für neuen Punkt"""
        self.add_point(self.last_voltage, power)

    def show_table(self):
        print(f"\n[{self.filename}] Kalibrierpunkte (V → W):")
        if not self.lookup_table:
            print("Tabelle ist leer.")
            return
        for v, p in self.lookup_table:
            print(f"{v:>6.2f} V → {p:>6.2f} W")
