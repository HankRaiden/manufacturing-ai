"""Säule 1, Schritt 1: Auftragsdaten aus dem XML-Export der Branchensoftware lesen.

Fast jede Branchensoftware (MIS/ERP) in der Fertigung kann pro Auftrag eine
XML-Datei in einen Ordner ("Hotfolder") schreiben. Diese Dateien enthalten bereits
alles, was für Transparenz gebraucht wird: Termine, Arbeitsgänge, Kostenstellen,
geplante Zeiten, Lieferadresse. In vielen Betrieben nutzt sie niemand.

Das Beispielschema in data/sample/jobs ist bewusst neutral gehalten. Für ein
echtes System reicht es in der Regel, die Namen in FIELD_MAP anzupassen.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable, Optional

# Viele Systeme exportieren Termine als fortlaufende Tageszahl (wie Excel).
SERIAL_EPOCH = date(1899, 12, 30)

# Element- und Attributnamen des Exports. Hier an das eigene System anpassen.
FIELD_MAP = {
    "job_number": "nummer",
    "product_type": "produktart",
    "description": "beschreibung",
    "clerk": "sachbearbeiter",
    "customer": ("Kunde", "name"),
    "customer_number": ("Kunde", "kundennummer"),
    "quantity": ("Auflage", "hoehe"),
    "dates": "Termine",
    "delivery": "Lieferadresse",
    "operation": "Arbeitsgang",
}


def parse_date(value: Optional[str]) -> Optional[date]:
    """Akzeptiert ISO-Datum (2026-03-09) und serielle Tageszahl (46090)."""
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    if value.isdigit():
        return SERIAL_EPOCH + timedelta(days=int(value))
    return date.fromisoformat(value)


@dataclass
class Operation:
    """Ein Arbeitsgang auf einer Kostenstelle (Maschine oder Handarbeitsplatz)."""

    work_centre_id: str
    work_centre: str
    name: str
    setup_min: float
    run_min: float
    day: Optional[date]

    @property
    def minutes(self) -> float:
        return self.setup_min + self.run_min


@dataclass
class Job:
    number: str
    customer: str
    customer_number: str
    product_type: str
    description: str
    clerk: str
    quantity: int
    print_date: Optional[date]
    finishing_date: Optional[date]
    delivery_date: Optional[date]
    delivery_name: str
    delivery_street: str
    delivery_zip: str
    delivery_city: str
    operations: list = field(default_factory=list)

    @property
    def planned_minutes(self) -> float:
        return sum(op.minutes for op in self.operations)


def _attr(root: ET.Element, spec) -> str:
    if isinstance(spec, tuple):
        element = root.find(spec[0])
        return (element.get(spec[1], "") if element is not None else "").strip()
    return root.get(spec, "").strip()


def parse_job(path: Path) -> Job:
    root = ET.parse(path).getroot()
    dates = root.find(FIELD_MAP["dates"])
    delivery = root.find(FIELD_MAP["delivery"])
    get_date = lambda key: parse_date(dates.get(key)) if dates is not None else None  # noqa: E731
    day_by_key = {
        "druck": get_date("druck"),
        "weiterverarbeitung": get_date("weiterverarbeitung"),
        "lieferung": get_date("lieferung"),
    }

    operations = []
    for element in root.iter(FIELD_MAP["operation"]):
        operations.append(
            Operation(
                work_centre_id=element.get("kostenstelle", ""),
                work_centre=element.get("name", ""),
                name=element.get("bezeichnung", ""),
                setup_min=float(element.get("ruestzeit_min", "0") or 0),
                run_min=float(element.get("laufzeit_min", "0") or 0),
                day=day_by_key.get(element.get("termin", "druck")),
            )
        )

    quantity = _attr(root, FIELD_MAP["quantity"])
    return Job(
        number=_attr(root, FIELD_MAP["job_number"]),
        customer=_attr(root, FIELD_MAP["customer"]),
        customer_number=_attr(root, FIELD_MAP["customer_number"]),
        product_type=_attr(root, FIELD_MAP["product_type"]),
        description=_attr(root, FIELD_MAP["description"]),
        clerk=_attr(root, FIELD_MAP["clerk"]),
        quantity=int(quantity) if quantity.isdigit() else 0,
        print_date=day_by_key["druck"],
        finishing_date=day_by_key["weiterverarbeitung"],
        delivery_date=day_by_key["lieferung"],
        delivery_name=delivery.get("name", "") if delivery is not None else "",
        delivery_street=delivery.get("strasse", "") if delivery is not None else "",
        delivery_zip=delivery.get("plz", "") if delivery is not None else "",
        delivery_city=delivery.get("ort", "") if delivery is not None else "",
        operations=operations,
    )


def read_folder(folder: Path) -> tuple:
    """Liest alle XML-Dateien eines Hotfolders.

    Gibt (aufträge, fehler) zurück. Eine defekte Datei stoppt den Lauf nicht,
    sie steht mit Dateiname und Grund in der Fehlerliste.
    """
    jobs, errors = [], []
    for path in sorted(Path(folder).glob("*.xml")):
        try:
            jobs.append(parse_job(path))
        except (ET.ParseError, ValueError) as exc:
            errors.append((path.name, str(exc)))
    return jobs, errors


def load_jobs(folder: Path) -> list:
    """Kurzform: nur die lesbaren Aufträge."""
    return read_folder(folder)[0]


def work_centres(jobs: Iterable[Job]) -> dict:
    """Alle Kostenstellen, die in den Aufträgen vorkommen: {id: name}."""
    result = {}
    for job in jobs:
        for op in job.operations:
            result.setdefault(op.work_centre_id, op.work_centre)
    return dict(sorted(result.items()))
