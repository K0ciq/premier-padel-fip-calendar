import datetime

ALLOWED_TIERS = ["MAJOR", "P1", "FINALS"]

def format_ics_datetime(dt):
    return dt.strftime("%Y%m%d")

def build_calendar():
    tournaments = [
        {"name": "Riyadh P1", "end": "2026-02-14", "tier": "P1"},
        {"name": "Miami P1", "end": "2026-03-28", "tier": "P1"},
        {"name": "Qatar Major", "end": "2026-04-10", "tier": "MAJOR"},
        {"name": "Buenos Aires P1", "end": "2026-05-16", "tier": "P1"},
        {"name": "Italy Major", "end": "2026-06-06", "tier": "MAJOR"},
        {"name": "Valencia P1", "end": "2026-06-13", "tier": "P1"},
        {"name": "Málaga P1", "end": "2026-07-18", "tier": "P1"},
        {"name": "London P1", "end": "2026-08-08", "tier": "P1"},
        {"name": "Madrid P1", "end": "2026-09-05", "tier": "P1"},
        {"name": "Paris Major", "end": "2026-09-12", "tier": "MAJOR"},
        {"name": "Milano P1", "end": "2026-10-17", "tier": "P1"},
        {"name": "Kuwait Major", "end": "2026-10-30", "tier": "MAJOR"},
        {"name": "Dubai P1", "end": "2026-11-14", "tier": "P1"},
        {"name": "Mexico Major", "end": "2026-11-28", "tier": "MAJOR"},
        {"name": "Barcelona Finals", "end": "2026-12-12", "tier": "FINALS"},
    ]

    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Premier Padel iCal Generator//EN",
        "X-WR-CALNAME:Premier Padel Top Tier",
        "X-WR-TIMEZONE:UTC",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]

    for t in tournaments:
        tier = t["tier"].upper()
        if not any(target in tier for target in ALLOWED_TIERS):
            continue

        end_dt = datetime.datetime.strptime(t["end"], "%Y-%m-%d").date()

        qf_date = end_dt - datetime.timedelta(days=2)
        sf_date = end_dt - datetime.timedelta(days=1)
        final_date = end_dt

        stages = [
            ("Quarterfinals", qf_date),
            ("Semifinals", sf_date),
            ("Finals", final_date),
        ]

        for stage, dt in stages:
            start_str = format_ics_datetime(dt)
            end_str = format_ics_datetime(dt + datetime.timedelta(days=1))
            uid = f"{t['name'].replace(' ', '_')}_{stage}_{start_str}@premierpadel"
            
            ics_lines.extend([
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"SUMMARY:🎾Premier Padel: {t['name']} - {stage}",
                f"DTSTART;VALUE=DATE:{start_str}",
                f"DTEND;VALUE=DATE:{end_str}",
                f"DESCRIPTION:Premier Padel {t['name']} ({stage})",
                "STATUS:CONFIRMED",
                "END:VEVENT"
            ])

    ics_lines.append("END:VCALENDAR")

    with open("premier-padel.ics", "w", encoding="utf-8") as f:
        f.write("\n".join(ics_lines))

if __name__ == "__main__":
    build_calendar()
