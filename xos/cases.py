"""Säule 3: E-Mail-to-Case.

Jede eingehende E-Mail wird zu einem Vorgang (Case) mit Zuständigkeit, Status,
Priorität und Frist. Damit ist sichtbar, wer was bearbeitet, auch wenn jemand
krank ist.

Zwei Wege zur Einordnung:
- classify()       – Regeln und Stichwörter. Läuft ohne KI und ohne Kosten.
- from_llm_json()  – übernimmt das Ergebnis eines Sprachmodells (Prompt in
                     prompts/email_to_case.md), prüft aber jeden Wert gegen die
                     erlaubten Listen und fällt sonst auf die Regeln zurück.

Wichtigste Regel: Der Originaltext der E-Mail bleibt unverändert am Vorgang.
Eine KI-Zusammenfassung kann etwas weglassen oder erfinden. Das Original nicht.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from typing import Optional

TYPES = [
    "Preisanfrage / Kalkulation",
    "Auftrag (Neu)",
    "Datenlieferung",
    "Reklamation",
    "Status-Nachfrage",
    "Rechnung / Admin",
    "Sonstiges",
]
STATUSES = ["Neu", "In Bearbeitung", "Wartet auf Kunde", "Wartet auf Intern", "Erledigt"]
PRIORITIES = ["Niedrig", "Normal", "Hoch", "Kritisch"]
SENTIMENTS = ["Positiv", "Neutral", "Negativ"]
ATTACHMENTS = ["Keine Dateien", "Anhang vorhanden", "Download-Link"]

# Wer bekommt welchen Vorgang? Rollen statt Namen, damit es übertragbar bleibt.
OWNER_BY_TYPE = {
    "Reklamation": "Geschäftsführung",
    "Preisanfrage / Kalkulation": "Kalkulation",
    "Datenlieferung": "Arbeitsvorbereitung",
    "Rechnung / Admin": "Buchhaltung",
}
DEFAULT_OWNER = "Info-Zentrale"

# Antwortfrist in Tagen je Priorität (nicht der Liefertermin der Ware).
RESPONSE_DAYS = {"Kritisch": 0, "Hoch": 1, "Normal": 2, "Niedrig": 3}

TYPE_KEYWORDS = [
    ("Reklamation", ["reklamation", "mangel", "fehlerhaft", "beschädigt", "falsch geliefert", "beschwerde", "unzufrieden"]),
    ("Status-Nachfrage", ["wann kommt", "status", "liefertermin", "schon fertig", "sendungsverfolgung", "wo bleibt"]),
    ("Rechnung / Admin", ["rechnung", "mahnung", "gutschrift", "zahlungsziel", "lieferschein"]),
    ("Preisanfrage / Kalkulation", ["angebot", "preis", "kalkulation", "was kostet", "kostenvoranschlag", "anfrage"]),
    ("Datenlieferung", ["anbei die daten", "druckdaten", "daten anbei", "zeichnung anbei", "finale datei", "korrigierte datei"]),
    ("Auftrag (Neu)", ["bestellen", "bestellung", "beauftragen", "auftrag erteilen", "hiermit bestelle"]),
]
URGENT_WORDS = ["eilt", "dringend", "sofort", "heute noch", "asap", "stopp", "notfall"]
SOON_WORDS = ["morgen", "kurzfristig", "schnellstmöglich", "zeitnah"]
NEGATIVE_WORDS = ["ärgerlich", "enttäuscht", "inakzeptabel", "unzufrieden", "beschwerde", "zum wiederholten mal", "mangel"]
POSITIVE_WORDS = ["vielen dank", "super", "perfekt", "sehr zufrieden", "top", "großartig"]
LINK_HOSTS = ["wetransfer", "we.tl", "dropbox", "drive.google", "onedrive", "sharepoint"]

JOB_NUMBER = re.compile(r"\b[A-Z]{0,3}\d{2}-\d{4}\b")
DATE_DE = re.compile(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4}|\d{2})?")
WEEKDAYS = ["montag", "dienstag", "mittwoch", "donnerstag", "freitag", "samstag", "sonntag"]


@dataclass
class Case:
    subject: str
    original_body: str  # unveränderter Text, niemals überschreiben
    description: str  # Zusammenfassung (Regel oder KI)
    type: str
    sentiment: str
    status: str
    priority: str
    owner: str
    due_date: str
    job_number: str
    wish_date: str
    attachment_status: str
    sender: str
    received: str

    def to_dict(self) -> dict:
        return asdict(self)


def _contains(text: str, words: list) -> bool:
    return any(word in text for word in words)


def detect_type(text: str) -> str:
    for case_type, words in TYPE_KEYWORDS:
        if _contains(text, words):
            return case_type
    return "Sonstiges"


def detect_priority(text: str, case_type: str) -> str:
    if _contains(text, URGENT_WORDS):
        return "Kritisch"
    if case_type == "Reklamation" or _contains(text, SOON_WORDS):
        return "Hoch"
    return "Normal"


def detect_sentiment(text: str) -> str:
    if _contains(text, NEGATIVE_WORDS):
        return "Negativ"
    if _contains(text, POSITIVE_WORDS):
        return "Positiv"
    return "Neutral"


def detect_attachment(text: str, attachments: int) -> str:
    if attachments > 0:
        return "Anhang vorhanden"
    if _contains(text, LINK_HOSTS):
        return "Download-Link"
    return "Keine Dateien"


def detect_wish_date(text: str, received: date) -> Optional[date]:
    """Findet "bis 12.05." oder "bis Freitag". Das ist der Wunschtermin des Kunden."""
    match = DATE_DE.search(text)
    if match:
        day, month = int(match.group(1)), int(match.group(2))
        year = match.group(3)
        year = received.year if not year else int(year) + (2000 if len(year) == 2 else 0)
        try:
            found = date(year, month, day)
        except ValueError:
            found = None
        if found:
            if not match.group(3) and found < received:
                found = date(year + 1, month, day)
            return found
    for index, name in enumerate(WEEKDAYS):
        if f"bis {name}" in text or f"am {name}" in text:
            ahead = (index - received.weekday()) % 7 or 7
            return received + timedelta(days=ahead)
    return None


def summarize(body: str, limit: int = 160) -> str:
    """Notlösung ohne KI: der erste inhaltliche Satz."""
    for line in body.splitlines():
        line = line.strip()
        if len(line) > 25 and not line.lower().startswith(("hallo", "guten", "sehr geehrte", "liebe", "moin")):
            return line[:limit]
    return body.strip()[:limit]


def classify(sender: str, subject: str, body: str, received: datetime, attachments: int = 0) -> Case:
    text = f"{subject}\n{body}".lower()
    case_type = detect_type(text)
    priority = detect_priority(text, case_type)
    match = JOB_NUMBER.search(f"{subject} {body}")
    wish = detect_wish_date(text, received.date())
    return Case(
        subject=subject,
        original_body=body,
        description=summarize(body),
        type=case_type,
        sentiment=detect_sentiment(text),
        status="Neu",
        priority=priority,
        owner=OWNER_BY_TYPE.get(case_type, DEFAULT_OWNER),
        due_date=(received.date() + timedelta(days=RESPONSE_DAYS[priority])).isoformat(),
        job_number=match.group(0) if match else "",
        wish_date=wish.isoformat() if wish else "",
        attachment_status=detect_attachment(text, attachments),
        sender=sender,
        received=received.isoformat(),
    )


def from_llm_json(raw: str, sender: str, subject: str, body: str, received: datetime, attachments: int = 0) -> Case:
    """Übernimmt KI-Ergebnisse nur, wenn sie zu den erlaubten Werten passen."""
    case = classify(sender, subject, body, received, attachments)
    try:
        data = json.loads(raw)
    except (TypeError, ValueError):
        return case
    if not isinstance(data, dict):
        return case
    if data.get("type") in TYPES:
        case.type = data["type"]
        case.owner = OWNER_BY_TYPE.get(case.type, DEFAULT_OWNER)
    if data.get("priority") in PRIORITIES:
        case.priority = data["priority"]
        case.due_date = (received.date() + timedelta(days=RESPONSE_DAYS[case.priority])).isoformat()
    if data.get("sentiment") in SENTIMENTS:
        case.sentiment = data["sentiment"]
    summary = data.get("summary")
    if isinstance(summary, str) and summary.strip():
        case.description = summary.strip()[:300]
    number = data.get("job_number")
    # Auftragsnummern nur übernehmen, wenn sie wirklich in der E-Mail stehen.
    if isinstance(number, str) and number and number in f"{subject} {body}":
        case.job_number = number
    return case


def needs_escalation(case: Case) -> bool:
    return case.priority == "Kritisch" or (case.type == "Reklamation" and case.sentiment == "Negativ")
