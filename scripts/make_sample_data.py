"""Erzeugt die synthetischen Beispieldaten in data/sample.

Alle Firmen, Personen, Adressen und Zahlen sind frei erfunden. Der Zufall ist
fest eingestellt (Seed), damit jeder dieselben Daten bekommt.

    python3 scripts/make_sample_data.py
"""
import csv
import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path
from xml.sax.saxutils import quoteattr

ROOT = Path(__file__).resolve().parent.parent / "data" / "sample"
MONDAY = date(2026, 3, 9)
TODAY = date(2026, 3, 11)
SERIAL_EPOCH = date(1899, 12, 30)
rng = random.Random(7)

PRESSES = [("4110", "Bogenoffset 1"), ("4120", "Bogenoffset 2"), ("4130", "Digitaldruck")]
FINISHING = [("4210", "Schneiden"), ("4220", "Falzen"), ("4310", "Veredelung")]
PRODUCTS = ["Broschüre", "Flyer", "Plakat", "Faltschachtel", "Mappe", "Katalog", "Etikett"]
CLERKS = ["MA-1", "MA-2", "MA-3"]
CUSTOMERS = [
    ("Muster Verlag GmbH", "Beispielweg 1", "50667", "Köln"),
    ("Rheinblick Events GmbH", "Uferallee 22", "40213", "Düsseldorf"),
    ("Kaffeerösterei Bohne & Co.", "Röstergasse 5", "50823", "Köln"),
    ("Stadtwerke Musterstadt", "Am Werk 3", "53111", "Bonn"),
    ("Agentur Farbraum", "Lindenstraße 48", "50674", "Köln"),
    ("Möbelhaus Eiche", "Industriering 9", "51063", "Köln"),
    ("Praxis Dr. Beispiel", "Parkstraße 14", "53113", "Bonn"),
    ("Buchhandlung Seitenweise", "Marktplatz 2", "52062", "Aachen"),
    ("Brauerei Hopfenhof", "Brauweg 7", "51373", "Leverkusen"),
    ("TechStart Labs GmbH", "Gründerallee 11", "40221", "Düsseldorf"),
]


def serial(day: date) -> int:
    return (day - SERIAL_EPOCH).days


def make_jobs() -> list:
    jobs_dir = ROOT / "jobs"
    jobs_dir.mkdir(parents=True, exist_ok=True)
    for old in jobs_dir.glob("*.xml"):
        old.unlink()
    jobs = []
    for index in range(24):
        number = f"26-{101 + index:04d}"
        name, street, plz, city = rng.choice(CUSTOMERS)
        print_day = MONDAY + timedelta(days=rng.randint(0, 4))
        finishing_day = print_day + timedelta(days=1)
        delivery_day = finishing_day + timedelta(days=rng.randint(1, 2))
        press = rng.choice(PRESSES)
        operations = [(press, "Druck", rng.choice([20, 30, 40, 50]), rng.choice([60, 90, 120, 180, 240]), "druck")]
        for centre in rng.sample(FINISHING, rng.randint(1, 2)):
            operations.append((centre, centre[1], rng.choice([10, 15, 20]), rng.choice([30, 45, 60, 90]), "weiterverarbeitung"))
        lines = [
            '<?xml version="1.0" encoding="utf-8"?>',
            f"<Auftrag nummer={quoteattr(number)} produktart={quoteattr(rng.choice(PRODUCTS))} "
            f'beschreibung="Beispielauftrag {index + 1}" sachbearbeiter={quoteattr(rng.choice(CLERKS))}>',
            f"  <Kunde name={quoteattr(name)} kundennummer={quoteattr('K-' + str(1000 + CUSTOMERS.index((name, street, plz, city))))}/>",
            f'  <Auflage hoehe="{rng.choice([250, 500, 1000, 2500, 5000, 10000])}"/>',
            f'  <Termine druck="{serial(print_day)}" weiterverarbeitung="{serial(finishing_day)}" lieferung="{serial(delivery_day)}"/>',
            f"  <Lieferadresse name={quoteattr(name)} strasse={quoteattr(street)} plz={quoteattr(plz)} ort={quoteattr(city)}/>",
            "  <Arbeitsgaenge>",
        ]
        for (centre_id, centre_name), label, setup, run, when in operations:
            lines.append(
                f"    <Arbeitsgang kostenstelle={quoteattr(centre_id)} name={quoteattr(centre_name)} "
                f'bezeichnung={quoteattr(label)} ruestzeit_min="{setup}" laufzeit_min="{run}" termin="{when}"/>'
            )
        lines += ["  </Arbeitsgaenge>", "</Auftrag>", ""]
        (jobs_dir / f"{number}.xml").write_text("\n".join(lines), encoding="utf-8")
        jobs.append((number, print_day, finishing_day))
    return jobs


def make_events(jobs: list) -> None:
    """Scans aus der Halle bis zum Demo-Tag."""
    events = []
    for position, (number, print_day, finishing_day) in enumerate(jobs):
        if print_day > TODAY:
            continue
        start = datetime.combine(print_day, datetime.min.time()).replace(hour=7 + position % 6, minute=10)
        events.append({"auftrag": number, "status": "In Produktion", "wer": "Halle", "zeit": start.isoformat(), "notiz": ""})
        if position == 5:
            events.append({"auftrag": number, "status": "Problem", "wer": "Halle", "zeit": (start + timedelta(hours=1)).isoformat(), "notiz": "Material fehlt"})
        elif finishing_day <= TODAY:
            done = datetime.combine(finishing_day, datetime.min.time()).replace(hour=14, minute=30)
            events.append({"auftrag": number, "status": "Fertig", "wer": "Halle", "zeit": done.isoformat(), "notiz": ""})
    (ROOT / "status_events.jsonl").write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events), encoding="utf-8")


def make_customers() -> None:
    rows = []
    for index in range(40):
        last = TODAY - timedelta(days=rng.randint(20, 1400))
        rows.append(
            {
                "kundennummer": f"K-{2000 + index}",
                "firma": f"Beispielkunde {index + 1:02d} GmbH",
                "email": f"einkauf@beispielkunde{index + 1:02d}.example",
                "letzter_auftrag": last.isoformat(),
                "umsatz_3_jahre": rng.choice([400, 900, 1800, 3500, 7000, 12000, 26000, 48000]),
                "werbung_erlaubt": "ja" if rng.random() > 0.15 else "nein",
            }
        )
    with (ROOT / "customers.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def make_offers() -> None:
    rows = []
    for index in range(8):
        sent = TODAY - timedelta(days=rng.randint(1, 12))
        answered = index in (1, 6)
        rows.append(
            {
                "angebot": f"A26-{300 + index:04d}",
                "kunde": f"Beispielkunde {index + 3:02d} GmbH",
                "ansprechpartner": "Frau Beispiel" if index % 2 else "Herr Muster",
                "sachbearbeiter": CLERKS[index % 3],
                "gesendet_am": sent.isoformat(),
                "status": "offen",
                "antwort_am": (sent + timedelta(days=1)).isoformat() if answered else "",
                "erinnerungen": 0,
                "letzte_erinnerung": "",
            }
        )
    with (ROOT / "offers.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


EMAILS = [
    ("einkauf@beispielkunde01.example", "Anfrage 5.000 Broschüren", "Guten Tag,\nwir benötigen ein Angebot für 5.000 Broschüren, 24 Seiten, A4. Lieferung bis 27.03. wäre ideal.\nViele Grüße", 0),
    ("marketing@beispielkunde02.example", "Reklamation Auftrag 26-0104", "Hallo,\ndie Lieferung zu 26-0104 ist beschädigt angekommen, mehrere Kartons sind eingedrückt. Das ist sehr ärgerlich, wir brauchen dringend Ersatz.\nMfG", 2),
    ("office@beispielkunde03.example", "Wann kommt unsere Lieferung?", "Guten Morgen,\nwann kommt unsere Lieferung zum Auftrag 26-0110? Wir bräuchten sie bis Freitag.\nDanke", 0),
    ("grafik@beispielkunde04.example", "Druckdaten Katalog", "Hallo zusammen,\nanbei die Daten für den Katalog als Download: https://we.tl/beispiel\nBitte um kurze Bestätigung.", 0),
    ("buchhaltung@beispielkunde05.example", "Rechnung fehlt", "Sehr geehrte Damen und Herren,\nuns fehlt noch die Rechnung zur letzten Lieferung. Können Sie diese bitte erneut senden?\nFreundliche Grüße", 0),
    ("inhaber@beispielkunde06.example", "Bestellung Flyer", "Guten Tag,\nhiermit bestelle ich 2.500 Flyer wie im Angebot A26-0302 beschrieben. Die finale Datei hängt an.\nViele Grüße", 1),
    ("einkauf@beispielkunde07.example", "Vielen Dank", "Hallo,\nvielen Dank für die schnelle Lieferung, die Mappen sind super geworden.\nBeste Grüße", 0),
    ("leitung@beispielkunde08.example", "EILT: Stopp Auftrag 26-0118", "Bitte sofort stoppen! Im Auftrag 26-0118 ist ein Fehler im Text. Korrigierte Datei folgt heute noch.", 0),
]


def make_emails() -> None:
    rows = []
    for index, (sender, subject, body, attachments) in enumerate(EMAILS):
        received = datetime.combine(TODAY, datetime.min.time()).replace(hour=7 + index, minute=5 * index)
        rows.append({"von": sender, "betreff": subject, "text": body, "anhaenge": attachments, "eingang": received.isoformat()})
    (ROOT / "emails.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    job_list = make_jobs()
    make_events(job_list)
    make_customers()
    make_offers()
    make_emails()
    print(f"Beispieldaten geschrieben nach {ROOT}")
