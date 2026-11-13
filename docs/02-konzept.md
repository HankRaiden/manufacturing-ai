# 2. Konzept: drei Säulen, eine Oberfläche

Der Grundgedanke: Die Verwaltung soll so präzise laufen wie die Maschinen. Dafür braucht es kein neues ERP. Es braucht eine dünne Schicht über den vorhandenen Systemen, die drei Fragen jederzeit beantwortet:

- Wo steht jeder Auftrag, und wie voll sind die Maschinen?
- Welche Kundenanfrage liegt bei wem, und seit wann?
- Welche Kunden haben lange nichts bestellt?

## Säule 1: Transparenz in der Halle

| Baustein | Was er tut | Code |
|---|---|---|
| Auftragsliste | Alle Aufträge durchsuchbar nach Nummer, Kunde, Liefertermin und Status | [`xos/jobticket.py`](../xos/jobticket.py) |
| Maschinen-Kalender | Auslastung je Kostenstelle und Tag aus den geplanten Zeiten. Unter 70 % grün, bis 90 % gelb, darüber rot | [`xos/capacity.py`](../xos/capacity.py) |
| Status per QR-Code | Auf der Auftragstasche klebt ein Code. Scannen, einen von drei Knöpfen drücken: In Produktion, Störung, Fertig | [`xos/status.py`](../xos/status.py) |
| Versand-Planer | Fertige Aufträge werden nach Adresse zusammengefasst und nach Region gebündelt. Die Tour öffnet sich in Google Maps | [`xos/shipping.py`](../xos/shipping.py) |
| Übersicht | Offene, bald fällige, überfällige und gestörte Aufträge, dazu der Engpass der Woche | [`xos/dashboard.py`](../xos/dashboard.py) |

Zwei Entscheidungen waren wichtig:

**Papier bleibt.** Die Auftragstasche wird nicht abgeschafft. Sie bekommt einen QR-Code. Die Leute in der Halle behalten, was sie kennen, und das Büro bekommt trotzdem aktuelle Daten. Das soll den Widerstand gegen die Umstellung klein halten.

**Soll und Ist getrennt.** Der Export der Branchensoftware liefert den Plan. Der Scan liefert die Wirklichkeit. Erst beides zusammen ergibt ein ehrliches Bild.

## Säule 2: Umsatz aus dem Bestand

| Baustein | Was er tut | Code |
|---|---|---|
| Einteilung | Kunden nach Umsatz in A, B und C | [`xos/reactivation.py`](../xos/reactivation.py) |
| Auswahl | Inaktiv seit über 365 Tagen, mit Einwilligung, die wertvollsten zuerst | [`xos/reactivation.py`](../xos/reactivation.py) |
| Kampagne | Drei kurze, persönliche E-Mails | [`templates/reaktivierung-emails.md`](../templates/reaktivierung-emails.md) |
| Messung | Angeschrieben, geantwortet, bestellt, Umsatz | [`docs/05-kennzahlen-und-ersparnis.md`](05-kennzahlen-und-ersparnis.md) |

Diese Säule ist technisch die einfachste und bringt am schnellsten Geld. Deshalb stand sie im ersten Fahrplan ganz vorn.

## Säule 3: Ordnung im Büro

| Baustein | Was er tut | Code |
|---|---|---|
| E-Mail-to-Case | Jede eingehende E-Mail wird ein Vorgang mit Art, Priorität, Zuständigkeit und Antwortfrist | [`xos/cases.py`](../xos/cases.py) |
| Einordnung durch KI | Ein Sprachmodell fasst zusammen und ordnet ein. Jeder Wert wird gegen feste Listen geprüft | [`prompts/email_to_case.md`](../prompts/email_to_case.md) |
| Nachfassen | Angebote ohne Antwort bekommen nach drei Tagen eine Erinnerung | [`xos/followup.py`](../xos/followup.py) |
| Übersicht Büro | Offene Vorgänge, Angebote ohne Antwort je Person, Eskalationen | [`xos/dashboard.py`](../xos/dashboard.py) |

Die wichtigste Regel: **Der Originaltext der E-Mail bleibt immer unverändert am Vorgang.** Eine Zusammenfassung kann etwas weglassen. Wer zweifelt, liest das Original.

## Wo hier KI steckt und wo nicht

Der größte Teil des Nutzens kommt ohne KI aus: Daten lesen, rechnen, anzeigen. KI wird an genau zwei Stellen gebraucht:

1. E-Mails verstehen: Art, Dringlichkeit, Stimmung, Auftragsnummer, Wunschtermin.
2. Dokumente lesen, wenn die Information im Anhang steht und nicht im Text.

Das ist eine Lehre für sich: Erst die Daten in Ordnung bringen, dann KI darauf setzen. Umgekehrt funktioniert es nicht.
