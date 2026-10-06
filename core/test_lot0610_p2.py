# -*- coding: utf-8 -*-
"""GARDA părții 2 din comanda Costin 06.10.2026 — ghidurile /ghid, structură pentru indexare.

  5. „17 URL-uri raportate 404 … Fiecare primește redirecționare permanentă (301) spre ghidul care l-a înlocuit; unde nu există
     înlocuitor, spre pagina-hub a temei.”
  6. „/ghid … se împarte pe teme …; /ghid rămâne cuprinsul temelor.”
  7. „Fiecare ghid primește linkuri spre ghidurile înrudite și spre pagina temei lui.”
  8. „… calea internă de fișier („sursă: anaf_surse/…”) … se înlocuiește cu numele actului normativ și link spre sursa oficială.”
"""
import io
import os
import re

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GHID = os.path.join(RAD, "ghid")


def _client():
    from fastapi.testclient import TestClient
    import main
    return TestClient(main.app), main


def _live():
    return {f[:-3] for f in os.listdir(GHID) if f.endswith(".md")}


def test_nicio_legatura_interna_spre_un_ghid_inexistent():
    """Un link intern spre un slug care nu există și nu e redirecționat = un 404 descoperit de Google (sursa celor raportate).
    MUTAȚIE: un link vechi repus într-o pagină -> pică."""
    import main
    live, rup = _live(), []
    for f in os.listdir(GHID):
        if not f.endswith(".md"):
            continue
        for m in re.finditer(r'/ghid/([a-z0-9-]+)(?=[)"#\s])', io.open(os.path.join(GHID, f), encoding="utf-8").read()):
            s = m.group(1)
            if s != "tema" and s not in live and s not in main._GHID_REDIRECT:
                rup.append("%s -> %s" % (f, s))
    assert not rup, rup[:20]


def test_harta_301_trimite_numai_spre_ghiduri_existente():
    import main
    live = _live()
    rele = {a: b for a, b in main._GHID_REDIRECT.items() if b not in live}
    assert not rele, rele


@pytest.mark.parametrize("adresa, tinta", [
    ("/ghid/esalonare-la-plata-anaf", "https://iconta.eu/ghid/esalonare-la-plata-anaf-2026"),
    ("/ghid/catalogul-mijloacelor-fixe-durate-normale-de-amortizare", "https://iconta.eu/ghid/catalog-mijloace-fixe-durate"),
    ("/ghid/deducere-personala-salarii.md", "https://iconta.eu/ghid/deducere-personala-salarii"),
    ("/ghid/GH-00001", "https://iconta.eu/ghid/plafonul-microintreprinderi-2026"),
    ("/ghid/proba-ghid", "https://iconta.eu/ghid"),
])
def test_adresele_care_au_existat_raspund_301(adresa, tinta):
    """MUTAȚIE: regula pentru „.md” scoasă -> 404 -> pică."""
    c, _m = _client()
    r = c.get(adresa, follow_redirects=False)
    assert (r.status_code, r.headers.get("location")) == (301, tinta)


def test_ghid_e_cuprinsul_temelor_iar_fiecare_tema_are_pagina_ei():
    """MUTAȚIE: lista plată a tuturor ghidurilor repusă pe /ghid -> mii de linkuri -> pică."""
    from core import ghid_teme as gt
    c, main = _client()
    r = c.get("/ghid")
    teme = re.findall(r'href="/ghid/tema/([a-z0-9-]+)"', r.text)
    assert r.status_code == 200 and len(r.content) < 20000, len(r.content)
    assert teme and set(teme) <= {t[1] for t in gt.TEME}
    assert not re.search(r'href="/ghid/(?!tema/)[a-z0-9-]+"', r.text), "cuprinsul temelor nu listează ghiduri"
    _ps, pe_tema = main._ghid_teme_index()
    assert sum(len(v) for v in pe_tema.values()) == len(_live()), "fiecare ghid stă într-o temă"
    for slug in teme:
        assert c.get("/ghid/tema/" + slug).status_code == 200
    s = c.get("/sitemap.xml").text
    assert all(("/ghid/tema/%s</loc>" % t) in s for t in teme)


def test_ghidul_are_tema_si_ghiduri_inrudite():
    """MUTAȚIE: `_ghid_legaturi` scos din pagina ghidului -> pică."""
    from core import ghid_teme as gt
    c, main = _client()
    pe_slug, pe_tema = main._ghid_teme_index()
    r = c.get("/ghid/balanta-impozitul-micro-calculez")
    tema = re.findall(r'class="ghid-tema">Tema: <a href="/ghid/tema/([a-z0-9-]+)"', r.text)
    assert tema == [gt.DUPA_CHEIE[pe_slug["balanta-impozitul-micro-calculez"]["tema"]][1]]
    rel = re.findall(r'<li><a href="/ghid/([a-z0-9-]+)"', r.text.split('class="ghid-legaturi"')[1])
    assert rel == gt.inrudite("balanta-impozitul-micro-calculez", pe_slug, pe_tema) and len(rel) == 6


def test_incadrarea_respecta_registrul_si_regula():
    from core import ghid_teme as gt
    assert gt.incadreaza("orice", "Orice titlu", "salarizare") == "salarizare"
    assert gt.incadreaza("rectificativa-d300-gresita", "Am greșit D300") == "greseli"
    assert gt.incadreaza("x", "Ceva fără cuvinte cunoscute") == "altele"
    # „altele” din registru nu e o încadrare — cade pe regulă. MUTAȚIE: excepția scoasă -> „altele” -> pică.
    assert gt.incadreaza("aflu-clientul-primit-factura-electronica", "Cum aflu dacă clientul a primit factura electronică",
                         "altele") == "spv"


def test_nicio_pagina_de_tema_nu_reface_lista_plata():
    """Tema „Alte teme” avea 1.575 de ghiduri (558 KB) — lista plată mutată pe altă adresă. Plafon: nicio temă peste 800 de
    ghiduri, „Alte teme” sub 10% din total. MUTAȚIE: excepția pentru „altele” scoasă -> 1.575 -> pică."""
    import main
    _ps, pe_tema = main._ghid_teme_index()
    total = sum(len(v) for v in pe_tema.values())
    assert max(len(v) for v in pe_tema.values()) <= 800, {k: len(v) for k, v in pe_tema.items()}
    assert len(pe_tema["altele"]) < total / 10, len(pe_tema["altele"])


#: căi interne care nu au voie să apară pe o pagină publică (pct.8: „calea internă de fișier … se înlocuiește cu numele
#: actului normativ și link spre sursa oficială”); clasa generalizată: orice cale de fișier din depozit sau de pe server
CAI_INTERNE = re.compile(r"anaf_surse|\b(?:core|scripts)/[\w/*.]*|/home/costin|/opt/iconta|scratchpad")
#: domeniile surselor oficiale (Portalul legislativ, ANAF, Monitorul Oficial, ONRC, Ministerul Finanțelor)
OFICIAL = ("legislatie.just.ro", "static.anaf.ro", "www.anaf.ro", "anaf.ro", "monitoruloficial.ro", "www.onrc.ro", "mfinante.gov.ro")


def test_ghidurile_nu_arata_cai_interne_de_fisier():
    """MUTAȚIE: „(sursă: anaf_surse/og_2_2001.html)” repus într-un ghid -> pică."""
    rele = []
    for f in sorted(os.listdir(GHID)):
        if f.endswith(".md"):
            for m in CAI_INTERNE.finditer(io.open(os.path.join(GHID, f), encoding="utf-8").read()):
                rele.append("%s: %s" % (f, m.group(0)))
    assert not rele, (len(rele), rele[:10])


def test_sursa_citata_trimite_la_sursa_oficiala():
    """Fiecare „(sursă: [act](url))” duce la un domeniu oficial. MUTAȚIE: un link de sursă spre alt domeniu -> pică."""
    rele = []
    for f in sorted(os.listdir(GHID)):
        if f.endswith(".md"):
            for u in re.findall(r"[Ss]ursă: \[[^\]]+\]\((https?://[^)/]+)", io.open(os.path.join(GHID, f), encoding="utf-8").read()):
                if u.split("://", 1)[1] not in OFICIAL:
                    rele.append("%s: %s" % (f, u))
    assert not rele, rele[:10]
