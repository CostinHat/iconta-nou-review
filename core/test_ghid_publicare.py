# -*- coding: utf-8 -*-
"""GARD — site-ul public /ghid/ (comanda Costin 13.10.2026 pct.2c, 2d, 2e, verbatim în DECIZII).

  c) „Adaugă pe fiecare ghid data ultimei actualizări. Nu adăuga autori sau titluri profesionale.”
     -> `.ghid-actualizat` „Actualizat la zz.ll.aaaa” imediat după H1, din `modified` (= `dateModified` = `lastmod` din sitemap).
  d) „Exclude rutele aplicației din indexare (robots.txt + antetul X-Robots-Tag: noindex). Paginile publice rămân indexabile. Verifică
     ca sitemap.xml să conțină doar pagini publice și să nu existe linkuri din paginile publice către rutele aplicației.”
     -> `_edge_canonic_head` pune `X-Robots-Tag: noindex` pe tot ce nu e `_pagina_publica_indexabila`; robots.txt e allow-list-ul ei.
  e) „De acum, nu publici ghiduri noi până la decizia mea.” -> `ghid_publicate.txt`, lista înghețată a celor 6558 de ghiduri publicate
     pe 13.10.2026: un `ghid/*.md` nou nu se servește, nu intră în cuprins, în teme, în ghidurile înrudite și nici în sitemap.
"""
import os
import re
import shutil
from xml.etree import ElementTree as ET

import pytest

NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
#: numărul ghidurilor publicate; se schimbă NUMAI printr-o decizie a lui Costin (pct.2e): 6.558 la înghețare (13.10.2026) -> 6.513 după
#: comasarea celor 45 de grupuri (răspunsul la §6 COMANDA_13_10 pct.1, aceeași zi)
PUBLICATE_LA_INGHETARE = 6513


@pytest.fixture(scope="module")
def c():
    from fastapi.testclient import TestClient
    import main
    return TestClient(main.app), main


def _ancore(html):
    """Destinațiile linkurilor (`<a href>`) din pagină, fără gazda canonică, fără fragment și interogare; externele deoparte."""
    out = []
    for h in re.findall(r'<a\b[^>]*\bhref="([^"]+)"', html):
        p = re.sub(r"^https://iconta\.eu(?=/|$)", "", h) or "/"
        if re.match(r"(https?:|mailto:|tel:|#)", p):
            continue
        out.append(re.split(r"[#?]", p)[0])
    return out


# ── e) publicarea înghețată ─────────────────────────────────────────────────────────────────────────────────────────────────────
def test_publicate_sunt_lista_inghetata(c):
    _cl, main = c
    pub = main._ghid_publicate()
    assert len(pub) == PUBLICATE_LA_INGHETARE
    assert sorted(g["slug"] for g in main._ghid_lista()) == sorted(pub)


def test_un_ghid_nou_nu_se_publica(c, tmp_path, monkeypatch):
    """Un fișier nou în ghid/ (copia unui ghid publicat, alt slug): 404 pe pagină, absent din cuprins, teme și sitemap.
    MUTAȚIA: scoate filtrul `_ghid_publicate()` din `_ghid_lista` / `public_ghid` -> ROȘU."""
    cl, main = c
    d = tmp_path / "ghid"
    shutil.copytree(main._GHID_DIR, d)
    sursa = sorted(main._ghid_publicate())[0]
    shutil.copy(d / (sursa + ".md"), d / "ghid-nou-nepublicat-proba.md")
    monkeypatch.setattr(main, "_GHID_DIR", str(d))
    assert (cl.get("/ghid/ghid-nou-nepublicat-proba").status_code, cl.get("/ghid/" + sursa).status_code) == (404, 200)
    assert [g["slug"] for g in main._ghid_lista() if g["slug"] == "ghid-nou-nepublicat-proba"] == []
    loc = [e.text for e in ET.fromstring(cl.get("/sitemap.xml").content).iter(NS + "loc")]
    assert [u for u in loc if u.endswith("/ghid/ghid-nou-nepublicat-proba")] == []


# ── c) data ultimei actualizări ─────────────────────────────────────────────────────────────────────────────────────────────────
def test_fiecare_ghid_are_data_sub_titlu_fara_autor(c):
    """Pe TOATE ghidurile publicate: exact o dată, imediat după H1, egală cu `dateModified`; niciun autor persoană, niciun titlu
    profesional. MUTAȚIA: scoate linia `.ghid-actualizat` din `public_ghid` -> ROȘU."""
    _cl, main = c
    gresite = []
    for g in main._ghid_lista():
        t = main.public_ghid(g["slug"]).body.decode("utf-8")
        date = re.findall(r'</h1><p class="ghid-actualizat">Actualizat la (\d\d)\.(\d\d)\.(\d{4})</p>', t)
        dm = re.findall(r'"dateModified": "(\d{4})-(\d\d)-(\d\d)', t)
        autori = re.findall(r'"@type": "Person"|\bAutor(?:ul)?\s*:|\b(?:expert contabil|contabil autorizat)\b[^<]{0,40}</p>\s*</main>', t)
        if len(date) != 1 or [x[::-1] for x in date] != dm or autori or len(re.findall(r'class="ghid-actualizat"', t)) != 1:
            gresite.append(g["slug"])
    assert gresite == [], gresite[:10]


# ── d) indexarea ────────────────────────────────────────────────────────────────────────────────────────────────────────────────
PUBLICE = ["/", "/ghid", "/ghid/tema/tva", "/public/termeni", "/robots.txt", "/sitemap.xml", "/sitemap-index.xml",
           "/sitemap-pagini.xml", "/sitemap-ghiduri-1.xml", "/static/stil.css"]
APLICATIE = ["/static/js/app.js", "/public/config", "/tenants/2", "/auth/me", "/depune", "/d406-mapare", "/tva?an=2025",
             "/admin/versiune", "/ghid-inexistent"]


def test_antetul_noindex_numai_pe_rutele_aplicatiei(c):
    """MUTAȚIA: `/tenants` declarat public în `_pagina_publica_indexabila` sau antetul scos din middleware -> ROȘU."""
    cl, main = c
    pub = sorted(main._ghid_publicate())[:3]
    antete = {u: cl.get(u).headers.get("x-robots-tag") for u in PUBLICE + ["/ghid/" + s for s in pub] + APLICATIE}
    assert [u for u, h in antete.items() if h is not None] == APLICATIE, antete
    assert {antete[u] for u in APLICATIE} == {"noindex"}
    assert cl.head("/tenants/2").headers.get("x-robots-tag") == "noindex"


def test_robots_e_allow_listul_suprafetei_publice(c):
    """Fiecare `Allow` din robots.txt e suprafață publică (fără antet), iar `Disallow` acoperă restul."""
    cl, main = c
    t = cl.get("/robots.txt").text
    #: câte o cale reală pentru fiecare regulă `Allow` (prefixele robots.txt -> o pagină servită de sub ele)
    exemplu = {"/$": "/", "/ghid": "/ghid/tema/tva", "/public/termeni": "/public/termeni", "/static/": "/static/stil.css",
               "/sitemap": "/sitemap-index.xml", "/robots.txt": "/robots.txt"}
    #: adresele retrase (410) sunt lăsate accesate ca să se vadă 410 (lotul 9 pct.D2, `core/test_search_console_404.py`); nu sunt suprafață
    retrase = {r for c_ in main.ADRESE_RETRASE for r in (c_ + "$", c_ + "?")}
    allow = [a for a in re.findall(r"^Allow: (\S+)$", t, re.M) if a not in retrase]
    assert sorted(allow) == sorted(exemplu)
    assert [a for a in allow if not main._pagina_publica_indexabila(exemplu[a])] == []
    assert re.findall(r"^Disallow: (\S+)$", t, re.M) == ["/static/js/", "/"]


def test_sitemap_numai_pagini_publice(c):
    cl, main = c
    loc = [e.text for e in ET.fromstring(cl.get("/sitemap.xml").content).iter(NS + "loc")]
    cai = [re.sub(r"^https://iconta\.eu", "", u) or "/" for u in loc]
    assert [p for p in cai if not main._pagina_publica_indexabila(p)] == []
    ghiduri = sorted(p[len("/ghid/"):] for p in cai if re.fullmatch(r"/ghid/(?!tema/)[^/]+", p))
    assert ghiduri == sorted(main._ghid_publicate())


def test_niciun_link_din_paginile_publice_spre_aplicatie(c):
    """Toate paginile publice HTML: landing, cuprinsul, fiecare temă, termenii și FIECARE ghid publicat (cu ghidurile înrudite).
    MUTAȚIA: un link `/tenants` adăugat în `_ghid_legaturi` -> ROȘU."""
    cl, main = c
    from core import ghid_teme as _gt
    pagini = {u: cl.get(u).text for u in ["/", "/ghid", "/public/termeni"] + ["/ghid/tema/" + t[1] for t in _gt.TEME]}
    for g in main._ghid_lista():
        pagini["/ghid/" + g["slug"]] = main.public_ghid(g["slug"]).body.decode("utf-8")
    spre_aplicatie = sorted({(u, a) for u, t in pagini.items() for a in _ancore(t) if not main._pagina_publica_indexabila(a)})
    assert spre_aplicatie == []
    assert len(pagini) > PUBLICATE_LA_INGHETARE


def test_procedura_numara_numai_lista_ordonata():
    """C18 (găsită de Code la captura C17, 13.10.2026): regula veche `.ghid-procedura li::before { content: counter(pas) }` prindea și
    lista cu buline dintr-un bloc de procedură, unde contorul nu crește — „0” la fiecare punct. Orice numerotare prin contor e numai pe
    `ol > li`. MUTAȚIE: regula veche repusă -> pică."""
    css = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "stil.css"), encoding="utf-8").read()
    numerotari = [s.strip() for s, corp in re.findall(r"([^{}]+)\{([^{}]*)\}", css) if re.search(r"content:\s*counter\(", corp)]
    assert numerotari and [s for s in numerotari if not re.search(r"\bol\s*>\s*li::before$", s)] == [], numerotari


# ── comasarea celor 45 de grupuri (răspunsul la §6 COMANDA_13_10 pct.1) ─────────────────────────────────────────────────────────
def _comasate():
    import csv
    cale = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ghid_comasate.csv")
    return [r for r in csv.DictReader(x for x in open(cale, encoding="utf-8") if not x.startswith("#"))]


def test_comasarea_trimite_301_spre_ghidul_pastrat(c):
    """Fiecare ghid comasat: fișierul șters, scos din lista publicată, 301 spre ghidul păstrat (fără lanț), absent din sitemap; ghidul
    păstrat e publicat și răspunde 200. MUTAȚIE: o redirecționare scoasă din `_GHID_REDIRECT` -> pică (404 în loc de 301)."""
    cl, main = c
    rows = _comasate()
    assert len(rows) == 45 and len({r["comasat"] for r in rows}) == 45
    pub = main._ghid_publicate()
    loc = {e.text for e in ET.fromstring(cl.get("/sitemap.xml").content).iter(NS + "loc")}
    rele = []
    for r in rows:
        k, p = r["comasat"], r["pastrat"]
        rr = cl.get("/ghid/" + k, follow_redirects=False)
        stare = (os.path.exists(os.path.join(main._GHID_DIR, k + ".md")), k in pub, rr.status_code, rr.headers.get("location"),
                 main._GHID_BAZA + "/ghid/" + k in loc, p in pub, os.path.exists(os.path.join(main._GHID_DIR, p + ".md")))
        if stare != (False, False, 301, main._GHID_BAZA + "/ghid/" + p, False, True, True):
            rele.append((k, stare))
    assert rele == []
    assert [a for a, b in main._GHID_REDIRECT.items() if b in main._GHID_REDIRECT] == []      # niciun lanț 301 -> 301
