"""Führt alle Bausteine zu einer Übersicht zusammen (JSON + eine HTML-Seite)."""
from __future__ import annotations

import html
import json
from datetime import date, datetime, timedelta
from pathlib import Path

from . import capacity, cases, followup, reactivation, shipping, status
from .jobticket import read_folder, work_centres

LIGHT_COLORS = {"gruen": "#dfe9e2", "gelb": "#f1e6c4", "rot": "#edc9c4"}


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


def _table(headers: list, rows: list) -> str:
    head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def render_html(data: dict) -> str:
    e = html.escape
    k = data["kpis"]
    b = k["bottleneck"] or {}
    cards = [
        ("Offene Aufträge", k["open_jobs"]),
        ("Bald fällig", k["due_soon"]),
        ("Überfällig", k["overdue"]),
        ("Problemaufträge", k["problems"]),
        ("Engpass", f"{e(b.get('work_centre', '–'))} · {int(b.get('utilization', 0) * 100)} %"),
    ]
    card_html = "".join(f"<div class='card'><span>{e(t)}</span><b>{v}</b></div>" for t, v in cards)

    days = [c["day"][8:] + "." + c["day"][5:7] + "." for c in data["calendar"][0]["cells"]] if data["calendar"] else []
    cal_rows = []
    for row in data["calendar"]:
        cells = [e(row["name"])]
        for cell in row["cells"]:
            color = LIGHT_COLORS[cell["light"]] if cell["minutes"] else "transparent"
            cells.append(f"<span class='cell' style='background:{color}'>{int(cell['utilization'] * 100)} %</span>")
        cal_rows.append(cells)

    job_rows = [[e(j["number"]), e(j["customer"]), e(j["product"]), e(j["delivery"]), e(j["status"])] for j in data["jobs"]]
    case_rows = [[e(c["subject"]), e(c["type"]), e(c["priority"]), e(c["owner"]), e(c["due_date"]), e(c["job_number"])] for c in data["cases"]]
    tour_rows = [
        [e(t["region"]), len(t["stops"]), t["job_count"], f"<a href='{e(t['maps_url'])}'>Route öffnen</a>"] for t in data["tours"]
    ]
    reminder_rows = [[e(r["offer"]), e(r["customer"]), e(r["clerk"]), r["days_waiting"]] for r in data["reminders"]]
    r = data["reactivation"]

    return f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>XOS Demo-Übersicht</title>
<style>
:root {{ --bg:#f2f2f3; --text:#1d1f20; --accent:#5980a6; --line:#c5ccd3; }}
body {{ margin:0; padding:24px; background:var(--bg); color:var(--text); font:15px/1.45 system-ui, sans-serif; }}
h1 {{ margin:0 0 4px; font-size:28px; }} h2 {{ margin:32px 0 8px; font-size:18px; color:var(--accent); }}
p {{ margin:0 0 16px; max-width:70ch; }}
.cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:12px; }}
.card {{ border:1px solid var(--line); padding:12px; }} .card span {{ display:block; font-size:13px; }} .card b {{ font-size:22px; }}
.scroll {{ overflow-x:auto; }} table {{ border-collapse:collapse; width:100%; }}
th, td {{ text-align:left; padding:6px 10px; border-bottom:1px solid var(--line); white-space:nowrap; }}
th {{ font-size:13px; color:var(--accent); }} .cell {{ display:block; padding:2px 6px; text-align:right; font-variant-numeric:tabular-nums; }}
a {{ color:var(--accent); }}
</style></head><body>
<h1>XOS Demo-Übersicht</h1>
<p>Stand {e(data['today'])}. Alle Daten sind synthetisch. Die Seite zeigt, was aus einem XML-Export, QR-Scans, E-Mails und einer Kundenliste entsteht.</p>
<div class="cards">{card_html}</div>
<h2>Maschinen-Kalender (Auslastung je Kostenstelle und Tag)</h2>
<div class="scroll">{_table(['Kostenstelle'] + days, cal_rows)}</div>
<h2>Aufträge</h2><div class="scroll">{_table(['Auftrag', 'Kunde', 'Produkt', 'Liefertermin', 'Status'], job_rows)}</div>
<h2>Versand-Touren (fertige Aufträge, nach Region gebündelt)</h2>
<div class="scroll">{_table(['Region (PLZ)', 'Stopps', 'Aufträge', 'Google Maps'], tour_rows)}</div>
<h2>Vorgänge aus E-Mails</h2>
<div class="scroll">{_table(['Betreff', 'Art', 'Priorität', 'Zuständig', 'Antwort bis', 'Auftrag'], case_rows)}</div>
<h2>Angebote nachfassen</h2>
<div class="scroll">{_table(['Angebot', 'Kunde', 'Sachbearbeitung', 'Tage ohne Antwort'], reminder_rows)}</div>
<h2>Kundenreaktivierung</h2>
<p>{r['inactive']} inaktive Kunden mit Einwilligung, {r['active']} aktive, {r['blocked']} ohne Werbeeinwilligung (werden nicht angeschrieben).</p>
</body></html>
"""
