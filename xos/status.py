"""Säule 1, Schritt 3: Status aus der Halle per QR-Code.

Der Plan aus der Branchensoftware sagt, was passieren soll. Der Scan in der
Halle sagt, was passiert ist. Auf jeder Auftragstasche klebt ein QR-Code, der
auf eine Seite mit drei Knöpfen führt: "In Produktion", "Störung", "Fertig".

Papier bleibt erlaubt. Das ist Absicht: Die Mitarbeitenden behalten ihre Tasche,
das Büro bekommt trotzdem Echtzeit-Daten.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

OFFEN, IN_PRODUKTION, FERTIG = "Offen", "In Produktion", "Fertig"
VERSANDBEREIT, VERSENDET, PROBLEM = "Versandbereit", "Versendet", "Problem"

STATUSES = [OFFEN, IN_PRODUKTION, FERTIG, VERSANDBEREIT, VERSENDET, PROBLEM]

# Was die Halle per Scan melden darf, und worauf es den Auftrag setzt.
SCAN_ACTIONS = {"start": IN_PRODUKTION, "stoerung": PROBLEM, "fertig": FERTIG}

ALLOWED = {
    OFFEN: {IN_PRODUKTION, PROBLEM},
    IN_PRODUKTION: {FERTIG, PROBLEM},
    PROBLEM: {IN_PRODUKTION, FERTIG},
    FERTIG: {VERSANDBEREIT, PROBLEM},
    VERSANDBEREIT: {VERSENDET, PROBLEM},
    VERSENDET: set(),
}


def scan_url(base_url: str, job_number: str) -> str:
    """Die Adresse, die als QR-Code auf die Auftragstasche gedruckt wird."""
    return f"{base_url.rstrip('/')}/status?{urlencode({'auftrag': job_number})}"


def next_status(current: str, target: str) -> str:
    if target not in ALLOWED.get(current, set()):
        raise ValueError(f"Übergang nicht erlaubt: {current} -> {target}")
    return target


class EventLog:
    """Append-only Protokoll (JSON Lines). Jede Meldung bleibt nachvollziehbar."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def append(self, job_number: str, status: str, who: str, at: datetime, note: str = "") -> dict:
        event = {"auftrag": job_number, "status": status, "wer": who, "zeit": at.isoformat(), "notiz": note}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        return event

    def read(self) -> list:
        if not self.path.exists():
            return []
        with self.path.open(encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]


def replay(events: list) -> tuple:
    """Spielt alle Meldungen in zeitlicher Reihenfolge ab.

    Gibt (status je Auftrag, abgelehnte Meldungen) zurück. Ein unmöglicher
    Übergang wird nicht still übernommen, er landet mit Grund in der zweiten Liste.
    """
    status, rejected = {}, []
    for event in sorted(events, key=lambda e: e["zeit"]):
        job = event["auftrag"]
        try:
            status[job] = next_status(status.get(job, OFFEN), event["status"])
        except ValueError as exc:
            rejected.append({**event, "grund": str(exc)})
    return status, rejected


def current_status(events: list) -> dict:
    """Kurzform: nur der aktuelle Status je Auftrag."""
    return replay(events)[0]
