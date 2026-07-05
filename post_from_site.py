#!/usr/bin/env python3
import re, sys, html, datetime, os, requests

HOME="/data/data/com.termux/files/home"
BASE="https://api.theracingapi.com/v1"

def norm(x):
    return re.sub(r"[^a-z0-9]", "", str(x).lower())

def nice_date(d):
    return datetime.date.fromisoformat(d).strftime("%A %-d %B")

def api_prices(date):
    auth_file=f"{HOME}/sb_tomorrow/racingapi_auth.txt"
    user=open(auth_file).read().splitlines()[0].strip()
    pw=open(auth_file).read().splitlines()[1].strip()

    r=requests.get(BASE+"/racecards/pro", auth=(user,pw), timeout=30)
    r.raise_for_status()
    cards=r.json().get("racecards", [])

    prices={}
    horse_prices={}
    for c in cards:
        off=str(c.get("off_time","")).strip()[:5]
        course=norm(c.get("course",""))
        for h in c.get("runners", []):
            name=norm(h.get("horse","") or h.get("name",""))
            odds = h.get("odds") or []
            price = ""
            if odds:
                price = odds[0].get("decimal") or odds[0].get("fractional") or ""
            if name and price:
                horse_prices[name] = str(price)
            if off and course and name and price:
                prices[(off,course,name)] = str(price)

    prices["_horse_only"] = horse_prices
    return prices

def grab(date=None, top1_only=False):
    if date is None:
        date=datetime.date.today().isoformat()

    prices=api_prices(date)
    doc=open(f"{HOME}/magpie-site/{date}.html",encoding="utf-8").read()

    out=["🐦 MAGPIE TIPS — "+nice_date(date)+" 🐦","","⭐ = top pick"+("" if top1_only else " · • = second")+" · advised price",""]

    for rb in doc.split('<div class="race-block"')[1:]:
        tm=re.search(r'race-time">([^<]+)<',rb)
        cm=re.search(r'race-course">([^<]+)<',rb)
        if not tm or not cm: continue

        time=tm.group(1).strip()
        course=html.unescape(cm.group(1).strip())
        ckey=norm(course)

        picks=[]
        for m in re.finditer(r'<div class="pick (top[12])([^"]*)"', rb):
            slot=m.group(1)
            part=rb[m.start():m.start()+3000]

            hm=re.search(r'class="horse">([^<]+)<',part)
            pm=re.search(r'class="v">([^<]*)<',part)
            tier=re.search(r'class="medal ([A-Z]+)"',part)
            if not hm: continue

            horse=html.unescape(hm.group(1).strip())
            horse=re.sub(r'\s+\(\d+\)\s*$','',horse)
            hkey=norm(horse)

            price=html.unescape(pm.group(1).strip()) if pm else ""
            if price in ("","-") or "tbc" in price.lower():
                price=prices.get((time,ckey,hkey)) or prices.get("_horse_only",{}).get(hkey) or "price tbc"

            tag=f" 🏆{tier.group(1)}" if tier and tier.group(1)=="PLATINUM" else ""
            is_nr=("NON-RUNNER" in part.upper()) or ("🚫" in part)

            star="⭐" if slot=="top1" else "•"
            txt=f"{star} {horse} 🚫NR" if is_nr else (f"{star} {horse} (price tbc)" if price in ("","-","price tbc") else f"{star} {horse} {price}{tag}")
            picks.append((slot,txt))

        row=f"{time} {course}"
        top=next((x for s,x in picks if s=="top1"),None)
        sec=next((x for s,x in picks if s=="top2"),None)
        if top: row+=f"\n  {top}"
        if sec and not top1_only: row+=f"\n  {sec}"
        out.append(row)

    out+=["","👉 Full card + Magpie Read: magpietips.co.uk","","#HorseRacing #RacingTips #UKRacing #MagpieTips"]
    return "\n".join(out)

if __name__=="__main__":
    args=sys.argv[1:]
    top1="--top1" in args
    args=[a for a in args if not a.startswith("--")]
    print(grab(args[0] if args else None, top1))
