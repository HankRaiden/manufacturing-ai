# 4. Datenmodell

Vier Objekte reichen für den Anfang.

## Auftrag

Kommt aus dem Export der Branchensoftware und wird nicht von Hand gepflegt.

| Feld | Typ | Bemerkung |
|---|---|---|
| Auftragsnummer | Text | Der Schlüssel, der alles verbindet. Steht auf der Tasche, im QR-Code und in E-Mails |
| Kunde, Kundennummer | Text | |
| Produktart, Beschreibung | Text | |
| Auflage | Zahl | |
| Sachbearbeitung | Text | Für Filter und Auswertung je Person |
| Termin Fertigung | Datum | |
| Termin Weiterverarbeitung | Datum | |
| Liefertermin | Datum | |
| Lieferadresse | Name, Straße, PLZ, Ort | Grundlage für den Versand-Planer |
| Status | Auswahl | Offen, In Produktion, Fertig, Versandbereit, Versendet, Problem |

## Arbeitsgang

Ein Auftrag hat mehrere Arbeitsgänge. Das ist wichtig: Ein Auftrag ist selten ein einziger Durchlauf. Wer das nicht abbildet, plant die Kapazität falsch.

| Feld | Typ | Bemerkung |
|---|---|---|
| Kostenstelle | Text | Maschine oder Handarbeitsplatz |
| Bezeichnung | Text | |
| Rüstzeit | Minuten | |
| Laufzeit | Minuten | |
| Tag | Datum | aus dem Termin des Auftrags |

## Statusmeldung

Jeder Scan wird als eigenes Ereignis gespeichert und nie überschrieben. So bleibt nachvollziehbar, wer wann was gemeldet hat.

| Feld | Typ |
|---|---|
| Auftragsnummer | Text |
| Status | In Produktion, Störung, Fertig |
| Wer | Text |
| Zeit | Zeitstempel |
| Notiz | Text |

## Vorgang (Case)

Aus jeder eingehenden E-Mail wird ein Vorgang. Die 13 Felder sind in drei Gruppen geordnet, damit oben steht, was man zum Entscheiden braucht.

### Gruppe 1: Steuerung

| Feld | Werte | Wozu |
|---|---|---|
| Status | Neu, In Bearbeitung, Wartet auf Kunde, Wartet auf Intern, Erledigt | Jeder Vorgang muss bewegt werden |
| Priorität | Niedrig, Normal, Hoch, Kritisch | Signalwörter wie "eilt" oder "Stopp" heben die Priorität |
| Zuständig | Rolle oder Person | Ersetzt das Weiterleiten im Postfach |
| Art | Preisanfrage / Kalkulation, Auftrag (Neu), Datenlieferung, Reklamation, Status-Nachfrage, Rechnung / Admin, Sonstiges | Grundlage für Regeln, etwa "Reklamation geht an die Geschäftsführung" |
| Antwort bis | Datum | Die Frist für die Antwort, nicht der Liefertermin der Ware |

### Gruppe 2: Produktionsdaten

| Feld | Werte | Wozu |
|---|---|---|
| Auftragsnummer | Text | Die Verbindung zu Säule 1. Ohne sie wird wieder gesucht |
| Wunschtermin des Kunden | Datum | "Brauche ich bis Freitag". Wichtig für die Planung |
| Kategorie | je nach Betrieb | Hilft bei der Zuteilung |
| Anhang | Keine Dateien, Anhang vorhanden, Download-Link | In vielen Betrieben ist eine Anfrage ohne Daten nicht bearbeitbar. Das sieht man so in der Liste |
| Betreff | Text | Für die Listenansicht |

### Gruppe 3: Inhalt

| Feld | Werte | Wozu |
|---|---|---|
| Zusammenfassung | Text | Von KI oder Regel erzeugt |
| Stimmung | Positiv, Neutral, Negativ | "Negativ" bei einer Reklamation löst eine Eskalation aus |
| Originaltext | Text | Unverändert. Die Absicherung gegen Fehler der KI |

Die Feldliste als CSV zum Importieren: [`templates/case-felder.csv`](../templates/case-felder.csv).

## Was bewusst fehlt

- **Kalkulation.** Eine eigene Kalkulation mit Papierpreisen, Rüstkosten und Marge war im ersten Entwurf geplant und ist später aus dem Umfang gefallen. Sie ist das komplexeste Stück und gehört nicht in die erste Ausbaustufe.
- **Lager und Material.** Aus dem Materialzettel ließe sich eine Bestellvorlage und eine Nachkalkulation ableiten. Sinnvoll, aber ein eigenes Projekt.
- **Anbindung an Buchhaltung oder ERP.** Daten werden gelesen, nicht zurückgeschrieben. Das hält das Risiko klein.
