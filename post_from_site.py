#!/usr/bin/env python3
import re, sys, html, datetime, os

def grab(date=None, top1_only=False):
    if date is None:
        date = datetime.date.today().isoformat()
    path = f"{date}.html"
    if not os.path.exists(path):
        alt = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{date}.html")
        path = alt if os.path.exists(alt) else path
    with open(path, encoding="utf-8") as f:
        doc = f.read()
    blocks = doc.split('<div class="race-block"')
    races = []
    for b in blocks[1:]:
        time_m   = re.search(r'race-time">([^<]+)</span>', b)
        course_m = re.search(r'race-course">([^<]+)</span>', b)
        if not time_m or not course_m:
            continue
        time   = time_m.group(1).strip()
        course = html.unescape(course_m.group(1).strip())
        picks = []
        for pm in re.finditer(r'<div class="pick (top1|top2)([^"]*)"(.*?)(?=<div class="pick |</div></div><div class="race-block|</div></div>$|$)', b, re.S):
            slot, classes, body = pm.group(1), pm.group(2), pm.group(3)
            is_nr  = 'nr' in classes.split() or 'NON-RUNNER' in body
            horse_m= re.search(r'class="horse">([^<]+)</span>', body)
            tier_m = re.search(r'class="medal [A-Z]+">([A-Z]+)</span>', body)
            price_m= re.search(r'class="v">([^<]*)</span>', body)
            if not horse_m:
                continue
            horse = html.unescape(horse_m.group(1).strip())
            horse = re.sub(r'\s+\(\d+\)\s*$', '', horse).strip()
            tier  = tier_m.group(1) if tier_m else ""
            price = html.unescape(price_m.group(1).strip()) if price_m else "-"
            picks.append((slot, horse, tier, price, is_nr))
        races.append((time, course, picks))
    out = ["🐦 MAGPIE TIPS — " + _nice_date(date) + " 🐦", ""]
    out.append("⭐ = top pick" + ("" if top1_only else " · • = second") + " · advised price")
    out.append("")
    for time, course, picks in races:
        line_top = line_sec = None
        for slot, horse, tier, price, is_nr in picks:
            star = "⭐" if slot == "top1" else "•"
            tag  = f" 🏆{tier}" if tier == "PLATINUM" else ""
            if is_nr:
                txt = f"{star} {horse} 🚫NR"
            elif price in ("-", ""):
                txt = f"{star} {horse} (price tbc)"
            else:
                txt = f"{star} {horse} {price}{tag}"
            if slot == "top1": line_top = txt
            else: line_sec = txt
        row = f"{time} {course}"
        if line_top: row += f"\n  {line_top}"
        if line_sec and not top1_only: row += f"\n  {line_sec}"
        out.append(row)
    out += ["", "👉 Full card + Magpie Read: magpietips.co.uk", "", "#HorseRacing #RacingTips #UKRacing #MagpieTips"]
    return "\n".join(out)

def _nice_date(d):
    return datetime.date.fromisoformat(d).strftime("%A %-d %B")

if __name__ == "__main__":
    args = sys.argv[1:]
    top1 = "--top1" in args
    args = [a for a in args if not a.startswith("--")]
    print(grab(args[0] if args else None, top1))
