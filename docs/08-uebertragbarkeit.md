# 8. Für wen das noch passt

Das Projekt ist in einer Druckerei entstanden. Das Muster dahinter gibt es in sehr vielen Betrieben.

## Das Muster

Das Konzept passt, wenn die meisten dieser Punkte zutreffen:

- Es wird **auf Auftrag gefertigt**, nicht auf Lager.
- Ein Auftrag läuft über **mehrere Arbeitsgänge** an verschiedenen Stationen.
- Es gibt einen **Laufzettel**, eine Auftragstasche oder eine Begleitkarte aus Papier.
- Eine **Branchensoftware** für Kalkulation oder Planung ist vorhanden und kann Daten exportieren.
- Anfragen kommen per **E-Mail an mehrere Postfächer**.
- Es gibt **eigene Auslieferung** oder regelmäßige Touren.
- Der Kundenstamm besteht überwiegend aus **Geschäftskunden mit Wiederholbedarf**.

## Branchen

| Branche | Was der Auftragstasche entspricht | Was besonders zieht |
|---|---|---|
| Verpackungs- und Etikettenhersteller | Auftragsmappe | Maschinen-Kalender, Nachfassen von Angeboten |
| Werbetechnik, Schilder, Beschriftung | Auftragszettel | QR-Status, Versand und Montagetouren |
| Lohnfertigung Metall (Drehen, Fräsen, Lasern) | Laufkarte | Auslastung je Maschine, Anfragen mit Zeichnung im Anhang |
| Kunststoff-Spritzguss, Lohnfertigung | Fertigungsauftrag | Rüstzeiten im Kalender, Liefertreue |
| Schreinerei, Möbel- und Innenausbau | Auftragsmappe | Status je Gewerk, Montageplanung |
| Oberflächentechnik, Galvanik, Pulverbeschichtung | Warenbegleitschein | Status je Charge, Touren für Abholung und Lieferung |
| Werkzeug- und Formenbau | Projektmappe | Vorgänge je Projekt, Wunschtermine |
| Textilveredelung, Stickerei | Auftragszettel | viele kleine Aufträge, Datenlieferung per E-Mail |
| Lohnabfüller, Konfektionierer | Chargenprotokoll | Kapazität je Linie, Reaktivierung |

## Was sich je Branche ändert

- **Die Feldnamen im Export.** Dafür gibt es `FIELD_MAP` in [`xos/jobticket.py`](../xos/jobticket.py).
- **Die Arten von Vorgängen.** In einer Lohnfertigung heißt "Datenlieferung" eben "Zeichnung". Die Listen stehen oben in [`xos/cases.py`](../xos/cases.py).
- **Die Stichwörter** für Dringlichkeit und Art.
- **Die Kapazität** je Kostenstelle: eine Schicht, zwei Schichten, Wochenende.

## Was gleich bleibt

- Die Auftragsnummer als Schlüssel über alle Systeme.
- Plan aus der Software, Wirklichkeit aus dem Scan.
- Jede E-Mail wird ein Vorgang mit Zuständigkeit und Frist.
- Erst die vorhandenen Daten nutzen, dann Neues kaufen.

## Auch außerhalb der Fertigung

Säule 3 ist kein Fertigungsthema. E-Mail-to-Case und Nachfassen passen für jeden Betrieb, in dem Anfragen per E-Mail kommen: Handwerk, Agenturen, Dienstleister, Händler. Säule 2 passt für jeden Betrieb mit einem Kundenstamm, der lange nicht angesprochen wurde.
