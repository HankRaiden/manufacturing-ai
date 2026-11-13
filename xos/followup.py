"""Säule 3: Angebote automatisch nachfassen.

Reagiert ein Kunde nach drei Tagen nicht auf ein Angebot, geht eine freundliche
Erinnerung raus. Niemand muss daran denken.
"""
from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

REMIND_AFTER_DAYS = 3
MAX_REMINDERS = 2

TEMPLATE = (
    "Guten Tag {contact},\n\n"
    "vor ein paar Tagen haben wir Ihnen unser Angebot {offer} geschickt. "
    "Gibt es dazu noch Fragen, oder sollen wir etwas anpassen?\n\n"
    "Viele Grüße\n{clerk}"
)


def load_offers(path: Path) -> list:
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def due_reminders(offers: list, today: date) -> list:
    """Offene Angebote ohne Antwort, bei denen die Frist abgelaufen ist."""
    due = []
    for offer in offers:
        if offer["status"] != "offen" or offer.get("antwort_am"):
            continue
        reminders = int(offer.get("erinnerungen") or 0)
        if reminders >= MAX_REMINDERS:
            continue
        last_touch = date.fromisoformat(offer.get("letzte_erinnerung") or offer["gesendet_am"])
        waiting = (today - last_touch).days
        if waiting >= REMIND_AFTER_DAYS:
            due.append(
                {
                    "offer": offer["angebot"],
                    "customer": offer["kunde"],
                    "clerk": offer["sachbearbeiter"],
                    "days_waiting": (today - date.fromisoformat(offer["gesendet_am"])).days,
                    "reminder_no": reminders + 1,
                    "text": TEMPLATE.format(contact=offer["ansprechpartner"], offer=offer["angebot"], clerk=offer["sachbearbeiter"]),
                }
            )
    return due


def open_offers_by_clerk(offers: list) -> dict:
    counts = {}
    for offer in offers:
        if offer["status"] == "offen" and not offer.get("antwort_am"):
            counts[offer["sachbearbeiter"]] = counts.get(offer["sachbearbeiter"], 0) + 1
    return dict(sorted(counts.items()))
