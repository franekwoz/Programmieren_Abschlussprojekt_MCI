# TODO

## P0 – Pflicht

- [x] Basisdateien inspizieren und vorhandenen Code nachvollziehbar erweitern
- [x] BatteryPack implementieren
- [x] BatterySimulator implementieren
- [x] Beispielskripte ausführen
- [x] Projektstruktur anlegen
- [x] GPS-CSV-Reader und Datenmodelle einrichten
- [x] Kinematik und Fahrphysik implementieren
- [x] Akkumodelle und CLI vorbereiten
- [x] Diagramme und Ergebnisdateien erzeugen
- [x] Tests für die Pflichtfunktionen anlegen

## P1 – Qualität

- [ ] bessere Fehlermeldungen und Grenzwerttests ergänzen
- [ ] Performance bei größeren Routen verbessern
- [ ] Dokumentation weiter ausbauen

## P2 – Erweiterungen

### Rolling resistance
- Ziel: Rollwiderstand in die Fahrphysik integrieren
- Datei: src/ebike_sim/extensions/rolling_resistance.py
- geplante Schnittstelle: calculate_rolling_resistance(...)
- offene Implementierungsschritte: Konfiguration, Kraftmodell, Untergründe
- Akzeptanzkriterien: zusätzliche Kraftkomponente und Test abgedeckt

### Temperature model
- Ziel: Temperaturabhängige Batterieeffekte modellieren
- Datei: src/ebike_sim/extensions/temperature_model.py
- geplante Schnittstelle: calculate_temperature_adjusted_resistance(...), calculate_temperature_adjusted_capacity(...)
- offene Implementierungsschritte: Temperaturkoeffizienten, Segmentnutzung aus GPS
- Akzeptanzkriterien: sinnvolle Anpassung der Simulation

### Air density
- Ziel: Luftdichte aus Höhe und Temperatur berechnen
- Datei: src/ebike_sim/extensions/air_density.py
- geplante Schnittstelle: calculate_air_density(...)
- offene Implementierungsschritte: barometrisches Modell
- Akzeptanzkriterien: realistische Dichtewerte

### Recuperation
- Ziel: Rekuperation unterstützen
- Datei: src/ebike_sim/extensions/recuperation.py
- geplante Schnittstelle: calculate_recuperation_current(...)
- offene Implementierungsschritte: negative Leistung erkennen, Strombegrenzung
- Akzeptanzkriterien: negative Ströme in der Simulation

### Weather
- Ziel: Wetterdaten optional einbeziehen
- Datei: src/ebike_sim/extensions/weather.py
- geplante Schnittstelle: TODO(extension)
- offene Implementierungsschritte: Windmodell, optionale Datei
- Akzeptanzkriterien: zusätzliche Kräfte und Datenexport

### Route map
- Ziel: interaktive Routenkarte exportieren
- Datei: src/ebike_sim/extensions/route_map.py
- geplante Schnittstelle: TODO(extension)
- offene Implementierungsschritte: folium-Integration, Farbgebung
- Akzeptanzkriterien: HTML-Ausgabe

### Parameter study
- Ziel: Parameterstudien automatisieren
- Datei: src/ebike_sim/extensions/parameter_study.py
- geplante Schnittstelle: TODO(extension)
- offene Implementierungsschritte: Vergleich verschiedener Parameter
- Akzeptanzkriterien: tabellarischer Export
