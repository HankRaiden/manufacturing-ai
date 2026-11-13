"""Was kostet der Status quo? Ein einfacher, ehrlicher Rechner.

Alle Werte sind Annahmen. Die Voreinstellungen sind Beispielwerte für einen
mittelständischen Betrieb. Bitte mit eigenen Zahlen füllen: Die Rechnung ist
nur so gut wie die Annahmen, und sie beschreibt ein Potenzial, kein Ergebnis.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class Assumptions:
    # Suchaufwand im Büro
    office_staff: int = 7
    search_minutes_per_day: float = 40
    internal_hourly_rate: float = 80
    working_days: int = 220
    # Verpasste Anfragen
    missed_orders_per_week: float = 1
    contribution_per_order: float = 2000
    weeks: int = 50
    # Maschinen-Leerlauf durch fehlende Planung
    idle_hours_per_week: float = 1
    machine_hourly_rate: float = 300
    # Versand ohne Bündelung
    shipping_saving_per_day: float = 100


def status_quo_cost(a: Assumptions = None) -> dict:
    a = a or Assumptions()
    search = a.office_staff * (a.search_minutes_per_day / 60) * a.internal_hourly_rate * a.working_days
    leads = a.missed_orders_per_week * a.contribution_per_order * a.weeks
    idle = a.idle_hours_per_week * a.machine_hourly_rate * a.weeks
    shipping = a.shipping_saving_per_day * a.working_days
    return {
        "assumptions": asdict(a),
        "search_effort": round(search),
        "missed_orders": round(leads),
        "machine_idle": round(idle),
        "shipping": round(shipping),
        "total_per_year": round(search + leads + idle + shipping),
    }


def payback_months(one_off_investment: float, yearly_cost_of_status_quo: float, realised_share: float = 1.0) -> float:
    """Monate bis zur Amortisation. realised_share = wie viel vom Potenzial wirklich gehoben wird."""
    saving = yearly_cost_of_status_quo * realised_share
    return round(one_off_investment / saving * 12, 1) if saving else float("inf")
