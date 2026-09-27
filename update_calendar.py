import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

SOURCE = 'https://www.padelfip.com/es/calendario-premier-padel/?events-year={year}'
OUT = Path('docs/premier-padel.ics')
YEARS = range(datetime.now(timezone.utc).year, datetime.now(timezone.utc).year + 2)

HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; PremierPadelCalendar/1.0)'}
ALLOWED = ('major', 'p1', 'finals')

MONTHS = {
    'enero':1,'febrero':2,'marzo':3,'abril':4,'mayo':5,'junio':6,
    'julio':7,'agosto':8,'septiembre':9,'octubre':10,'noviembre':11,'diciembre':12
}

def parse_date_range(text):
    m = re.search(r'(\d{2}/\d{2}/\d{4})\s+al\s+(\d{2}/\d{2}/\d{4})', text)
    if not m:
        return None
    return datetime.strptime(m.group(1), '%d/%m/%Y').date(), datetime.strptime(m.group(2), '%d/%m/%Y').date()

def classify(name):
    n = name.lower()
    if 'final' in n:
        return 'Finals'
    if 'major' in n:
        return 'Major'
    if re.search(r'\bp1\b', n):
        return 'P1'
    return None

def clean(s):
    return re.sub(r'\s+', ' ', s).strip()

def esc(s):
    return s.replace('\\','\\\\').replace(';','\\;').replace(',','\\,').replace('\n','\\n')

def fold(line):
    # RFC 5545 line folding at <=75 octets. ASCII is enough for field prefixes;
    # for UTF-8 text, fold by encoded bytes without splitting a codepoint.
    out=[]
    while len(line.encode('utf-8')) > 75:
        cut=75
        while len(line[:cut].encode('utf-8')) > 75:
            cut-=1
        out.append(line[:cut])
        line=' '+line[cut:]
    out.append(line)
    return '\r\n'.join(out)

def fetch_events(year):
    r = requests.get(SOURCE.format(year=year), headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    events=[]
    # FIP's calendar cards contain an event link, a date range, and a location.
    # We deliberately identify by visible text/category, not brittle CSS classes.
    for a in soup.find_all('a', href=True):
        name = clean(a.get_text(' ', strip=True))
        kind = classify(name)
        if not kind or len(name) < 4 or name.upper() in {'IR AL EVENTO'}:
            continue
        parent = a.parent
        # Search a bounded ancestor for date/location text.
        block = parent
        for _ in range(6):
            if block is None: break
            txt = clean(block.get_text(' ', strip=True))
            if re.search(r'\d{2}/\d{2}/\d{4}\s+al\s+\d{2}/\d{2}/\d{4}', txt):
                dr = parse_date_range(txt)
                if dr:
                    start, end = dr
                    # End date on FIP is inclusive; all-day ICS uses DTEND exclusive.
                    end_excl = end.fromordinal(end.toordinal()+1)
                    parts = [p.strip() for p in txt.split('|') if p.strip()]
                    # Remove name/date/status fragments and derive location from lines/text.
                    loc = ''
                    known_cities = re.findall(r'(?:del \d{2}/\d{2}/\d{4} al \d{2}/\d{2}/\d{4})\s+(.+?)(?:\s+(?:IR AL EVENTO|Terminado|Inscripción|En directo)|$)', txt, re.I)
                    if known_cities: loc = clean(known_cities[0])
                    # Better: use text around the date and remove common status labels.
                    after = re.split(r'\d{2}/\d{2}/\d{4}\s+al\s+\d{2}/\d{2}/\d{4}', txt, maxsplit=1)[-1]
                    after = re.sub(r'\b(IR AL EVENTO|Terminado|Inscripción (?:cerrada|abierta)|En directo)\b.*$', '', after, flags=re.I).strip(' |')
                    if after and len(after) < 100: loc = after
                    url = urljoin(SOURCE.format(year=year), a['href'])
                    events.append({'name':name,'kind':kind,'start':start,'end':end_excl,'location':loc,'url':url})
                    break
            block = block.parent
    # Deduplicate by URL/name/date.
    uniq={}
    for e in events:
        uniq[(e['name'], e['start'], e['end'])]=e
    return list(uniq.values())

def main():
    all_events=[]
    for year in YEARS:
        try:
            all_events.extend(fetch_events(year))
        except Exception as e:
            print(f'Warning: failed to fetch {year}: {e}')
    all_events.sort(key=lambda e:(e['start'], e['name']))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    lines=[
        'BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//Independent FIP Premier Padel Calendar//EN',
        'CALSCALE:GREGORIAN','METHOD:PUBLISH','X-WR-CALNAME:Premier Padel — FIP Majors, P1 & Finals',
        'X-WR-CALDESC:Filtered directly from the official FIP Premier Padel calendar. Categories: Major, P1, Finals.',
        'X-PUBLISHED-TTL:P1W'
    ]
    for e in all_events:
        uid=f"{e['start'].isoformat()}-{re.sub(r'[^a-z0-9]+','-',e['name'].lower()).strip('-')}@fip-calendar.local"
        lines += ['BEGIN:VEVENT',f'UID:{uid}',f'DTSTAMP:{stamp}',f'DTSTART;VALUE=DATE:{e["start"].strftime("%Y%m%d")}',f'DTEND;VALUE=DATE:{e["end"].strftime("%Y%m%d")}',f'SUMMARY:{esc(e["name"])}',f'CATEGORIES:{e["kind"]}',f'DESCRIPTION:{esc("Official FIP Premier Padel calendar — " + e["kind"])}']
        if e['location']: lines.append(f'LOCATION:{esc(e["location"])}')
        if e['url']: lines.append(f'URL:{e["url"]}')
        lines += ['END:VEVENT']
    lines.append('END:VCALENDAR')
    OUT.write_text('\r\n'.join(fold(x) for x in lines)+'\r\n', encoding='utf-8')
    print(f'Wrote {OUT} with {len(all_events)} events')
    if not all_events:
        raise SystemExit('No qualifying events found; refusing to overwrite with an empty feed.')

if __name__=='__main__': main()
