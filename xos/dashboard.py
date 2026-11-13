"""Führt alle Bausteine zu einer Übersicht zusammen. Die Darstellung liegt in page.py."""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path

from . import capacity, cases, followup, reactivation, shipping, status
from .jobticket import read_folder, work_centres
from .page import render_html  # noqa: F401  (bleibt hier erreichbar)


def build(data_dir: Path, today: date, origin: str = "Werkstraße 1, 50999 Köln") -> dict:
    data_dir = Path(data_dir)
    jobs, unreadable = read_folder(data_dir / "jobs")
    events = status.EventLog(data_dir / "status_events.jsonl").read()
    job_status, rejected = status.replay(events)
    monday = today - timedelta(days=today.weekday())
    calendar = capacity.week_calendar(jobs, work_centres(jobs), monday)

    def state(job):
        return job_status.get(job.number, status.OFFEN)

    open_jobs = [j for j in jobs if state(j) not in (status.VERSENDET,)]
    overdue = [j for j in open_jobs if j.delivery_date and j.delivery_date < today and state(j) != status.FERTIG]
    due_soon = [j for j in open_jobs if j.delivery_date and 0 <= (j.delivery_date - today).days <= 2]
    problems = [j for j in jobs if state(j) == status.PROBLEM]

    with (data_dir / "emails.json").open(encoding="utf-8") as handle:
        emails = json.load(handle)
    case_list = [
        cases.classify(m["von"], m["betreff"], m["text"], datetime.fromisoformat(m["eingang"]), m.get("anhaenge", 0))
        for m in emails
    ]
    offers = followup.load_offers(data_dir / "offers.csv")
    segments = reactivation.segment(reactivation.load_customers(data_dir / "customers.csv"), today)

    return {
        "today": today.isoformat(),
        "kpis": {
            "open_jobs": len(open_jobs),
            "due_soon": len(due_soon),
            "overdue": len(overdue),
            "problems": len(problems),
            "bottleneck": capacity.bottleneck(calendar),
        },
        "jobs": [
            {
                "number": j.number,
                "customer": j.customer,
                "product": j.product_type,
                "clerk": j.clerk,
                "delivery": j.delivery_date.isoformat() if j.delivery_date else "",
                "status": state(j),
                "scan_url": status.scan_url("https://xos.example", j.number),
            }
            for j in jobs
        ],
        "calendar": calendar,
        "status_counts": {name: sum(1 for j in jobs if state(j) == name) for name in status.STATUSES},
        "events": sorted(events, key=lambda x: x["zeit"], reverse=True)[:15],
        "tours": shipping.plan(jobs, job_status, origin),
        "cases": [c.to_dict() for c in case_list],
        "escalations": [c.subject for c in case_list if cases.needs_escalation(c)],
        "reminders": followup.due_reminders(offers, today),
        "open_offers_by_clerk": followup.open_offers_by_clerk(offers),
        "reactivation": {
            "inactive": len(segments["inactive"]),
            "active": len(segments["active"]),
            "blocked": len(segments["blocked"]),
            "top": [
                {"firma": c["firma"], "klasse": c["klasse"], "tage_inaktiv": c["tage_inaktiv"]}
                for c in segments["inactive"][:5]
            ],
        },
        "unreadable_files": unreadable,
        "rejected_scans": rejected,
    }
