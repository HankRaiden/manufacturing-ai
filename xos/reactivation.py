"""Säule 2: Bestandskunden wieder aktivieren (Database Reactivation).

Viele Betriebe haben tausende Kunden in der Datenbank und sprechen kaum einen
davon aktiv an. Hier werden Kunden nach Umsatz in A/B/C eingeteilt und die
inaktiven herausgefiltert. Das Ergebnis ist die Liste für eine Kampagne.
"""
from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

INACTIVE_AFTER_DAYS = 365
A_SHARE, B_SHARE = 0.80, 0.95  # A = die Kunden, die 80 % des Umsatzes bringen


def load_customers(path: Path) -> list:
    with Path(path).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["umsatz_3_jahre"] = float(row["umsatz_3_jahre"] or 0)
    return rows


def classify_abc(customers: list) -> list:
    total = sum(c["umsatz_3_jahre"] for c in customers) or 1.0
    running = 0.0
    for customer in sorted(customers, key=lambda c: c["umsatz_3_jahre"], reverse=True):
        running += customer["umsatz_3_jahre"]
        share = running / total
        customer["klasse"] = "A" if share <= A_SHARE else "B" if share <= B_SHARE else "C"
    return customers


def segment(customers: list, today: date) -> dict:
    """Wer wird angeschrieben? Nur Kunden mit Einwilligung und ohne Sperrvermerk."""
    classify_abc(customers)
    inactive, active, blocked = [], [], []
    for customer in customers:
        days = (today - date.fromisoformat(customer["letzter_auftrag"])).days
        customer["tage_inaktiv"] = days
        if customer.get("werbung_erlaubt", "").lower() != "ja":
            blocked.append(customer)
        elif days > INACTIVE_AFTER_DAYS:
            inactive.append(customer)
        else:
            active.append(customer)
    # zuerst die wertvollsten Schläfer
    inactive.sort(key=lambda c: ("ABC".index(c["klasse"]), -c["umsatz_3_jahre"]))
    return {"inactive": inactive, "active": active, "blocked": blocked}


def potential(contacted: int, reactivation_rate: float, avg_order_value: float) -> dict:
    """Vorsichtige Hochrechnung. Eine Schätzung, kein Versprechen."""
    reactivated = round(contacted * reactivation_rate)
    return {
        "contacted": contacted,
        "reactivation_rate": reactivation_rate,
        "reactivated": reactivated,
        "avg_order_value": avg_order_value,
        "revenue_potential": round(reactivated * avg_order_value),
    }
