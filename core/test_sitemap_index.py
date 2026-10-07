# -*- coding: utf-8 -*-
"""GARD — sitemap-ul în limitele protocolului, numai URL-uri canonice care răspund 200 (comanda Costin 07.10.2026, B).

Măsurat pe 07.10 (jurnalele nginx de la 23.09, IP-urile verificate prin DNS invers + direct): `https://iconta.eu/sitemap.xml`
răspundea 200, `application/xml`, 771.017 octeți, XML valid, 6.581 URL-uri pe `https://iconta.eu`; Google verificat l-a cerut o singură
dată (Inspection Tool, 05.10 13:13, 200), iar fetcher-ul de sitemap-uri NICIODATĂ — „Nu s-a putut prelua” nu corespunde niciunui
răspuns eșuat. Ce era greșit în conținut: un URL redirecționat (`/ghid/cote-tva-2025` -> 301). Acum: indexul `/sitemap-index.xml`
(indicat de `robots.txt`), copiii lui și `/sitemap.xml` din aceeași sursă (`_sitemap_intrari`), fără slug-uri redirecționate.
"""
import re
from xml.etree import ElementTree as ET

import pytest

NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


@pytest.fixture(scope="module")
def c():
    from fastapi.testclient import TestClient
    import main
    return TestClient(main.app), main


def _locuri(xml):
    return [e.text for e in ET.fromstring(xml).iter(NS + "loc")]


def test_robots_indica_indexul_si_il_permite(c):
    cl, main = c
    t = cl.get("/robots.txt").text
    assert re.findall(r"^Sitemap: (\S+)$", t, re.M) == [main._GHID_BAZA + "/sitemap-index.xml"]
    assert re.search(r"^Allow: /sitemap$", t, re.M)


def test_indexul_si_copiii_respecta_protocolul(c):
    """Fiecare copil: 200, XML valid, ≤ 50.000 de URL-uri și ≤ 50 MB; reuniunea copiilor = sitemap-ul plat, fără dubluri."""
    cl, main = c
    r = cl.get("/sitemap-index.xml")
    assert r.status_code == 200 and r.headers["content-type"].startswith("application/xml")
    copii = _locuri(r.content)
    assert copii[0] == main._GHID_BAZA + "/sitemap-pagini.xml" and len(copii) >= 2
    toate = []
    for u in copii:
        rc = cl.get(u.replace(main._GHID_BAZA, ""))
        assert rc.status_code == 200 and len(rc.content) < 50 * 1024 * 1024, u
        loc = _locuri(rc.content)
        assert 0 < len(loc) <= 50000, u
        toate += loc
    plat = _locuri(cl.get("/sitemap.xml").content)
    assert len(toate) == len(set(toate)) and sorted(toate) == sorted(plat)
    assert cl.get("/sitemap-ghiduri-%d.xml" % len(copii)).status_code == 404     # dincolo de ultimul copil: nu există


def test_niciun_url_redirectionat_si_toate_pe_gazda_canonica(c):
    """Un slug redirecționat nu ajunge în sitemap (nu există fișier pentru el — garda de mai jos). MUTAȚIE: `ghid/cote-tva-2025.md`
    pus la loc -> apare în sitemap și pică (ambele teste)."""
    cl, main = c
    loc = _locuri(cl.get("/sitemap.xml").content)
    assert len(loc) > 5000                                            # premisă: ghidurile chiar sunt acolo
    assert all(u.startswith(main._GHID_BAZA + "/") for u in loc)
    slugs = {m.group(1) for m in (re.match(r"^https://[^/]+/ghid/(?!tema/)([a-z0-9-]+)$", u) for u in loc) if m}
    assert sorted(slugs & (set(main._GHID_REDIRECT) | set(main._GHID_REDIRECT_HUB))) == []


def test_un_esantion_raspunde_200_fara_redirect_si_e_autocanonic(c):
    """Fiecare al 50-lea URL + paginile + primul și ultimul ghid: 200 direct (fără 301) și `rel=canonical` = el însuși (unde există).
    Verificarea completă (toate cele ~6.580) s-a făcut la livrare pe serverul viu: 6.580 × 200, 0 canonical diferit."""
    cl, main = c
    loc = _locuri(cl.get("/sitemap.xml").content)
    esantion = sorted(set(loc[::50] + loc[:12] + loc[-2:]))
    for u in esantion:
        r = cl.get(u.replace(main._GHID_BAZA, "") or "/", follow_redirects=False)
        assert r.status_code == 200, (u, r.status_code)
        can = re.search(r'<link rel="canonical" href="([^"]+)"', r.text)
        assert can is None or can.group(1) == u, (u, can.group(1))


def test_nicio_referinta_spre_un_slug_redirectionat(c):
    """Clasa celui de mai sus, măsurată 07.10: 6 link-uri interne din ghiduri, `FUNCTIONALITATI.csv::ghid_slug` și fișierul
    `ghid/cote-tva-2025.md` (servit niciodată: ruta îl redirecționează) trimiteau la un slug redirecționat. Un link intern spre un 301
    e o pagină pe care Google o descoperă și n-o indexează. MUTAȚIE: un `](/ghid/cote-tva-2025)` pus la loc într-un ghid -> pică."""
    import csv, glob, io, os
    _cl, main = c
    red = set(main._GHID_REDIRECT) | set(main._GHID_REDIRECT_HUB)
    linkuri = sorted({(os.path.basename(f), m) for f in glob.glob(os.path.join(main._GHID_DIR, "*.md"))
                      for m in re.findall(r"\]\(/ghid/([a-z0-9-]+)\)", io.open(f, encoding="utf-8").read()) if m in red})
    assert linkuri == []
    rad = os.path.dirname(main._GHID_DIR)
    fc = [r["ghid_slug"] for r in csv.DictReader(io.open(os.path.join(rad, "FUNCTIONALITATI.csv"), encoding="utf-8")) if r.get("ghid_slug") in red]
    assert fc == []
    assert sorted(k for k in red if os.path.isfile(os.path.join(main._GHID_DIR, k + ".md"))) == []
