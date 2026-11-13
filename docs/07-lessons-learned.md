# 7. Was ich heute anders machen würde

Wichtig vorweg: Das Projekt ist nicht über Konzept, Angebot und Demo hinausgekommen. Die Punkte hier sind Lehren aus dieser Phase, nicht aus dem laufenden Betrieb.

## 1. Eigene Software statt White-Label-CRM

Ich habe die Demo auf einem White-Label-CRM gebaut, weil dort vieles schon da ist: Kontakte, Postfächer, Automatisierungen, Rechte. Für E-Mails und Kampagnen passt das gut.

Für die Halle passt es schlecht. Ein Maschinen-Kalender, eine Auftragsliste mit Arbeitsgängen, ein Versand-Planer: Das sind keine CRM-Funktionen. Ich habe sie als eigene Seiten gebaut und in die Oberfläche eingehängt. Die Plattform trug damit nur noch einen Teil, und ich wäre trotzdem an sie gebunden gewesen: an ihre Grenzen und an ihre Änderungen.

Heute würde ich die wenigen Schlüsselfunktionen als eigene, kleine Software bauen. Die Referenz-Implementierung in diesem Repository zeigt, wie wenig Code das im Kern ist.

## 2. Die Daten bleiben beim Auftraggeber

Aufträge, Kunden, Preise und E-Mails sind das Herz eines Betriebs. In meinem Aufbau hätten sie auf einer fremden Plattform gelegen.

Heute würde ich so bauen, dass die Daten im Betrieb bleiben: auf einem eigenen Server oder in einer Umgebung, die der Betrieb selbst kontrolliert. Das macht Gespräche über Datenschutz einfacher, und der Betrieb bleibt unabhängig, auch von mir.

## 3. Mit einer Säule starten, nicht mit drei

Ich habe drei Säulen auf einmal geplant. Das war gut gemeint und zu viel: zu viel Umfang und zu viel Veränderung auf einmal für ein Team, das bisher mit Papier arbeitet.

Heute würde ich mit genau einer Säule anfangen. Welche das ist, entscheidet der Betrieb: die, in der er selbst den größten Mehrwert sieht. Ich kann eine Empfehlung geben, mehr nicht. In diesem Projekt war es die Visualisierung des Maschinenparks.

Woran ich meine Empfehlung festmachen würde:

- **Reaktivierung**, wenn schnell Umsatz sichtbar werden soll. Wenig Technik, Ergebnis in Wochen.
- **Auftragsliste mit QR-Status**, wenn das Suchen der größte Schmerz ist.
- **E-Mail-to-Case**, wenn Anfragen verloren gehen.

Die zweite Säule kommt, wenn die erste läuft und genutzt wird.

## 4. Bezahlung nach Ergebnis

Ich habe einen Festpreis angeboten. Damit trägt der Betrieb das ganze Risiko: Er zahlt, bevor er weiß, ob es wirkt.

Heute würde ich die Bezahlung an ein messbares Ergebnis knüpfen: an reaktivierten Umsatz, an gesparte Stunden, an die Zahl der Vorgänge mit eingehaltener Frist. Das gibt dem Betrieb Sicherheit, und es zwingt mich, nur das zu bauen, was wirklich etwas bringt.

Voraussetzung dafür ist eine ehrliche Messung vorher. Siehe [`05-kennzahlen-und-ersparnis.md`](05-kennzahlen-und-ersparnis.md).

## Was ich wieder so machen würde

- **Zuerst die vorhandenen Daten nutzen.** Der XML-Export war da. Keine Sensoren, keine neue Hardware.
- **Papier nicht abschaffen.** Die Auftragstasche bleibt, sie bekommt einen QR-Code.
- **Den Originaltext der E-Mail aufbewahren.** Das ist die Grundlage dafür, der KI überhaupt zu trauen.
- **Einen Vormittag zuschauen**, bevor ich irgendetwas vorschlage.
- **Erst rechnen, dann KI.** Der größte Nutzen steckt in Lesen, Rechnen und Anzeigen.
