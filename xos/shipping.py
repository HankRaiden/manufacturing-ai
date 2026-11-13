"""Säule 1, Schritt 4: Versand-Planer.

Sobald Aufträge "Fertig" sind, werden Lieferungen an dieselbe Adresse
zusammengefasst und nach Region gebündelt. Daraus entsteht eine Tour für den
Fahrer, die sich mit einem Klick in Google Maps öffnen lässt.

Zwei Stufen:
1. maps_url()            – ohne API-Schlüssel, Reihenfolge wie übergeben.
2. routes_api_request()  – Anfrage an die Google Routes API mit optimierter
                           Reihenfolge. Braucht einen eigenen API-Schlüssel und
                           ist hier nur als Anfrage-Aufbau enthalten, nicht als
                           getesteter Live-Aufruf.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable
from urllib.parse import urlencode

from .jobticket import Job
from .status import FERTIG, VERSANDBEREIT

MAX_WAYPOINTS_URL = 9  # Google-Maps-Links erlauben nur wenige Zwischenstopps


def ready_jobs(jobs: Iterable[Job], status: dict) -> list:
    return [job for job in jobs if status.get(job.number) in (FERTIG, VERSANDBEREIT)]


def consolidate(jobs: Iterable[Job]) -> list:
    """Mehrere Aufträge an dieselbe Adresse werden ein Stopp."""
    stops = {}
    for job in jobs:
        key = (job.delivery_name.lower(), job.delivery_street.lower(), job.delivery_zip)
        stop = stops.setdefault(
            key,
            {
                "name": job.delivery_name,
                "street": job.delivery_street,
                "zip": job.delivery_zip,
                "city": job.delivery_city,
                "jobs": [],
                "due": None,
            },
        )
        stop["jobs"].append(job.number)
        if job.delivery_date and (stop["due"] is None or job.delivery_date.isoformat() < stop["due"]):
            stop["due"] = job.delivery_date.isoformat()
    return list(stops.values())


def group_by_region(stops: Iterable[dict], digits: int = 2) -> dict:
    """Bündelt Stopps nach den ersten Ziffern der Postleitzahl."""
    regions = defaultdict(list)
    for stop in stops:
        regions[stop["zip"][:digits] or "??"].append(stop)
    # innerhalb der Region nach PLZ sortieren: einfache, nachvollziehbare Reihenfolge
    return {region: sorted(items, key=lambda s: s["zip"]) for region, items in sorted(regions.items())}


def address(stop: dict) -> str:
    return f"{stop['street']}, {stop['zip']} {stop['city']}"


def maps_url(origin: str, stops: list) -> str:
    """Link, der die Tour in Google Maps öffnet (Start und Ziel = Betrieb)."""
    if not stops:
        return ""
    params = {"api": "1", "origin": origin, "destination": origin, "travelmode": "driving"}
    params["waypoints"] = "|".join(address(stop) for stop in stops[:MAX_WAYPOINTS_URL])
    return "https://www.google.com/maps/dir/?" + urlencode(params)


def routes_api_request(origin: str, stops: list) -> dict:
    """Aufbau einer Anfrage an die Google Routes API mit optimierter Stopp-Reihenfolge.

    Senden als POST an https://routes.googleapis.com/directions/v2:computeRoutes
    mit den Headern X-Goog-Api-Key und X-Goog-FieldMask. Die optimierte Reihenfolge
    steht in der Antwort unter routes[0].optimizedIntermediateWaypointIndex.
    Bitte gegen die aktuelle Google-Dokumentation prüfen, bevor es produktiv geht.
    """
    return {
        "url": "https://routes.googleapis.com/directions/v2:computeRoutes",
        "headers": {
            "X-Goog-Api-Key": "<EIGENER_API_SCHLUESSEL>",
            "X-Goog-FieldMask": "routes.optimizedIntermediateWaypointIndex,routes.distanceMeters,routes.duration",
        },
        "body": {
            "origin": {"address": origin},
            "destination": {"address": origin},
            "intermediates": [{"address": address(stop)} for stop in stops],
            "travelMode": "DRIVE",
            "optimizeWaypointOrder": True,
        },
    }


def plan(jobs: Iterable[Job], status: dict, origin: str) -> list:
    """Eine Tour pro Region, mit Stopps, Aufträgen und Maps-Link."""
    tours = []
    for region, stops in group_by_region(consolidate(ready_jobs(jobs, status))).items():
        tours.append(
            {
                "region": region,
                "stops": stops,
                "job_count": sum(len(stop["jobs"]) for stop in stops),
                "maps_url": maps_url(origin, stops),
            }
        )
    return tours
