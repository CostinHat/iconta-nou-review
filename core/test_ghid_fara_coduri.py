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
    """`ghid_suprapuneri.csv` (lista pentru aprobarea comasării) = ce măsoară unealta acum; exemplul din comandă e un grup."""
    rows = list(csv.DictReader(io.open(os.path.join(_RAD, "ghid_suprapuneri.csv"), encoding="utf-8")))
    acum = [(str(n), s, t) for n, g in enumerate(sp.grupuri(sp.ghiduri()), 1) for s, t in g]
    assert [(r["grup"], r["slug"], r["titlu"]) for r in rows] == acum, "regenerează: python scripts/scan_ghid_suprapuneri.py --csv"
    grup = {r["slug"]: r["grup"] for r in rows}
    assert grup["contabilitatea-depozit-en-gros-adaos"] == \
        grup["cum-se-calculeaza-adaosul-si-descarcarea-la-un-depozit-en-gros"]
