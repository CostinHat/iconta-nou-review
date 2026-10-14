# -*- coding: utf-8 -*-
"""GARD — comanda Costin 13.10.2026, pct.2b (verbatim în DECIZII): „Scoate din textele publice denumirile din cod (de ex. nir_gv,
coeficient_k) și înlocuiește-le cu numele funcției din aplicație, cum îl vede contabilul.” + pct.2a (măsurătoarea suprapunerilor).

CE ERA: 1.056 de ghiduri publice (din 6.558) purtau 2.413 denumiri din codul aplicației — funcții (`nir_gv(linii, …)`), câmpuri,
tabele, fișiere `.py`, teste, coduri de funcționalitate (F027), „dosarul de cercetare”, identificatori de firmă (tenant_005) — iar unele
blocuri de temei citau CODUL aplicației ca sursă. Unealta: `scripts/curata_coduri_ghid.py`.

CE FACE IMPOSIBIL: un ghid publicat cu o denumire din codul aplicației. Denumirile din structurile OFICIALE ANAF (`d_rec`, `cod_oblig` …)
rămân — sunt ale ANAF, nu ale aplicației (`NOMENCLATOR_OFICIALE`). La fel, o EXPRESIE de cod (`regim == "micro"`, `deductibil: False`,
`pull()`) și o trimitere la registrul intern al proiectului („neconformitate deschisă (R95)”) — găsite la proba lotului, după prima
trecere. MUTAȚIE: `nir_gv` sau `regim == "micro"` scrise înapoi într-un ghid -> pică."""
import csv
import glob
import io
import os
import re
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_RAD, "scripts"))
import curata_coduri_ghid as cc  # noqa: E402
import scan_ghid_suprapuneri as sp  # noqa: E402

_SNAKE = re.compile(r"(?<![\w/.-])([a-z][a-z0-9]*(?:_[a-z0-9]+)+)(?![\w/-])")


def _text_public(t):
    """Ce se publică: titlul, descrierea și corpul (celelalte chei din front-matter nu ajung pe pagină)."""
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    if m:
        t = "\n".join(ln for ln in m.group(1).splitlines() if ln.startswith(("title:", "description:"))) + "\n" + t[m.end():]
    t = re.sub(r"https?://\S+", " ", t)
    return re.sub(r"\]\([^)]*\)", "]", t)


def test_niciun_ghid_public_nu_poarta_denumiri_din_codul_aplicatiei():
    rele = []
    for cale in sorted(glob.glob(os.path.join(_RAD, "ghid", "*.md"))):
        t = io.open(cale, encoding="utf-8").read()
        _nou, k = cc.curata(t)
        snake = [x for x in _SNAKE.findall(_text_public(t)) if x not in cc.NOMENCLATOR_OFICIALE]
        alte = re.findall(r"\bF\d{3}\b|\btenant_\d+\b|/home/|`[\w/.-]+\.py`|registrul intern al proiectului|neconformitate deschisă \(R\d",
                          _text_public(t))
        alte += [x for x in re.findall(r"`([^`\n]+)`", _text_public(t)) if cc.EXPRESIE_COD.search(x)]     # `regim == "micro"`, `pull()`
        if k or snake or alte:
            rele.append((os.path.basename(cale), k, snake[:3], alte[:3]))
    assert not rele, (len(rele), rele[:5])


def test_suprapunerile_masurate_sunt_cele_ale_uneltei():
    """`ghid_suprapuneri.csv` = ce măsoară unealta acum. Cele 45 de grupuri măsurate la 13.10.2026 au fost comasate (răspunsul la §6
    COMANDA_13_10 pct.1; registrul: `ghid_comasate.csv`), deci unealta nu mai găsește niciun grup; exemplul din comandă e o pereche
    comasată. MUTAȚIE: un ghid comasat repus în ghid/ (cu titlul lui) -> grupul reapare -> pică."""
    rows = list(csv.DictReader(io.open(os.path.join(_RAD, "ghid_suprapuneri.csv"), encoding="utf-8")))
    acum = [(str(n), s, t) for n, g in enumerate(sp.grupuri(sp.ghiduri()), 1) for s, t in g]
    assert [(r["grup"], r["slug"], r["titlu"]) for r in rows] == acum, "regenerează: python scripts/scan_ghid_suprapuneri.py --csv"
    comasate = list(csv.DictReader(x for x in io.open(os.path.join(_RAD, "ghid_comasate.csv"), encoding="utf-8") if not x.startswith("#")))
    pereche = {r["comasat"]: r["pastrat"] for r in comasate}
    assert pereche.get("cum-se-calculeaza-adaosul-si-descarcarea-la-un-depozit-en-gros") == "contabilitatea-depozit-en-gros-adaos"


def test_nicio_proza_despre_cod_numita_de_costin():
    """Comanda Costin 13.10.2026 (răspunsul la §6 COMANDA_13_10 pct.2): „fără referiri la cod sau la registrele proiectului.” Tiparele
    numite („comentariul din cod”, „registrul intern al proiectului”, „dosarul tehnic / de cercetare”, „mirrorul local”) și trimiterile
    tehnice (coduri GH, linii de cod, cron, .timer): ZERO în orice ghid, inclusiv în casetele de temei.
    MUTAȚIE: „(verificat pe mirrorul local)” pus înapoi într-o casetă -> pică."""
    rele = []
    for cale in sorted(glob.glob(os.path.join(_RAD, "ghid", "*.md"))):
        z = cc.proza_cod(io.open(cale, encoding="utf-8").read(), cc.PROZA_COD_ZERO)
        if z:
            rele.append((os.path.basename(cale), z[:3]))
    assert rele == [], (len(rele), rele[:5])


def test_proza_despre_cod_clasa_larga_nu_creste():
    """Clasa largă („verificat în cod”, „motorul de calcul”, „cercetarea”, termeni tehnici) — măsurată, la decizia lui Costin; nu
    crește pe niciun ghid (`core/clichet_proza_cod_ghid.json`), un ghid nou pornește de la zero.
    MUTAȚIE: „Verificat în cod:” adăugat într-un ghid -> pică."""
    import json
    pin = json.load(io.open(os.path.join(_RAD, "core", "clichet_proza_cod_ghid.json"), encoding="utf-8"))["fisiere"]
    crescute = []
    for cale in sorted(glob.glob(os.path.join(_RAD, "ghid", "*.md"))):
        s = os.path.basename(cale)[:-3]
        n = len(cc.proza_cod(io.open(cale, encoding="utf-8").read(), cc.PROZA_COD_CLICHET))
        if n > pin.get(s, 0):
            crescute.append((s, pin.get(s, 0), n))
    assert crescute == [], crescute[:10]
