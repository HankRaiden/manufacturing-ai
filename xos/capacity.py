"""Säule 1, Schritt 2: Maschinen-Kalender und Auslastung.

Aus den geplanten Zeiten der Arbeitsgänge wird pro Kostenstelle und Tag die
Auslastung berechnet. Das ersetzt die Plantafel an der Wand und die Frage
"Ist die Maschine morgen frei?".
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Iterable

from .jobticket import Job

CAPACITY_MIN_PER_DAY = 480  # eine Schicht; pro Kostenstelle überschreibbar
GREEN_BELOW = 0.70
RED_ABOVE = 0.90


def traffic_light(utilization: float) -> str:
    if utilization > RED_ABOVE:
        return "rot"
    if utilization >= GREEN_BELOW:
        return "gelb"
    return "gruen"


def load_by_day(jobs: Iterable[Job]) -> dict:
    """{(kostenstelle, tag): {"minutes": float, "jobs": [auftragsnummern]}}"""
    load = defaultdict(lambda: {"minutes": 0.0, "jobs": []})
    for job in jobs:
        for op in job.operations:
            if op.day is None:
                continue
            cell = load[(op.work_centre_id, op.day)]
            cell["minutes"] += op.minutes
            if job.number not in cell["jobs"]:
                cell["jobs"].append(job.number)
    return dict(load)


def week_calendar(jobs: Iterable[Job], centres: dict, monday: date, capacities: dict = None) -> list:
    """Wochenansicht Mo–So: eine Zeile pro Kostenstelle, eine Zelle pro Tag."""
    capacities = capacities or {}
    load = load_by_day(jobs)
    days = [monday + timedelta(days=i) for i in range(7)]
    rows = []
    for centre_id, centre_name in centres.items():
        capacity = capacities.get(centre_id, CAPACITY_MIN_PER_DAY)
        cells = []
        for day in days:
            cell = load.get((centre_id, day), {"minutes": 0.0, "jobs": []})
            utilization = cell["minutes"] / capacity if capacity else 0.0
            cells.append(
                {
                    "day": day.isoformat(),
                    "minutes": round(cell["minutes"]),
                    "capacity": capacity,
                    "utilization": round(utilization, 2),
                    "light": traffic_light(utilization),
                    "jobs": cell["jobs"],
                }
            )
        rows.append({"id": centre_id, "name": centre_name, "cells": cells})
    return rows


def bottleneck(calendar: list):
    """Die am stärksten ausgelastete Zelle der Woche (Kostenstelle + Tag)."""
    worst = None
    for row in calendar:
        for cell in row["cells"]:
            if worst is None or cell["utilization"] > worst["utilization"]:
                worst = {"work_centre": row["name"], **cell}
    return worst
