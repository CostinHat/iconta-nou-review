# -*- coding: utf-8 -*-
"""GARD — citatele din casetele de temei ale ghidurilor publice se regăsesc LITERAL în sursele oficiale locale (`core/ghid_citate.py`).

Comanda Costin 13.10.2026 (răspunsul la §6 al raportului COMANDA_13_10, pct.3, verbatim în DECIZII): „pune temeiul din lege, citat
verbatim din sursă verificată. Unde nu există normă aplicabilă, nu pune caseta. Nu inventa temeiuri.”

CE FACE IMPOSIBIL: (1) un ghid nou sau o casetă nouă cu un citat care nu e în textul legii; (2) creșterea, în orice ghid, a numărului
de citate neregăsite. Clichetul e PE FIȘIER (`core/clichet_citate_ghid.json`), un ghid absent din el pornește de la zero — cele 71 de
ghiduri care au primit temeiul la 13.10.2026 sunt la zero. CE NU VEDE: că articolul numit lângă citat e cel din care provine textul
(atribuirea) — o recitire, nu o potrivire de text. Citatele vechi neregăsite (măsurate în clichet) așteaptă decizia lui Costin.
"""
import glob
import io
import json
import os

from core import ghid_citate as gc

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLICHET = os.path.join(RAD, "core", "clichet_citate_ghid.json")


def test_CALIBRARE_citatul_literal_trece_iar_cel_modificat_pica():
    """Un fragment luat literal din Codul fiscal (cu ghilimele interioare, spațiu de portal înaintea punctuației) trece; același
    fragment cu un cuvânt adăugat pică; un citat cu omisiune „[...]” se verifică pe fiecare parte."""
    sursa = 'cazul în care clientul este persoana obligată la plata TVA, mențiunea "taxare inversă"'
    caseta = "::: ghid-temei\n„%s”\n— CF\n:::\n"
    assert gc.citate(caseta % sursa) == [sursa]
    assert (gc.neregasite(caseta % sursa), gc.neregasite(caseta % (sursa + " obligatorie"))) == ([], [sursa + " obligatorie"])
    omis = "Sunt considerate venituri din salarii toate veniturile în bani [...] și cele care nu există în lege niciodată"
    assert gc.neregasite(caseta % omis) == [omis]


def _acum():
    out = {}
    for f in sorted(glob.glob(os.path.join(RAD, "ghid", "*.md"))):
        n = len(gc.neregasite(io.open(f, encoding="utf-8").read()))
        if n:
            out[os.path.basename(f)[:-3]] = n
    return out


def test_niciun_ghid_nu_are_mai_multe_citate_neregasite():
    """MUTAȚIE: un citat modificat într-o casetă a unui ghid de la zero -> pică."""
    pin = json.load(io.open(CLICHET, encoding="utf-8"))["fisiere"]
    acum = _acum()
    crescute = sorted((s, pin.get(s, 0), n) for s, n in acum.items() if n > pin.get(s, 0))
    assert crescute == [], crescute[:10]


def test_citatele_din_caseta_sunt_paragrafe_separate():
    """Într-o casetă cu mai multe citate, după rândul de sursă („— act … (sursă: …)”) vine un rând liber, altfel markdown lipește
    sursa de citatul următor într-un singur paragraf (văzut la captura lotului, 13.10.2026: 302 locuri în 201 de ghiduri).
    MUTAȚIE: rândul liber scos dintr-o casetă cu două citate -> pică."""
    import re
    lipite = []
    for f in sorted(glob.glob(os.path.join(RAD, "ghid", "*.md"))):
        for b in re.findall(r"^:::\s*ghid-temei[^\n]*\n(.*?)^:::\s*$", io.open(f, encoding="utf-8").read(), re.S | re.M):
            r = b.splitlines()
            lipite += [os.path.basename(f) for a, c in zip(r, r[1:])
                       if a.lstrip().startswith(("—", "–")) and c.strip() and not c.lstrip().startswith(("—", "–"))]
    assert lipite == [], (len(lipite), lipite[:5])


def test_CALIBRARE_poarta_de_publicare_opreste_un_ghid_nou_cu_citat_inventat(tmp_path):
    """Verificarea e LEGATĂ în poarta de pre-publicare (`core/ghid_poarta.verifica_ghid`): un ghid nou (fără loc în clichet) cu un
    citat care nu e în lege e oprit; același ghid cu citatul literal trece. MUTAȚIE: verificarea scoasă din poartă -> pică."""
    from core import ghid_poarta as gp
    sursa = 'cazul în care clientul este persoana obligată la plata TVA, mențiunea "taxare inversă"'
    corp = "---\ntitle: Proba\ndescription: Proba\npoarta: v1\n---\n\n# Proba\n\n::: ghid-temei\n„%s”\n:::\n"
    rau, bun = tmp_path / "ghid-proba-citat-inventat.md", tmp_path / "ghid-proba-citat-literal.md"
    rau.write_text(corp % (sursa + " de două ori"), encoding="utf-8")
    bun.write_text(corp % sursa, encoding="utf-8")
    (ok_rau, mes_rau), (ok_bun, _m) = gp.verifica_ghid(str(rau), set(), {}), gp.verifica_ghid(str(bun), set(), {})
    assert (ok_rau, ok_bun, len([m for m in mes_rau if m.startswith("CITAT ")])) == (False, True, 1)
