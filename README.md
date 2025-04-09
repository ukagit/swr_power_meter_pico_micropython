
# Power & SWR Meter mit ADS1115 + OLED (MicroPython)

Dieses Projekt ist ein kompaktes HF-Leistungsmessgerät basierend auf einem ADS1115 ADC, SSD1306 OLED und Kalibrierungstabellen.
Es misst die Vorwärts- und Rücklaufleistung und zeigt SWR und Watt auf einem OLED an – mit AutoRange, Peak-Hold und SWR-Warnung.

---

## 🔧 Hardware

- ADS1115 (16 Bit ADC)
- SSD1306 OLED (128x64)
- HF-Richtkoppler (z. B. Spannungsteiler + Gleichrichter) wie z.B Stockton-Messbrücke von DG1KPN 
- Microcontroller (z. B. Raspberry Pi Pico)
- Optional: Taster für Kalibrierung / Bereichsumschaltung

![Stockton-Messbrücke von DG1KPN](richtkoppler_pic.png)

![mein HW Aufbau PICO OLED ADS in der Dose DL2DBG](IMG_8894.jpg)
![es geht auch einfach DL2DBG](IMG_8895.jpg)


- Beispiel -> Stockton-Messbrücke von DG1KPN
- mein HW Aufbau PICO OLED ADS1115 und Accu in der Dose DL2DBG
- es geht auch einfach DL2DBG

 ## Hinweis  
 Die Schaltung ist **isoliert von der "normalen" Masse** aufgebaut.  
 Daher erfolgt die Stromversorgung **über eine Batterie**.  
 Die **Kopplung der Messbrücke** mit dem **AD-Wandler** (A0_3, A1_3,z.b. ADS1115_COMP_0_3)  
 erfolgt als **differenzielle Messung** mit separatem Ground.
 Wenn man den Aufbau **nicht isoliert** oder **unsymmetrisch** umsetzt,  
 können sich **parasitäre Spannungen** einstellen.  
 Dadurch kann z. B. die **Reflektion nicht auf Null** gehen,  
 und das **SWR (Stehwellenverhältnis)** zeigt dann **fälschlicherweise Werte größer als 1.1**,  
 obwohl die reale Anpassung in Ordnung wäre.


## ⚙️ Features

- ✅ Messung von Vorwärts- und Rücklaufleistung (z. B. AIN0-AIN3, AIN1-AIN3)
- ✅ Automatische Bereichserkennung (AutoRange für optimalen Gain)
- ✅ SWR-Berechnung + Return Loss
- ✅ Peak-Hold für Leistung & SWR (einstellbar)
- ✅ OLED-Darstellung:
  - Balkenanzeige für Leistung
  - Balkenanzeige in Stufen für SWR
  - Großschrift für Wattanzeige (`freesans30`)
- ✅ Kalibrierung per JSON-Datei (linear interpoliert)
- ✅ JSON-basierte Speicherfunktion

---

## 📦 Dateien

| Datei              | Beschreibung                             |
|--------------------|------------------------------------------|
| `main_autorange.py`| Hauptprogramm mit AutoRange aktiviert    |
| `cal_1w.json`      | Beispiel-Kalibriertabelle (optional)     |
| `freesans30.py`    | Große Schrift für OLED (externe Font)    |

Die anderen Python Programme sind zum Test.---

## 🧠 Beispiel: Kalibriertabelle

## 💬 Feedback
Der gesamte Aufbau ist eine **kleine Übung für mich selbst**,  
Daher ist die Dokumentation aktuell noch **recht mager gehalten**.  
Sollte jedoch Interesse am **Nachbau** oder an neuen  **Funktionen** bestehen,   
freue ich mich über **Rückmeldungen**.  
Auch **konstruktive Hinweise oder Verbesserungsvorschläge** sind jederzeit willkommen!

```json
[
  [2.0, 1.0],
  [6.32, 10.0],
  [20.0, 100.0]
]
```

→ Spannung (V) → Leistung (W)  
Wird automatisch sortiert & interpoliert.

---

## 📈 AutoRange

AutoRange misst zunächst auf dem kleinsten Gain (±6.144 V) und passt automatisch auf ±4.096, ±2.048 V usw. an, bis die Auflösung optimal ist.

---

## 🧪 OLED-Anzeige

- Leistung in Großschrift
- Balkenanzeige für aktuelle Watt
- SWR-Stufenbalken (1.0–5.0)
- Fehleranzeige bei SWR > Limit
- Anzeige von Gain (optional aktivierbar)

---

## 📜 Lizenz

MIT License – freie Nutzung mit Namensnennung

---

> Projekt von [Uli DL2DBG] – inspiriert durch echte HF-Messpraxis 🔧📡
> Ich danke meinem neuen Mitarbeiter chatgpt  :-) 🔧📡
