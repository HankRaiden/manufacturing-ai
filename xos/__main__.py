"""Kommandozeile.

    python3 -m xos demo            # rechnet die Beispieldaten durch, schreibt out/dashboard.html
    python3 -m xos roi             # Kosten des Status quo mit Beispielannahmen
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from . import dashboard, roi

ROOT = Path(__file__).resolve().parent.parent


def cmd_demo(args) -> None:
    data = dashboard.build(Path(args.data), date.fromisoformat(args.today))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "dashboard.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "dashboard.html").write_text(dashboard.render_html(data), encoding="utf-8")
    k = data["kpis"]
    b = k["bottleneck"] or {}
    print(f"Stand {data['today']}")
    print(f"  Aufträge offen: {k['open_jobs']} | bald fällig: {k['due_soon']} | überfällig: {k['overdue']} | Problem: {k['problems']}")
    print(f"  Engpass: {b.get('work_centre', '–')} am {b.get('day', '–')} mit {int(b.get('utilization', 0) * 100)} %")
    print(f"  Versand-Touren: {len(data['tours'])} | Vorgänge aus E-Mails: {len(data['cases'])} | Eskalationen: {len(data['escalations'])}")
    print(f"  Angebote nachfassen: {len(data['reminders'])} | inaktive Kunden: {data['reactivation']['inactive']}")
    print(f"  Geschrieben: {out / 'dashboard.html'}")


def cmd_roi(args) -> None:
    result = roi.status_quo_cost()
    labels = [
        ("search_effort", "Suchaufwand im Büro"),
        ("missed_orders", "Verpasste Anfragen"),
        ("machine_idle", "Maschinen-Leerlauf"),
        ("shipping", "Versand ohne Bündelung"),
        ("total_per_year", "Summe pro Jahr"),
    ]
    print("Kosten des Status quo (Beispielannahmen, bitte eigene Zahlen einsetzen):")
    for key, label in labels:
        print(f"  {label:<26} {result[key]:>10,.0f} €".replace(",", "."))


def main() -> None:
    parser = argparse.ArgumentParser(prog="xos", description="XOS Referenz-Implementierung")
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo", help="Beispieldaten durchrechnen")
    demo.add_argument("--data", default=str(ROOT / "data" / "sample"))
    demo.add_argument("--out", default=str(ROOT / "out"))
    demo.add_argument("--today", default="2026-03-11")
    demo.set_defaults(func=cmd_demo)
    sub.add_parser("roi", help="Kosten des Status quo").set_defaults(func=cmd_roi)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
