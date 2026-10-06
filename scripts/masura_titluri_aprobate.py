"""[07.10.2026, lotul 07.10 pct.22] Titlurile APROBATE (livrate spre publicare in pachetele de lot) fara pagina publicata.

Sursa de adevar pentru „publicat” = paginile din ghid/ (ce serveste iconta.eu/ghid/<slug>), NU statutul din registru.
Un titlu aprobat are pagina daca oricare din: slug_publicat din registru, titlul din registru, titlul DRAFTULUI aprobat,
slugul fisierului draft — exista in ghid/. Potrivirea „titlu apropiat” a masuratorii din 06.10 lega 4 drafturi de alt rand
din registru (statut „asemanator”), desi drafturile insele erau publicate — de aici 287 in loc de 283."""
import csv, io, os, re, zipfile, collections, unicodedata, glob
G = "/home/costin/ghid_incoming"
def norm(t): return re.sub(r"\s+", " ", unicodedata.normalize("NFC", (t or "")).strip().lower())
reg = list(csv.DictReader(open("index_titluri_ghid.csv", encoding="utf-8")))
pe_id = {r["id"]: r for r in reg}
pe_titlu = {}
for r in reg: pe_titlu.setdefault(norm(r["titlu"]), r)
pag_slug, pag_titlu = set(), set()
for fp in glob.glob("ghid/*.md"):
    pag_slug.add(os.path.basename(fp)[:-3])
    tm = re.search(r'^title:\s*"?(.*?)"?\s*$', io.open(fp, encoding="utf-8").read(), re.M)
    if tm: pag_titlu.add(norm(tm.group(1)))
aprobate = {}   # cheie -> dict(id, titlu, pachet, pagina)
def cheie(r, titlu): return r["id"] if r else "T:" + norm(titlu)
def are_pagina(r, titlu, slug):
    if r and r["slug_publicat"] and r["slug_publicat"] in pag_slug: return True
    if r and norm(r["titlu"]) in pag_titlu: return True
    if titlu and norm(titlu) in pag_titlu: return True
    if slug and slug in pag_slug: return True
    return False
def adauga(r, titlu, slug, pachet):
    k = cheie(r, titlu)
    p = are_pagina(r, titlu, slug)
    if k in aprobate:
        aprobate[k]["pagina"] = aprobate[k]["pagina"] or p; return
    aprobate[k] = {"id": r["id"] if r else "", "status": r["status"] if r else "(fara rand)", "titlu": titlu or (r or {}).get("titlu"),
                   "pachet": pachet, "pagina": p}
pachete = [f for f in sorted(os.listdir(G)) if re.match(r"batch\d+.*_ghiduri.*\.zip$", f) or f in ("ghiduri_lot18.zip", "iconta_lot19_ghiduri.zip")]
for f in pachete:
    z = zipfile.ZipFile(os.path.join(G, f))
    for n in z.namelist():
        if not (n.endswith(".md") and ("/ghid/" in "/" + n or "GH-" in n or "/draft/" in n or n.startswith("ghid/"))): continue
        txt = z.read(n).decode("utf-8", "ignore")
        tm = re.search(r'^title:\s*"?(.*?)"?\s*$', txt, re.M)
        titlu = tm.group(1) if tm else None
        m = re.search(r"(GH-\d{5})[^/]*\.md$", n)
        r = pe_id.get(m.group(1)) if m else (pe_titlu.get(norm(titlu)) if titlu else None)
        adauga(r, titlu, os.path.basename(n)[:-3], f)
z = zipfile.ZipFile(os.path.join(G, "iconta_lot19_ghiduri.zip"))
for row in csv.DictReader(io.TextIOWrapper(z.open("verificare/lot19_titluri.csv"), encoding="utf-8-sig")):
    adauga(pe_titlu.get(norm(row["titlu"])), row["titlu"], None, "lot19_titluri.csv")
nep = sorted((v["id"], v["status"], v["pachet"], v["titlu"]) for v in aprobate.values() if not v["pagina"])
print("PACHETE citite:", len(pachete), "| PAGINI in ghid/:", len(pag_slug))
print("TITLURI APROBATE (distincte):", len(aprobate), "| cu pagina:", sum(1 for v in aprobate.values() if v["pagina"]))
print("APROBATE FARA PAGINA PUBLICATA:", len(nep), dict(collections.Counter(x[1] for x in nep)))
with open(os.environ.get("IESIRE", "/dev/null"), "w", encoding="utf-8", newline="") as fo:
    w = csv.writer(fo); w.writerow(["id", "status_registru", "pachet", "titlu"]); w.writerows(nep)
