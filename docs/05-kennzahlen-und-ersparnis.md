# 5. Kennzahlen und mögliche Ersparnis

Alle Zahlen auf dieser Seite sind Schätzungen und Zielwerte aus der Angebotsphase. Sie sind nicht gemessen, denn das System lief nie im Betrieb. Wer das Konzept nutzt, sollte zuerst den eigenen Ausgangswert erheben und nach drei Monaten wieder messen.

## Was der Status quo kostet

Die Rechnung steht als Code in [`xos/roi.py`](../xos/roi.py). Mit `python3 -m xos roi` läuft sie mit den Beispielannahmen.

| Kostentreiber | Rechnung | Schätzung pro Jahr |
|---|---|---|
| Suchen und Abstimmen | 7 Personen × 40 Minuten pro Tag × interner Stundensatz × 220 Arbeitstage | rund 82.000 € |
| Verpasste Anfragen | 1 Auftrag pro Woche × Deckungsbeitrag × 50 Wochen | rund 100.000 € |
| Maschinen-Leerlauf | 1 Stunde pro Woche × Maschinenstundensatz × 50 Wochen | rund 15.000 € |
| Versand ohne Bündelung | Ersparnis pro Tag × 220 Arbeitstage | rund 22.000 € |
| **Summe** | | **rund 219.000 €** |

Drei Hinweise zur Ehrlichkeit dieser Rechnung:

- Sie zeigt ein Potenzial. Wie viel davon wirklich gehoben wird, hängt davon ab, ob das System genutzt wird. `payback_months()` hat dafür den Parameter `realised_share`.
- Gesparte Suchzeit ist erst dann Geld, wenn die Zeit für etwas anderes genutzt wird.
- Der größte Posten, die verpassten Anfragen, ist am schwersten zu belegen. Vorher zählen.

## Potenzial der Reaktivierung

| Annahme | Wert |
|---|---|
| Bestandskunden | 3.000 |
| Rücklauf (vorsichtig) | 2 % |
| Reaktivierte Kunden | 60 |
| Durchschnittlicher Auftrag | 2.000 € |
| **Zusätzlicher Umsatz** | **rund 120.000 €** |

Im Code: `reactivation.potential(3000, 0.02, 2000)`.

## Kennzahlen, die sich zu messen lohnen

### Halle

| Kennzahl | Vorher | Ziel |
|---|---|---|
| Zeit der Geschäftsführung für Statusabfragen | rund 5 Stunden pro Woche | nahe null |
| Sichtbarkeit der Maschinenauslastung | keine | täglich je Kostenstelle |
| Liefertreue | nicht gemessen | Anteil pünktlicher Lieferungen |
| Durchlaufzeit je Auftrag | nicht gemessen | Eingang bis Versand |
| Stopps pro Tour | Einzelfahrten | gebündelt nach Region |

### Büro

| Kennzahl | Vorher | Ziel |
|---|---|---|
| Reaktionszeit auf Anfragen | 24 bis 48 Stunden | unter 2 Stunden |
| Verlorene E-Mails pro Monat | geschätzt 15 bis 20 | 0 |
| Nachfassquote bei Angeboten | rund 30 % | über 95 % |
| Kontrollaufwand der Geschäftsführung | rund 8 Stunden pro Woche | unter 1 Stunde |
| Einhaltung der Antwortfrist | nicht gemessen | über 90 % |
| Erstlösungsquote | nicht gemessen | über 80 % |

### Reaktivierung

| Kennzahl | Bedeutung |
|---|---|
| Angeschrieben | Kunden in der Kampagne |
| Antwortquote | Antworten geteilt durch Angeschriebene |
| Reaktivierungsquote | Bestellungen geteilt durch Angeschriebene |
| Umsatz aus der Kampagne | Summe der Aufträge reaktivierter Kunden |
| Abmeldungen | Wer nicht mehr angeschrieben werden will. Muss niedrig bleiben |

## Wie man misst, ohne sich zu belügen

1. **Vorher zählen.** Zwei Wochen Strichliste: Wie oft wird nach einem Auftrag gesucht? Wie viele Anrufe "Wo ist meine Lieferung"?
2. **Eine Kennzahl pro Säule** wählen, nicht zehn.
3. **Nach 90 Tagen** dieselbe Zählung wiederholen.
4. Was sich nicht verbessert hat, offen benennen.
