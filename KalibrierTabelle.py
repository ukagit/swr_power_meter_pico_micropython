from cal_table import KalibrierTabelle

table_1w = KalibrierTabelle("cal_1w.json")
table_10w = KalibrierTabelle("cal_10w.json")
table_100w = KalibrierTabelle("cal_100w.json")

# Spannung messen z. B. v = read_adc_voltage()
v = 6.3
print("Gemessene Leistung (10W-Bereich):", table_10w.get_power(v), "W")

# Punkt hinzufügen
table_10w.add_point(v, 10.0)
# Anzeige
table_10w.show_table()
