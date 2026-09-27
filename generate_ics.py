import datetime
import re
import urllib.request
import json
from icalendar import Calendar, Event

# Keywords to match target tournament tiers
ALLOWED_TIERS = ["MAJOR", "P1", "FINALS"]

def build_ical():
    cal = Calendar()
    cal.add('prodid', '-//Premier Padel iCal Generator//mx//')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'Premier Padel Top Tier')
    cal.add('x-wr-timezone', 'UTC')

    # Example structured dataset for target tournaments
    # In practice, you can fetch live data from the official FIP API or site
    tournaments = [
        {"name": "Riyadh P1", "start": "2026-02-09", "end": "2026-02-14", "tier": "P1"},
        {"name": "Miami P1", "start": "2026-03-23", "end": "2026-03-29", "tier": "P1"},
        {"name": "Qatar Major", "start": "2026-04-06", "end": "2026-04-11", "tier": "MAJOR"},
        {"name": "Buenos Aires P1", "start": "2026-05-11", "end": "2026-05-17", "tier": "P1"},
        {"name": "Italy Major", "start": "2026-06-01", "end": "2026-06-07", "tier": "MAJOR"},
        {"name": "Valencia P1", "start": "2026-06-08", "end": "2026-06-14", "tier": "P1"},
        {"name": "Málaga P1", "start": "2026-07-13", "end": "2026-07-19", "tier": "P1"},
        {"name": "London P1", "start": "2026-08-03", "end": "2026-08-09", "tier": "P1"},
        {"name": "Madrid P1", "start": "2026-08-31", "end": "2026-09-06", "tier": "P1"},
        {"name": "Paris Major", "start": "2026-09-07", "end": "2026-09-13", "tier": "MAJOR"},
        {"name": "Milano P1", "start": "2026-10-12", "end": "2026-10-18", "tier": "P1"},
        {"name": "Kuwait City P1", "start": "2026-10-26", "end": "2026-10-31", "tier": "P1"},
        {"name": "Dubai P1", "start": "2026-11-09", "end": "2026-11-15", "tier": "P1"},
        {"name": "Mexico Major", "start": "2026-11-23", "end": "2026-11-29", "tier": "MAJOR"},
        {"name": "Barcelona Finals", "start": "2026-12-07", "end": "2026-12-13", "tier": "FINALS"},
    ]

    for t in tournaments:
        tier = t["tier"].upper()
        if not any(target in tier for target in ALLOWED_TIERS):
            continue

        end_dt = datetime.datetime.strptime(t["end"], "%Y-%m-%d").date()
        
        # Quarterfinals: 2 days before final (Friday)
        # Semifinals: 1 day before final (Saturday)
        # Finals: Main end date (Sunday)
        qf_date = end_dt - datetime.timedelta(days=2)
        sf_date = end_dt - datetime.timedelta(days=1)
        final_date = end_dt

        stages = [
            ("Quarterfinals", qf_date),
            ("Semifinals", sf_date),
            ("Finals", final_date),
        ]

        for stage, dt in stages:
            event = Event()
            title = f"🎾Premier Padel: {t['name']} - {stage}"
            event.add('summary', title)
            event.add('dtstart', dt)
            event.add('dtend', dt + datetime.timedelta(days=1))
            event.add('description', f"Premier Padel {t['name']} ({stage})")
            cal.add_component(event)

    with open("premier_padel.ics", "wb") as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    build_ical()
