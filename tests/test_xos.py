"""Tests gegen die synthetischen Beispieldaten.

    python3 -m unittest discover -s tests -v
"""
import json
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

from xos import capacity, cases, dashboard, followup, reactivation, roi, shipping, status
from xos.jobticket import load_jobs, parse_date, read_folder, work_centres

SAMPLE = Path(__file__).resolve().parent.parent / "data" / "sample"
TODAY = date(2026, 3, 11)


class JobTicketTest(unittest.TestCase):
    def test_serial_and_iso_dates(self):
        self.assertEqual(parse_date("46090"), date(2026, 3, 9))
        self.assertEqual(parse_date("2026-03-09"), date(2026, 3, 9))
        self.assertIsNone(parse_date(""))

    def test_sample_jobs_load_completely(self):
        jobs, errors = read_folder(SAMPLE / "jobs")
        self.assertEqual(len(jobs), 24)
        self.assertEqual(errors, [])
        self.assertTrue(all(job.operations and job.delivery_zip for job in jobs))

    def test_broken_file_does_not_stop_the_run(self):
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, "kaputt.xml").write_text("<Auftrag nummer='1'", encoding="utf-8")
            jobs, errors = read_folder(Path(folder))
            self.assertEqual(jobs, [])
            self.assertEqual(errors[0][0], "kaputt.xml")


class CapacityTest(unittest.TestCase):
    def test_traffic_light_thresholds(self):
        self.assertEqual(capacity.traffic_light(0.69), "gruen")
        self.assertEqual(capacity.traffic_light(0.70), "gelb")
        self.assertEqual(capacity.traffic_light(0.90), "gelb")
        self.assertEqual(capacity.traffic_light(0.91), "rot")

    def test_calendar_minutes_match_operations(self):
        jobs = load_jobs(SAMPLE / "jobs")
        calendar = capacity.week_calendar(jobs, work_centres(jobs), date(2026, 3, 9))
        in_week = sum(
            op.minutes for job in jobs for op in job.operations if date(2026, 3, 9) <= op.day <= date(2026, 3, 15)
        )
        self.assertEqual(sum(cell["minutes"] for row in calendar for cell in row["cells"]), round(in_week))
        self.assertEqual(len(calendar[0]["cells"]), 7)


class StatusTest(unittest.TestCase):
    def test_transitions(self):
        self.assertEqual(status.next_status(status.OFFEN, status.IN_PRODUKTION), status.IN_PRODUKTION)
        with self.assertRaises(ValueError):
            status.next_status(status.OFFEN, status.VERSENDET)

    def test_invalid_scan_is_reported_not_swallowed(self):
        events = [{"auftrag": "1", "status": status.VERSENDET, "wer": "x", "zeit": "2026-03-11T08:00:00", "notiz": ""}]
        state, rejected = status.replay(events)
        self.assertEqual(state, {})
        self.assertEqual(len(rejected), 1)

    def test_scan_url(self):
        self.assertEqual(status.scan_url("https://xos.example/", "26-0101"), "https://xos.example/status?auftrag=26-0101")


class ShippingTest(unittest.TestCase):
    def test_only_finished_jobs_and_same_address_is_one_stop(self):
        jobs = load_jobs(SAMPLE / "jobs")
        state = status.current_status(status.EventLog(SAMPLE / "status_events.jsonl").read())
        tours = shipping.plan(jobs, state, "Werkstraße 1, 50999 Köln")
        planned = [number for tour in tours for stop in tour["stops"] for number in stop["jobs"]]
        self.assertTrue(planned)
        self.assertTrue(all(state[number] == status.FERTIG for number in planned))
        self.assertEqual(len(planned), len(set(planned)))
        addresses = [(s["name"], s["street"]) for t in tours for s in t["stops"]]
        self.assertEqual(len(addresses), len(set(addresses)))
        self.assertTrue(all(t["maps_url"].startswith("https://www.google.com/maps/dir/") for t in tours))


class CaseTest(unittest.TestCase):
    def setUp(self):
        with (SAMPLE / "emails.json").open(encoding="utf-8") as handle:
            self.mails = json.load(handle)

    def classify(self, index):
        m = self.mails[index]
        return cases.classify(m["von"], m["betreff"], m["text"], datetime.fromisoformat(m["eingang"]), m["anhaenge"])

    def test_complaint_goes_to_management_and_escalates(self):
        case = self.classify(1)
        self.assertEqual((case.type, case.owner, case.job_number), ("Reklamation", "Geschäftsführung", "26-0104"))
        self.assertTrue(cases.needs_escalation(case))
        self.assertEqual(case.original_body, self.mails[1]["text"])

    def test_wish_date_weekday_and_explicit_date(self):
        self.assertEqual(self.classify(2).wish_date, "2026-03-13")  # "bis Freitag" ab Mittwoch
        self.assertEqual(self.classify(0).wish_date, "2026-03-27")

    def test_download_link_and_urgency(self):
        self.assertEqual(self.classify(3).attachment_status, "Download-Link")
        self.assertEqual(self.classify(7).priority, "Kritisch")

    def test_llm_output_is_validated(self):
        m = self.mails[0]
        args = (m["von"], m["betreff"], m["text"], datetime.fromisoformat(m["eingang"]))
        bad = cases.from_llm_json('{"type": "Erfunden", "priority": "Mega", "job_number": "99-9999"}', *args)
        self.assertEqual((bad.type, bad.priority, bad.job_number), ("Preisanfrage / Kalkulation", "Normal", ""))
        good = cases.from_llm_json('{"type": "Auftrag (Neu)", "priority": "Hoch", "summary": "Kurz."}', *args)
        self.assertEqual((good.type, good.priority, good.description), ("Auftrag (Neu)", "Hoch", "Kurz."))
        self.assertEqual(cases.from_llm_json("kein json", *args).type, "Preisanfrage / Kalkulation")


class FollowUpAndReactivationTest(unittest.TestCase):
    def test_reminders_respect_waiting_time_and_answers(self):
        offers = followup.load_offers(SAMPLE / "offers.csv")
        due = followup.due_reminders(offers, TODAY)
        answered = {o["angebot"] for o in offers if o["antwort_am"]}
        self.assertTrue(due)
        self.assertTrue(all(r["days_waiting"] >= followup.REMIND_AFTER_DAYS for r in due))
        self.assertFalse(answered & {r["offer"] for r in due})

    def test_segments_never_contact_without_consent(self):
        segments = reactivation.segment(reactivation.load_customers(SAMPLE / "customers.csv"), TODAY)
        self.assertEqual(sum(len(v) for v in segments.values()), 40)
        self.assertTrue(all(c["werbung_erlaubt"] == "ja" and c["tage_inaktiv"] > 365 for c in segments["inactive"]))
        self.assertTrue(all(c["werbung_erlaubt"] != "ja" for c in segments["blocked"]))

    def test_potential(self):
        self.assertEqual(reactivation.potential(3000, 0.02, 2000)["revenue_potential"], 120000)


class RoiAndDashboardTest(unittest.TestCase):
    def test_status_quo_cost(self):
        result = roi.status_quo_cost()
        parts = result["search_effort"] + result["missed_orders"] + result["machine_idle"] + result["shipping"]
        self.assertAlmostEqual(result["total_per_year"], parts, delta=2)
        self.assertEqual(result["missed_orders"], 100000)

    def test_dashboard_builds_and_renders(self):
        data = dashboard.build(SAMPLE, TODAY)
        self.assertEqual(len(data["jobs"]), 24)
        self.assertEqual(len(data["cases"]), 8)
        self.assertIn("XOS Demo-Übersicht", dashboard.render_html(data))
        json.dumps(data)  # muss serialisierbar sein


if __name__ == "__main__":
    unittest.main()
