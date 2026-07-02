#!/usr/bin/env python3
# patch_0701.py YYYY-MM-DD : fill BLANK advised-price spans in the published HTML
# from the prices posted on Telegram (Betfair-sourced). Blanks only; numeric never touched.
# Fozzie/Newport/King Of War have no price -> stay blank -> void. Backs up to .bak.
import sys, os, re, unicodedata, shutil
DATE=sys.argv[1] if len(sys.argv)>1 else "2026-07-01"
SITE=os.path.expanduser(f"~/magpie-site/{DATE}.html")
if not os.path.exists(SITE): sys.exit(f"missing {SITE}")
TG={
"Kodiak Breeze":"2.36","Possessive":"2.52","Quick Sharpener":"18.50","Doyouknowwhatimean":"34.00",
"Arapaho Gold":"1.35","Micks The Boy":"19.50","Calli Black":"15.00","Majestic Moment":"6.00",
"Lord Dor":"1.67","Neigh Botha":"8.60","Turpin Gold":"8.00","Desert Master":"17.00","Uncle Sam":"15.50",
"Versatile":"6.60","Trouville":"2.24","Simbas Pride":"3.85","Go Lockers Go":"7.80","Sword Of Wessex":"7.80",
"Dunstall Star":"4.40","York Tower":"3.05","Asia Force":"5.00","Al Mootamarid":"4.60","Novello Lad":"7.80",
"Lord Roxby":"8.20","Tattie Bogle":"7.60","Iamyouare":"3.90","Roxboro River":"5.60","Away And Gone":"10.00",
"Scandi Noir":"2.72","Imperial Cult":"4.00","Hello Cotai":"4.60","Monastere":"9.80","Im Spartacus":"8.60",
"Shemiyla Star":"4.10","Mojito Madness":"10.50","Reality Queen":"2.64","Rosieisme Darling":"4.40",
"Treasure Rose":"6.20","Reimagined":"11.50","Dream Composer":"6.00","Amazing Journey":"3.15","Angel Ang":"3.50",
"Theheatison":"4.70","Rodeeve":"9.40","Queen Aethelflaed":"8.20","Central Command":"9.40","Alma Latina":"2.02",
"Neptune Legend":"2.06","Sisters In The Sky":"21.00","Only One Scobie":"4.70","Fortuity":"5.60",
"Sarangpur":"1.90","Stintino Sunset":"12.50","Monks Mead":"7.40","Blue Hero":"11.50","Bella Colombia":"3.70",
"Launch Time":"4.50","Gearings Point":"10.00","Ricardo Phillips":"11.00","Sant Alessio":"8.80","Post Rider":"7.00",
"Pleased":"2.14","Vanir":"3.15","Musical Angel":"7.00","Sporting Light":"15.50","Sea Of Charm":"27.00","Pivotal Days":"60.00",
}
def clean(n):
    n=unicodedata.normalize("NFKD",n or "").encode("ascii","ignore").decode().lower()
    n=re.sub(r"\([^)]*\)","",n); return re.sub(r"[^a-z0-9]","",n)
PR={clean(k):v for k,v in TG.items()}
html=open(SITE,encoding="utf-8").read()
horses=[(m.start(),m.group(1)) for m in re.finditer(r'class="horse">([^<]+)',html)]
def hb(pos):
    nm=None
    for hp,hn in horses:
        if hp<pos: nm=hn
        else: break
    return nm
RE=re.compile(r'(Advised price</span><span class="v">)([^<]*)(</span>)')
filled=[]; kept=0; blank=[]
def repl(m):
    global kept
    pre,val,post=m.group(1),m.group(2).strip(),m.group(3)
    if val not in ("","-","\u2014"): kept+=1; return m.group(0)
    hn=hb(m.start()); cp=PR.get(clean(hn or ""))
    if cp is None: blank.append((hn or "").strip()); return m.group(0)
    filled.append((hn,cp)); return pre+cp+post
new=RE.sub(repl,html)
print(f"kept {kept} numeric | filled {len(filled)} blanks | left blank {len(blank)}")
for hn,cp in filled: print(f"  + {hn:24} -> {cp}")
if blank: print("  · still blank (no price = void):", blank)
if filled:
    shutil.copy(SITE,SITE+".bak"); open(SITE,"w",encoding="utf-8").write(new)
    print(f"\nwrote {SITE} (backup .bak)")
else: print("\nnothing to fill")
