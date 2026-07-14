# E-Bike Abschlussprojekt

Dieses Projekt implementiert eine minimale Auswertung einer E-Bike-Fahrt und eine einfache Simulation verschiedener Akkutypen.

## Projektziel

- GPS-Daten aus einer semikolongetrennten CSV einlesen
- Strecke und Fahrphysik berechnen
- Akkus simulieren
- Ergebnisse als Diagramme und Zusammenfassungen exportieren

## Ausgangsdateien

Die Basis bildet die vorhandene Kapitel-09.2-Struktur mit:

- plotting_utils.py
- example_utils.py
- battery_pack_start.py
- battery_simulator_start.py

## Projektstruktur

Siehe die Ordnerstruktur in der Projektübersicht.

## Installation

```bash
python -m venv .venv
pip install -r requirements.txt
```

## Eingabeformat

Die GPS-CSV verwendet das Trennzeichen `;` mit den Spalten `lat`, `lon`, `ele`, `time`, `temperature`.

## Beispielaufruf

```bash
python -m ebike_sim --input data/final_project_input_data.csv --battery both --output outputs
```

## Ergebnisdateien

Die Minimalversion erzeugt Dateien unter `outputs/figures`, `outputs/reports` und `outputs/logs`.

## Testausführung

```bash
pytest
```

## Akkumodell

Die einfache Startversion verwendet ein lineares OCV-Modell mit Innenwiderstand. Die erweiterte Variante nutzt LiPo- und MMC-Batterien mit linear interpolierter Zellspannung.

## Formeln

Die Minimalversion verwendet Haversine-Distanz, Geschwindigkeit, Beschleunigung, Steigung und einfache Kraft- und Leistungsberechnung.

## Physikalische Annahmen

- vereinfachter Radnabenmotor
- kein Getriebe
- kein Rollwiderstand in der Minimalversion
- keine Rekuperation in der Minimalversion
- Motorwirkungsgrad 100 %

## Bekannte Einschränkungen

- Temperatur beeinflusst die Pflichtsimulation noch nicht.
- Erweiterungen sind vorbereitet, aber noch nicht in den Standardlauf integriert.
