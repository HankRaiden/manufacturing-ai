"""Die Demo-Oberfläche als eine einzige HTML-Seite.

Aufbau und Aussehen folgen der ursprünglichen Demo: Symbolleiste links, Kopfzeile
mit Reitern, weiße Karten auf hellgrauem Grund. Die Seite kommt ohne externe
Dateien aus und lässt sich direkt im Browser öffnen.
"""
from __future__ import annotations

import html
from datetime import date

e = html.escape
WEEKDAYS = ["Mo.", "Di.", "Mi.", "Do.", "Fr.", "Sa.", "So."]

ICONS = {
    "home": "M3 11l9-8 9 8v9a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z",
    "grid": "M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z",
    "chat": "M4 5h16v11H9l-5 4z",
    "calendar": "M4 6h16v14H4zM4 10h16M8 3v5M16 3v5",
    "mail": "M3 6h18v12H3zM3 7l9 6 9-6",
    "users": "M9 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zM2.5 20a6.5 6.5 0 0 1 13 0M17 11a3 3 0 1 0 0-6M21.5 20a5.5 5.5 0 0 0-4-5.3",
    "chart": "M4 20V10M10 20V4M16 20v-7M22 20H2",
    "send": "M21 3L3 10l7 3 3 7z",
    "star": "M12 3l2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2l1.1-6.2L3 9.6l6.2-.9z",
    "settings": "M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6zM12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2",
    "alert": "M12 3l10 18H2zM12 10v5M12 18v.5",
    "clock": "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 7v5l3 2",
    "truck": "M2 7h11v9H2zM13 10h4l4 3v3h-8zM6 19a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM17 19a2 2 0 1 0 0-4 2 2 0 0 0 0 4z",
    "search": "M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zM20 20l-4-4",
    "package": "M3 8l9-5 9 5v8l-9 5-9-5zM3 8l9 5 9-5M12 13v8",
    "arrow": "M5 12h14M13 6l6 6-6 6",
    "pin": "M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11zM12 8a2 2 0 1 0 0 4 2 2 0 0 0 0-4z",
    "gauge": "M4 18a9 9 0 1 1 16 0M12 13l4-5",
    "inbox": "M3 13l3-8h12l3 8v6H3zM3 13h5l1 3h6l1-3h5",
}

PILL_CLASS = {
    "Offen": "blue", "In Produktion": "cyan", "Fertig": "green", "Versandbereit": "amber",
    "Versendet": "gray", "Problem": "red",
    "Kritisch": "red", "Hoch": "amber", "Normal": "gray", "Niedrig": "gray",
}
STAGE_COLORS = {
    "Offen": "#3b63e6", "In Produktion": "#52b1d3", "Fertig": "#8a5cf0",
    "Versandbereit": "#dd5599", "Versendet": "#55b683", "Problem": "#e0504c",
}

CSS = """
:root { --bg:#f3f4f6; --card:#fff; --line:#e5e7eb; --text:#111827; --muted:#6b7280; --blue:#2563eb; --blue-soft:#e8effd;
  --green:#16a34a; --green-soft:#edf8f0; --amber:#d39a1c; --amber-soft:#fbf5e4; --red:#dc2626; --red-soft:#fceaea; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text); font:15px/1.45 Inter, -apple-system, "Segoe UI", system-ui, sans-serif; }
svg.i { width:18px; height:18px; fill:none; stroke:currentColor; stroke-width:1.6; stroke-linecap:round; stroke-linejoin:round; flex:none; }
.rail { position:fixed; inset:0 auto 0 0; width:56px; background:#fff; border-right:1px solid var(--line); display:flex; flex-direction:column; align-items:center; gap:16px; padding:70px 0 16px; color:#4b5563; }
.rail .on { background:#eef0f3; border-radius:8px; padding:8px; color:#111827; } .rail .end { margin-top:auto; }
.top { position:fixed; inset:0 0 auto 56px; height:52px; background:#fff; border-bottom:1px solid var(--line); display:flex; align-items:center; justify-content:flex-end; gap:10px; padding:0 14px; z-index:2; }
.dot { width:32px; height:32px; border-radius:50%; display:grid; place-items:center; color:#fff; font-size:12px; font-weight:600; }
.app { margin-left:56px; padding-top:52px; }
.head { background:#fff; border-bottom:1px solid var(--line); display:flex; align-items:center; gap:22px; padding:12px 24px; flex-wrap:wrap; }
.brand { color:var(--blue); font-weight:700; font-size:20px; letter-spacing:.01em; }
.tabs { display:flex; gap:4px; flex-wrap:wrap; }
.tab { border:0; background:none; font:inherit; color:#374151; padding:8px 14px; border-radius:6px; cursor:pointer; }
.tab:hover { background:#f3f4f6; } .tab[aria-selected=true] { background:var(--blue-soft); color:var(--blue); font-weight:500; }
.tab:focus-visible, .btn:focus-visible, input:focus-visible, select:focus-visible { outline:2px solid var(--blue); outline-offset:2px; }
.btn { margin-left:auto; background:var(--blue); color:#fff; border:0; border-radius:6px; padding:9px 16px; font:inherit; font-weight:500; text-decoration:none; display:inline-flex; align-items:center; gap:8px; }
.btn.green { background:var(--green); margin-left:0; } .btn.ghost { background:#fff; color:var(--text); border:1px solid var(--line); }
main { padding:24px; max-width:1500px; } section[hidden] { display:none; }
h1 { font-size:22px; margin:0; } .sub { color:var(--muted); margin:2px 0 18px; } h2 { font-size:16px; margin:26px 0 10px; }
.cards { display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:16px; }
.cards.six { grid-template-columns:repeat(auto-fit,minmax(185px,1fr)); }
.card { background:var(--card); border:1px solid var(--line); border-radius:8px; padding:16px 18px; }
.kpi span { display:flex; align-items:center; gap:8px; color:#374151; } .kpi b { display:block; font-size:22px; margin-top:6px; }
.kpi.warn b { color:#c2761c; } .kpi.bad b { color:var(--red); }
.bar { height:5px; background:#e5e7eb; border-radius:3px; overflow:hidden; } .bar i { display:block; height:100%; border-radius:3px; }
.gruen .bar i { background:#4bb463; } .gelb .bar i { background:#dba92c; } .rot .bar i { background:#dc4a45; }
.machine small, .muted { color:var(--muted); } .machine .bar { margin:10px 0 8px; } .machine small { white-space:nowrap; }
.mrow { display:flex; justify-content:space-between; gap:8px; } .gruen .pct { color:var(--green); } .gelb .pct { color:var(--amber); } .rot .pct { color:var(--red); }
.filters { display:flex; gap:10px; flex-wrap:wrap; margin-bottom:12px; }
.filters input, .filters select { font:inherit; padding:9px 12px; border:1px solid var(--line); border-radius:6px; background:#fff; color:var(--text); }
.filters input { flex:1 1 280px; max-width:440px; }
.table { background:#fff; border:1px solid var(--line); border-radius:8px; overflow-x:auto; }
table { border-collapse:collapse; width:100%; } th, td { text-align:left; padding:13px 14px; white-space:nowrap; }
th { font-weight:500; color:#4b5563; border-bottom:1px solid var(--line); } td { border-top:1px solid #f0f1f3; } td.strong { font-weight:600; }
.pill { display:inline-block; padding:2px 10px; border-radius:999px; font-size:13px; }
.pill.green { background:var(--green-soft); color:var(--green); } .pill.amber { background:var(--amber-soft); color:#a16207; border:1px solid #f1e3b8; }
.pill.red { background:var(--red-soft); color:var(--red); } .pill.blue { background:var(--blue-soft); color:var(--blue); }
.pill.cyan { background:#e6f5fa; color:#0e7490; } .pill.gray { background:#f1f2f4; color:#4b5563; }
.link { color:var(--blue); text-decoration:none; display:inline-flex; align-items:center; gap:6px; }
.weekbar { display:flex; align-items:center; gap:14px; margin-bottom:14px; } .weekbar b { font-size:20px; }
.plan { background:#fff; border:1px solid var(--line); border-radius:8px; overflow-x:auto; }
.plan table { min-width:980px; table-layout:fixed; } .plan th { text-align:center; } .plan th:first-child { text-align:left; width:190px; }
.plan td { padding:6px; border-top:1px solid #f0f1f3; border-left:1px solid #f0f1f3; } .plan td:first-child { border-left:0; padding:14px; }
.cell { border-radius:8px; padding:8px 10px 10px; text-align:center; background:#f6f7f8; color:var(--muted); }
.cell b { display:block; font-size:16px; margin-top:6px; } .cell small { font-size:13px; color:var(--muted); }
.cell.gruen { background:var(--green-soft); } .cell.gruen b { color:var(--green); }
.cell.gelb { background:var(--amber-soft); } .cell.gelb b { color:var(--amber); }
.cell.rot { background:var(--red-soft); } .cell.rot b { color:var(--red); }
.legend { display:flex; justify-content:flex-end; gap:18px; padding:12px 16px; color:#4b5563; font-size:13px; border-top:1px solid #f0f1f3; }
.legend i { display:inline-block; width:10px; height:10px; border-radius:2px; margin-right:6px; }
.tours { display:grid; grid-template-columns:repeat(auto-fit,minmax(340px,1fr)); gap:16px; align-items:start; }
.tourhead { display:flex; align-items:center; gap:14px; flex-wrap:wrap; background:#eaf1fd; border:1px solid #cfe0fb; border-radius:8px; padding:12px 14px; color:var(--blue); margin-bottom:12px; }
.tourhead .btn { margin-left:auto; }
.stop { background:#fff; border:1px solid #9cc0f5; border-radius:8px; padding:14px 16px; margin-bottom:10px; }
.stop .row { display:flex; align-items:center; justify-content:space-between; gap:10px; }
.num { width:24px; height:24px; border-radius:50%; background:var(--blue); color:#fff; display:inline-grid; place-items:center; font-size:13px; margin-right:8px; }
.addr { background:#f6f7f8; border-radius:6px; padding:10px 12px; margin:10px 0; } .addr b { font-size:18px; margin-right:6px; }
.chart { display:flex; align-items:flex-end; gap:28px; height:240px; padding:8px 8px 0; }
.col { flex:1; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; height:100%; gap:6px; }
.col i { display:block; width:100%; max-width:150px; border-radius:6px 6px 0 0; min-height:2px; } .col b { font-size:14px; } .col span { font-size:13px; text-align:center; }
.note { color:var(--muted); font-size:13px; margin-top:22px; }
@media (max-width:700px) { .rail { display:none; } .top { left:0; } .app { margin-left:0; } main { padding:16px; } .head { padding:12px 16px; } }
"""

JS = """
const tabs = [...document.querySelectorAll('.tab')];
function show(id) {
  tabs.forEach(t => t.setAttribute('aria-selected', String(t.dataset.tab === id)));
  document.querySelectorAll('main > section').forEach(s => { s.hidden = s.id !== id; });
}
const fromHash = () => location.hash.replace('#tab-', '');
tabs.forEach(t => t.addEventListener('click', () => { show(t.dataset.tab); history.replaceState(null, '', '#tab-' + t.dataset.tab); }));
show(tabs.some(t => t.dataset.tab === fromHash()) ? fromHash() : tabs[0].dataset.tab);
const q = document.getElementById('q'), st = document.getElementById('st');
function filter() {
  const needle = q.value.trim().toLowerCase();
  document.querySelectorAll('#orders tbody tr').forEach(r => {
    r.hidden = !(r.textContent.toLowerCase().includes(needle) && (!st.value || r.dataset.status === st.value));
  });
}
q.addEventListener('input', filter); st.addEventListener('change', filter);
"""


def icon(name: str) -> str:
    return f'<svg class="i" viewBox="0 0 24 24" aria-hidden="true"><path d="{ICONS[name]}"/></svg>'


def pill(text: str) -> str:
    return f'<span class="pill {PILL_CLASS.get(text, "gray")}">{e(text)}</span>'


def count(n: int, one: str, many: str) -> str:
    return f"{n} {one if n == 1 else many}"


def de_date(value: str) -> str:
    return date.fromisoformat(value[:10]).strftime("%d.%m.%Y") if value else "–"


def table(headers: list, rows: list) -> str:
    head = "".join(f"<th>{e(h)}</th>" for h in headers)
    body = "".join(f"<tr{attrs}>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>" for attrs, cells in rows)
    return f'<div class="table"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def kpi(icon_name: str, label: str, value, tone: str = "") -> str:
    return f'<div class="card kpi {tone}"><span>{icon(icon_name)}{e(label)}</span><b>{value}</b></div>'


def overview(d: dict) -> str:
    k, b = d["kpis"], d["kpis"]["bottleneck"] or {}
    cards = "".join(
        [
            kpi("package", "Offene Aufträge", k["open_jobs"]),
            kpi("calendar", "Bald fällig", k["due_soon"]),
            kpi("clock", "Überfällig", k["overdue"], "bad" if k["overdue"] else ""),
            kpi("alert", "Problemaufträge", k["problems"], "warn" if k["problems"] else ""),
            kpi("gauge", "Engpass der Woche", f"{e(b.get('work_centre', '–'))}&nbsp;· {int(b.get('utilization', 0) * 100)}&nbsp;%", "bad"),
        ]
    )
    machines = []
    for row in d["calendar"]:
        cell = next((c for c in row["cells"] if c["day"] == d["today"]), None)
        if cell is None:
            continue
        width = min(cell["utilization"], 1) * 100
        machines.append(
            f'<div class="card machine {cell["light"]}"><div class="mrow"><b>{e(row["name"])}</b><b class="pct">{int(cell["utilization"] * 100)}&nbsp;%</b></div>'
            f'<div class="bar"><i style="width:{width:.0f}%"></i></div>'
            f'<small>{cell["minutes"]} / {cell["capacity"]} Min. · {count(len(cell["jobs"]), "Auftrag", "Aufträge")}</small></div>'
        )
    due = [
        ("", [f'<span class="strong">{e(j["number"])}</span>', e(j["customer"]), e(j["product"]), de_date(j["delivery"]), pill(j["status"])])
        for j in sorted(d["jobs"], key=lambda j: j["delivery"])
        if j["status"] not in ("Fertig", "Versandbereit", "Versendet") and j["delivery"]
    ][:6]
    return (
        f'<section id="overview"><h1>Tagesübersicht</h1><p class="sub">Stand {de_date(d["today"])}</p>'
        f'<div class="cards">{cards}</div><h2>Leitmaschinen heute</h2><div class="cards six">{"".join(machines)}</div>'
        "<h2>Bald fällig</h2>"
        + table(["Auftragsnr.", "Kunde", "Produkt", "Liefertermin", "Status"], due)
        + "</section>"
    )


def orders(d: dict) -> str:
    rows = [
        (
            f' data-status="{e(j["status"])}"',
            [f'<span class="strong">{e(j["number"])}</span>', e(j["customer"]), e(j["product"]), de_date(j["delivery"]), pill(j["status"]), e(j["clerk"])],
        )
        for j in d["jobs"]
    ]
    options = "".join(f"<option>{e(s)}</option>" for s in STAGE_COLORS)
    return (
        '<section id="orders"><div class="filters">'
        '<input id="q" type="search" placeholder="Suche nach Auftragsnr., Kunde, Produkt …" aria-label="Aufträge durchsuchen">'
        f'<select id="st" aria-label="Status"><option value="">Alle Status</option>{options}</select></div>'
        + table(["Auftragsnr.", "Kunde", "Produkt", "Liefertermin", "Status", "Sachbearbeitung"], rows)
        + "</section>"
    )


def week(d: dict) -> str:
    if not d["calendar"]:
        return '<section id="week"></section>'
    days = [date.fromisoformat(c["day"]) for c in d["calendar"][0]["cells"]]
    head = "<th>Maschine</th>" + "".join(f"<th>{WEEKDAYS[x.weekday()]} {x.strftime('%d.%m.')}</th>" for x in days)
    body = []
    for row in d["calendar"]:
        cells = [f'<td><b>{e(row["name"])}</b><br><small class="muted">Kostenstelle {e(row["id"])}</small></td>']
        for c in row["cells"]:
            if not c["minutes"]:
                cells.append('<td><div class="cell"><div class="bar"></div><b>–</b><small>&nbsp;</small></div></td>')
                continue
            width = min(c["utilization"], 1) * 100
            cells.append(
                f'<td><div class="cell {c["light"]}"><div class="bar"><i style="width:{width:.0f}%"></i></div>'
                f'<b>{int(c["utilization"] * 100)}%</b><small>{count(len(c["jobs"]), "Auftrag", "Aufträge")}</small></div></td>'
            )
        body.append("<tr>" + "".join(cells) + "</tr>")
    year, kw, _ = days[0].isocalendar()
    legend = '<div class="legend"><span><i style="background:#4bb463"></i>&lt;70%</span><span><i style="background:#dba92c"></i>70–90%</span><span><i style="background:#dc4a45"></i>&gt;90%</span></div>'
    return (
        f'<section id="week"><div class="weekbar"><b>KW {kw} / {year}</b></div>'
        f'<div class="plan"><table><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table>{legend}</div></section>'
    )


def shipping(d: dict) -> str:
    tours = []
    for tour in d["tours"]:
        stops = []
        for index, stop in enumerate(tour["stops"], 1):
            stops.append(
                f'<div class="stop"><div class="row"><span><span class="num">{index}</span>Stopp {index}</span>{pill("Versandbereit")}</div>'
                f'<p style="margin:10px 0 0"><b>{e(", ".join(stop["jobs"]))}</b><br>{e(stop["name"])}</p>'
                f'<div class="addr">{e(stop["street"])}<br><b>{e(stop["zip"])}</b>{e(stop["city"])}</div>'
                f'<div class="row muted"><span>Liefertermin</span><span>{de_date(stop["due"] or "")}</span></div></div>'
            )
        tours.append(
            f'<div><div class="tourhead">{icon("pin")}<b>Region {e(tour["region"])}</b><span>{count(len(tour["stops"]), "Stopp", "Stopps")}</span>'
            f'<span>{count(tour["job_count"], "Auftrag", "Aufträge")}</span><a class="btn green" href="{e(tour["maps_url"])}">{icon("truck")}Route öffnen</a></div>'
            + "".join(stops)
            + "</div>"
        )
    return f'<section id="shipping"><h1>Versand</h1><p class="sub">Fertige Aufträge, nach Region gebündelt. Die Route öffnet sich in Google Maps.</p><div class="tours">{"".join(tours)}</div></section>'


def updates(d: dict) -> str:
    rows = [("", [e(x["zeit"][11:16]) + " Uhr", de_date(x["zeit"]), f'<span class="strong">{e(x["auftrag"])}</span>', pill(x["status"]), e(x["wer"]), e(x["notiz"])]) for x in d["events"]]
    return '<section id="updates"><h1>Auftragsupdates</h1><p class="sub">Meldungen aus der Halle per QR-Scan, neueste zuerst.</p>' + table(["Zeit", "Datum", "Auftragsnr.", "Meldung", "Von", "Notiz"], rows) + "</section>"


def cases_section(d: dict) -> str:
    rows = [
        ("", [f'<span class="strong">{e(c["subject"])}</span>', e(c["type"]), pill(c["priority"]), e(c["owner"]), de_date(c["due_date"]), e(c["job_number"] or "–"), e(c["attachment_status"])])
        for c in d["cases"]
    ]
    reminders = [("", [f'<span class="strong">{e(r["offer"])}</span>', e(r["customer"]), e(r["clerk"]), f'{r["days_waiting"]} Tage']) for r in d["reminders"]]
    return (
        '<section id="cases"><h1>Vorgänge</h1><p class="sub">Jede eingehende E-Mail wird ein Vorgang mit Zuständigkeit und Antwortfrist.</p>'
        + table(["Betreff", "Art", "Priorität", "Zuständig", "Antwort bis", "Auftrag", "Anhang"], rows)
        + "<h2>Angebote ohne Antwort</h2>"
        + table(["Angebot", "Kunde", "Sachbearbeitung", "Wartet seit"], reminders)
        + "</section>"
    )


def reports(d: dict) -> str:
    k, r, counts = d["kpis"], d["reactivation"], d["status_counts"]
    top = max(counts.values()) or 1
    cols = "".join(
        f'<div class="col"><b>{counts[name]}</b><i style="height:{counts[name] / top * 100:.0f}%;background:{color}"></i><span>{e(name)}</span></div>'
        for name, color in STAGE_COLORS.items()
    )
    return (
        '<section id="reports"><h1>Pipeline</h1><p class="sub">Aufträge nach Status und Reaktivierung der Bestandskunden</p><h2>Aktueller Stand</h2><div class="cards">'
        + kpi("package", "Offene Aufträge", k["open_jobs"])
        + kpi("alert", "Problem-Aufträge", k["problems"], "warn" if k["problems"] else "")
        + kpi("clock", "Überfällig", k["overdue"], "bad" if k["overdue"] else "")
        + kpi("calendar", "Bald fällig", k["due_soon"])
        + f'</div><div class="card" style="margin-top:16px"><b>Verteilung nach Status</b><div style="font-size:30px;font-weight:700;margin-top:6px">{len(d["jobs"])}</div>'
        f'<small class="muted">Aufträge gesamt</small><div class="chart">{cols}</div></div><h2>Reaktivierung</h2><div class="cards">'
        + kpi("users", "Inaktive Kunden mit Einwilligung", r["inactive"])
        + kpi("users", "Aktive Kunden", r["active"])
        + kpi("mail", "Ohne Einwilligung (nicht angeschrieben)", r["blocked"])
        + "</div></section>"
    )


def render_html(d: dict) -> str:
    tab_names = [("overview", "Tagesübersicht"), ("orders", "Aufträge"), ("week", "Wochenplan"), ("shipping", "Versand"), ("updates", "Auftragsupdates"), ("cases", "Vorgänge"), ("reports", "Reports")]
    tabs = "".join(f'<button class="tab" role="tab" data-tab="{key}">{label}</button>' for key, label in tab_names)
    rail = "".join(f"<span>{icon(n)}</span>" for n in ["search", "grid", "chat", "calendar", "users", "mail", "send", "star", "chart"])
    dots = "".join(
        f'<span class="dot" style="background:{color}">{content}</span>'
        for color, content in [("#2f9e57", icon("chat")), ("#2563eb", icon("star")), ("#e9742b", icon("alert")), ("#3b82f6", "?"), ("#7fb69a", "XO")]
    )
    sections = overview(d) + orders(d) + week(d) + shipping(d) + updates(d) + cases_section(d) + reports(d)
    return f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>XOS Demo</title><style>{CSS}</style></head><body>
<nav class="rail" aria-hidden="true"><span class="on">{icon("home")}</span>{rail}<span class="end">{icon("settings")}</span></nav>
<div class="top" aria-hidden="true">{dots}</div>
<div class="app">
<div class="head"><span class="brand">XOS</span><div class="tabs" role="tablist">{tabs}</div></div>
<main>{sections}<p class="note">Alle Daten sind synthetisch. Die Seite zeigt, was aus einem XML-Export, QR-Scans, E-Mails und einer Kundenliste entsteht.</p></main>
</div><script>{JS}</script></body></html>
"""
