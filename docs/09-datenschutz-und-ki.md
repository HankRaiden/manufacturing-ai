# 9. Datenschutz und Umgang mit KI

Diese Seite ist eine Checkliste aus der Praxis und keine Rechtsberatung. Vor dem Start bitte mit dem eigenen Datenschutzbeauftragten oder einer Kanzlei abstimmen.

## E-Mails und Kundendaten

- **Auftragsverarbeitung regeln.** Sobald ein Dienstleister E-Mails und Kundenstammdaten verarbeitet, braucht es einen Vertrag zur Auftragsverarbeitung nach Art. 28 DSGVO. Das gilt auch für den Anbieter des Sprachmodells.
- **Wissen, wo die Daten liegen.** Welcher Anbieter, welches Land, welche Unterauftragnehmer? Am einfachsten ist die Antwort, wenn die Daten im Betrieb bleiben.
- **Persönliche Postfächer.** Werden nicht nur Sammeladressen, sondern auch persönliche Adressen angebunden, betrifft das die Mitarbeitenden. Vorher klären, was erlaubt ist, und einen vorhandenen Betriebsrat einbeziehen.
- **Auswertungen je Person** sind heikel. Kennzahlen zur Auslastung sind sinnvoll, eine Rangliste einzelner Mitarbeitender ist es selten.
- **Löschfristen** festlegen: Wie lange bleiben Vorgänge und Originaltexte gespeichert?

## Reaktivierung per E-Mail

Werbung per E-Mail braucht in Deutschland grundsätzlich eine Einwilligung (§ 7 UWG). Für Bestandskunden gibt es eine enge Ausnahme mit mehreren Bedingungen, unter anderem: Die Adresse stammt aus einem Kauf, beworben werden eigene ähnliche Leistungen, der Kunde hat nicht widersprochen, und er wurde bei der Erhebung und wird in jeder Nachricht auf sein Widerspruchsrecht hingewiesen.

Für die Praxis heißt das:

- Vor der Kampagne prüfen, für welche Kunden eine Einwilligung oder die Ausnahme greift.
- Kunden ohne diese Grundlage nicht anschreiben. Im Code ist das der Block `blocked` in [`xos/reactivation.py`](../xos/reactivation.py).
- In jeder Nachricht eine einfache Abmeldung anbieten und Abmeldungen sofort berücksichtigen.

## Regeln für den Einsatz von KI

| Regel | Umsetzung |
|---|---|
| Das Original bleibt erhalten | Der Text der E-Mail wird unverändert gespeichert. Die Zusammenfassung ist ein Zusatz |
| KI schlägt vor, feste Listen entscheiden | Art, Priorität und Stimmung werden nur übernommen, wenn sie zu den erlaubten Werten passen |
| Keine erfundenen Bezüge | Eine Auftragsnummer wird nur übernommen, wenn sie wörtlich in der E-Mail steht |
| Es geht auch ohne KI | Fällt das Modell aus, ordnen Regeln die E-Mail ein. Der Betrieb steht nicht |
| Menschen entscheiden bei Reklamationen | Eine negative Reklamation wird eskaliert, nicht automatisch beantwortet |
| Automatische Antworten nur für Standardfälle | Eingangsbestätigung ja, inhaltliche Zusagen nein |

## Zugangsdaten

- Keine Zugangsdaten in Code, Vorlagen oder Dokumenten. API-Schlüssel gehören in Umgebungsvariablen.
- In diesem Repository steht an der einzigen betroffenen Stelle ein Platzhalter.
