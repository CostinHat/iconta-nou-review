# -*- coding: utf-8 -*-
"""GARD — registrul de titluri (`index_titluri_ghid.csv`) nu spune „nepublicat” despre un ghid care e publicat.

[lotul 07.10 pct.22, comanda Costin 06.10.2026] „Numărul exact de titluri aprobate din registrul de titluri /ghid încă
nepublicate.” Măsurătoarea a arătat că registrul rămăsese în urmă: 81 de rânduri „candidat” / „asemănător” aveau pagina lor
publicată, sub titlul aprobat (care diferă de întrebarea din registru) sau cu întrebarea ca H1. Consecința nu era doar o cifră
greșită (287 în loc de 62): `ghid_titluri.de_propus()` ar fi propus din nou titluri deja publicate.

CE FACE IMPOSIBIL: un rând nepublicat în registru al cărui titlu este H1-ul sau titlul (frontmatter) unei pagini din `ghid/`
care NU e pagina „asemănătoare” a rândului și nu e revendicată de alt rând publicat. LIMITA DECLARATĂ: vede numai potrivirea
EXACTĂ (normalizată) a titlului — un ghid publicat sub un titlu reformulat față de registru și de H1 nu se vede de aici (pentru
acela, potrivirea pe GH-id din pachetele de lot, care stau în afara repo-ului: `~/ghid_incoming`)."""
import csv
import glob
import io
import os
import re
import unicodedata


def _norm(t):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", (t or "")).strip().lower())


def _pagini():
    out = {}
    for fp in glob.glob("ghid/*.md"):
        t = io.open(fp, encoding="utf-8").read()
        tm = re.search(r'^title:\s*"?(.*?)"?\s*$', t, re.M)
        h1 = re.search(r"^# (.+)$", t, re.M)
        for x in (tm.group(1) if tm else "", h1.group(1).strip() if h1 else ""):
            if x:
                out.setdefault(_norm(x), set()).add(os.path.basename(fp)[:-3])
    return out


def nepublicate_cu_pagina():
    reg = list(csv.DictReader(io.open("index_titluri_ghid.csv", encoding="utf-8")))
    publicate = {r["slug_publicat"] for r in reg if r["slug_publicat"]}
    pag = _pagini()
    gresite = []
    for r in reg:
        if r["status"] == "publicat":
            continue
        toate = pag.get(_norm(r["titlu"]), set())
        cand = toate - {r["slug_asemanator"]} - publicate
        if cand:
            gresite.append((r["id"], r["status"], sorted(cand)))
        elif r["status"] == "candidat" and toate:
            # titlul EXACT e deja live ca ghidul altui rând: „candidat” l-ar repropune (`de_propus`); e „asemanator”
            gresite.append((r["id"], "candidat cu titlul deja publicat", sorted(toate)))
    return gresite, len(reg), len(pag)


def test_registrul_nu_numeste_nepublicat_un_ghid_publicat():
    """MUTAȚIE: un rând corectat pus înapoi pe „candidat” (de ex. GH-00018, pagina `contract-part-time-regimul-micro`,
    al cărei H1 e întrebarea din registru) -> lista nevidă -> pică."""
    gresite, n_reg, n_pag = nepublicate_cu_pagina()
    assert n_reg > 8000 and n_pag > 6000          # premisă anti-vid: registrul și paginile chiar s-au citit
    assert gresite == []
