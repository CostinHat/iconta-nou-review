# -*- coding: utf-8 -*-
"""GARD P3 · VALUL B — un necunoscut nu se randează ca un „nu". **Pe toate cele șapte ecrane.**

**CE PAZEȘTE.** Ecranele de migrare citesc modelul de citire P2, care spune pentru fiecare firmă în
ce stare e rezumatul ei. Până la valul B, JS-ul o ignora — deci o firmă al cărei rezumat **încă nu
fusese calculat** arăta identic cu una măsurată și găsită goală: *„fără parteneri încă", „de
încărcat"*. Un NECUNOSCUT prezentat ca un NU hotărât (interdicția 32 / R39).

**CUM O PAZEȘTE, și de ce așa.** Nu căutând formulări. Proprietatea apărată nu e *„scrie «încă
necunoscut»"* — aia e o alegere de cuvinte, care se poate schimba mâine fără ca nimic să se strice.
Proprietatea e **DISTINCȚIA**: stările trebuie să producă randări diferite între ele, iar niciuna
dintre cele de neștiut n-are voie să coincidă cu «măsurat și gol». *Se compară randări între ele,
nu randări cu șiruri* — deci garda supraviețuiește oricărei reformulări și cade exact când semantica
se pierde. (METODA §23: structură, nu text.)

**TOATE CELE ȘAPTE, nu una.** Prima formă proba un singur ecran și lăsa restul „prin implementare
comună" — adică pe cuvânt. Ecranele NU sunt identice: `plan-conturi` n-are `are_*`, are o cifră;
`vector` își compune subtitlul din alte câmpuri. O singură probă n-ar fi acoperit nici măcar
formele, darămite comportamentul. *„Aceleași funcții ajutătoare" e o ipoteză despre cod, nu o
proprietate a ecranului.*

Rulează modulele REALE, în chromium, prin cererea reală a fiecărui ecran.
"""
import functools
import http.server
import json
import os
import re
import socketserver
import subprocess
import sys
import threading

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

#: Cele ȘAPTE ecrane care citesc modelul de citire. `strat` e cheia din `STRATURI` (indicele se
#: caută în modul, ca o reordonare să nu ducă proba pe alt ecran); `camp` e steagul „are", sau
#: `None` la ecranul care arată o cifră.
ECRANE = [
    {"nume": "parteneri", "strat": "solduri_parteneri", "ruta": "/migrare/parteneri",
     "camp": "are_parteneri"},
    {"nume": "salariati", "strat": "salariati", "ruta": "/migrare/salariati",
     "camp": "are_salariati"},
    {"nume": "asociati", "strat": "asociati", "ruta": "/migrare/asociati",
     "camp": "are_asociati"},
    {"nume": "mijloace_fixe", "strat": "mijloace_fixe", "ruta": "/migrare/mijloace-fixe",
     "camp": "are_mijloace"},
    {"nume": "solduri", "strat": "solduri", "ruta": "/migrare/solduri", "camp": "are_solduri"},
    {"nume": "vector", "strat": "vector_fiscal", "ruta": "/migrare/vector", "camp": "are_vector"},
    {"nume": "plan_conturi", "strat": "plan_conturi", "ruta": "/migrare/plan-conturi",
     "camp": None, "cifra": "nr_conturi"},
]
NUME = [e["nume"] for e in ECRANE]

#: CELE ȘASE FIRME, una per stare. Cifra e ACEEAȘI (7) la «are date» și la toate cele de neștiut:
#: dacă randarea ar folosi cifra fără să se uite la stare, rândurile ar ieși identice — și proba ar
#: cădea. *Fixtura e construită ca să nu poată trece din întâmplare.*
STARI = [
    ("curent_cu_date", True, 7, {"stare": "curent", "calculat_la": "2026-09-09T10:00:00+03:00"}),
    ("curent_goala", False, 0, {"stare": "curent", "calculat_la": "2026-09-09T10:00:00+03:00"}),
    ("lipseste", False, 0, {"stare": "lipseste", "calculat_la": None}),
    ("invalidat", True, 7, {"stare": "invalidat", "calculat_la": "2026-09-08T10:00:00+03:00"}),
    ("eroare", False, 0, {"stare": "eroare", "calculat_la": "2026-09-09T09:00:00+03:00"}),
    # NEVER_COMPUTED în forma în care chiar ajunge la ecran: câmpul lipsește cu totul.
    ("necalculat", False, 0, None),
]
IDX = {n: i for i, (n, _a, _c, _p) in enumerate(STARI)}


def _firme(ecran):
    """Fixtura ecranului: aceleași șase stări, în câmpurile pe care le citește chiar el."""
    out = []
    for i, (nume, are, cifra, pros) in enumerate(STARI):
        f = {"tenant_id": i + 1, "nume": "%s %s SRL" % (ecran["nume"].upper(), nume.upper()),
             "cui": str(i + 1), "randuri": cifra}
        if ecran["camp"]:
            f[ecran["camp"]] = are
        if ecran.get("cifra"):
            f[ecran["cifra"]] = cifra
        if ecran["nume"] == "vector":     # subtitlul lui se compune din câmpurile astea
            f.update({"regim_fiscal": "micro" if are else None, "platitor_tva": are,
                      "tip_decont": "lunar" if are else None, "operatiuni_ic": False})
        if pros is not None:
            f["prospetime"] = pros
        out.append(f)
    return out


MONTEAZA = """async ([modUrl, cheie]) => {
  const m = await import(modUrl);
  document.body.innerHTML = '<div id="mount"></div>';
  const corp = document.getElementById('mount');
  // Meniul navigheaza prin `nav.deschide(titlu, (corp, nav) => wizard...)`. Un ciot cu
  // `deschide(){}` gol ar inghiti clicul in tacere si proba ar masura un ecran care nu s-a
  // deschis niciodata — exact ce s-a intamplat la prima forma a acestei garzi.
  const nav = { setInapoi(){}, inapoiPas(){},
                deschide(t, fn){ return fn(corp, nav); },
                mergi(t, fn){ return fn(corp, nav); } };
  await m.randeazaMigrare(corp, nav);
  const idx = m.STRATURI.findIndex((s) => s.cheie === cheie);
  if (idx < 0) return { eroare: 'strat inexistent: ' + cheie };
  // `randeazaMigrare` NU e async: se intoarce inainte ca meniul (care asteapta doua cereri) sa
  // existe. Se asteapta APARITIA lui, nu un numar de milisecunde ales din burta.
  const pana = async (cond, cat) => {
    for (let i = 0; i < cat; i++) {
      if (cond()) return true;
      await new Promise((r) => setTimeout(r, 50));
    }
    return false;
  };
  const gata = await pana(() => corp.querySelectorAll('#mig-meniu > *').length > idx, 60);
  if (!gata) return { eroare: 'meniul n-a ajuns la randul ' + idx + ' in 3s' };
  corp.querySelectorAll('#mig-meniu > *')[idx].click();
  const randate = await pana(() => corp.querySelectorAll('.mig-frand').length > 0, 60);
  if (!randate) return { eroare: 'ecranul stratului n-a randat niciun rand in 3s' };
  const randuri = [...corp.querySelectorAll('.mig-frand')].map((el) => ({
    nume: (el.querySelector('.mig-frand-nume') || {}).textContent || '',
    sub: (el.querySelector('.mig-frand-sub') || {}).textContent || '',
    insigna: (el.querySelector('.mig-stare') || {}).textContent || '',
  }));
  const sumar = corp.querySelector('.mig-progres');
  return { randuri, sumar: sumar ? sumar.textContent : null };
}"""


def _lanseaza_chromium(pw):
    """Lansează; dacă nu merge, INSTALEAZĂ și mai încearcă o dată.

    Fără nicio potrivire pe textul excepției: formularea playwright-ului se schimbă între versiuni,
    iar o gardă care depinde de ea ar ceda tăcut la un upgrade — și ar ceda către *skip verde-fals*,
    cel mai prost fel de a ceda."""
    try:
        return pw.chromium.launch()
    except Exception:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=False)
        try:
            return pw.chromium.launch()
        except Exception:
            return None


@pytest.fixture(scope="module")
def randat():
    """Randările celor șase stări, pentru FIECARE dintre cele șapte ecrane. Un singur browser."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.fail("GARD headless nu poate rula: 'playwright' lipseste. NU e skip verde-fals.")

    Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=_RAD)

    class _Srv(socketserver.TCPServer):
        allow_reuse_address = True

    srv = _Srv(("127.0.0.1", 0), Handler)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    pw = sync_playwright().start()
    br = _lanseaza_chromium(pw)
    if br is None:
        pw.stop(); srv.shutdown()
        pytest.fail("GARD headless nu poate rula: chromium indisponibil. NU e skip verde-fals.")

    tot = {}
    try:
        for ecran in ECRANE:
            #: Răspunsurile ciotului, pe CALEA cererii. Un dicționar pe cale exactă, nu o scară de
            #: `in url`: `"/migrare/status" in url` ar prinde și `/migrare/status-vechi`, iar
            #: dispecerul ar servi tăcut altceva decât crede proba.
            raspunsuri = {ecran["ruta"]: {"firme": _firme(ecran)},
                          "/migrare/status": {"status": {}},
                          "/tenants": {"tenants": []}}

            def ruteaza(route, request, _r=raspunsuri):
                from urllib.parse import urlparse
                cale = urlparse(request.url).path.rstrip("/") or "/"
                route.fulfill(status=200, content_type="application/json",
                              body=json.dumps(_r.get(cale, {}), ensure_ascii=False))

            pg = br.new_page()
            for tipar in ("**/migrare/**", "**/tenants", "**/tenants?*"):
                pg.route(tipar, ruteaza)
            pg.goto("http://127.0.0.1:%d/static/" % port)
            rez = pg.evaluate(MONTEAZA, ["/static/js/ecrane/migrare.js", ecran["strat"]])
            pg.close()
            assert not rez.get("eroare"), "%s: %s" % (ecran["nume"], rez.get("eroare"))
            assert len(rez["randuri"]) == len(STARI), (
                "[anti-vacuu] %s a randat %d rânduri din %d — proba n-ar măsura ce cred"
                % (ecran["nume"], len(rez["randuri"]), len(STARI)))
            tot[ecran["nume"]] = rez
        assert set(tot) == set(NUME), "n-au fost randate toate ecranele: %s" % sorted(tot)
        yield tot
    finally:
        br.close(); pw.stop(); srv.shutdown()


def _r(randat, ecran, stare):
    """Randarea unei stări, ca pereche (subtitlu, insignă) — asta VEDE omul."""
    x = randat[ecran]["randuri"][IDX[stare]]
    return (x["sub"].strip(), x["insigna"].strip())


# ============================================================================
#  CELE CINCI ASERȚIUNI CERUTE, fiecare ca DISTINCȚIE, pe fiecare ecran
# ============================================================================
@pytest.mark.parametrize("ecran", NUME)
def test_MISSING_nu_se_randeaza_ca_gol(randat, ecran):
    """`MISSING_IS_NOT_RENDERED_AS_EMPTY`, pe fiecare ecran."""
    assert _r(randat, ecran, "lipseste") != _r(randat, ecran, "curent_goala"), (
        "%s: «lipsește» și «măsurat și gol» se randează identic: %r — un necunoscut arătat ca un nu"
        % (ecran, _r(randat, ecran, "lipseste")))


@pytest.mark.parametrize("ecran", NUME)
def test_NEVER_COMPUTED_nu_se_randeaza_ca_gol(randat, ecran):
    """`NEVER_COMPUTED_IS_NOT_RENDERED_AS_EMPTY` — firma fără niciun câmp de prospețime."""
    assert _r(randat, ecran, "necalculat") != _r(randat, ecran, "curent_goala"), (
        "%s: «niciodată calculat» și «măsurat și gol» se randează identic: %r"
        % (ecran, _r(randat, ecran, "necalculat")))


@pytest.mark.parametrize("ecran", NUME)
def test_INVALIDATED_nu_se_randeaza_ca_CURENT(randat, ecran):
    """`INVALIDATED_IS_NOT_RENDERED_AS_CURRENT`. Firma are o valoare veche și sursa s-a schimbat de
    atunci: valoarea veche nu se arată drept curentă — nici ca «are», nici ca «n-are»."""
    inv = _r(randat, ecran, "invalidat")
    assert inv != _r(randat, ecran, "curent_cu_date"), (
        "%s: «invalidat» se randează exact ca «curent cu date»: %r — stale arătat drept current"
        % (ecran, inv))
    assert inv != _r(randat, ecran, "curent_goala"), (
        "%s: «invalidat» se randează exact ca «curent și gol»: %r" % (ecran, inv))


@pytest.mark.parametrize("ecran", NUME)
def test_ERROR_nu_se_randeaza_ca_gol(randat, ecran):
    """`ERROR_IS_NOT_RENDERED_AS_EMPTY`."""
    assert _r(randat, ecran, "eroare") != _r(randat, ecran, "curent_goala"), (
        "%s: «eroare» și «măsurat și gol» se randează identic: %r"
        % (ecran, _r(randat, ecran, "eroare")))


@pytest.mark.parametrize("ecran", NUME)
def test_CURENT_gol_ramane_gol(randat, ecran):
    """`CURRENT_EMPTY_REMAINS_EMPTY`. **Direcția a doua**, fără de care toate cele de sus s-ar putea
    trece arătând „necunoscut" la TOATĂ lumea."""
    gol = _r(randat, ecran, "curent_goala")
    assert gol != _r(randat, ecran, "curent_cu_date"), (
        "%s: «gol» și «are date» se randează identic: %r" % (ecran, gol))
    for stare in ("lipseste", "invalidat", "eroare", "necalculat"):
        assert gol != _r(randat, ecran, stare), (
            "%s: «măsurat și gol» a fost înghițit de starea %r: %r" % (ecran, stare, gol))


@pytest.mark.parametrize("ecran", NUME)
def test_starile_sunt_DISTINCTE_intre_ele(randat, ecran):
    """Matricea întreagă: fiecare stare își are randarea ei.

    `lipseste` și `necalculat` SUNT aceeași stare în model — se așteaptă să arate la fel, și se
    scrie aici ca să fie o alegere, nu o scăpare."""
    toate = {s: _r(randat, ecran, s) for s in IDX if s != "necalculat"}
    perechi = [(a, b) for a in toate for b in toate if a < b and toate[a] == toate[b]]
    assert not perechi, "%s: stări care se randează identic: %s" % (
        ecran, [(a, b, toate[a]) for a, b in perechi])


# ============================================================================
#  SUMARUL — numai ecranele care au unul
# ============================================================================
@pytest.mark.parametrize("ecran", [e["nume"] for e in ECRANE if e["camp"]])
def test_sumarul_nu_topeste_necunoscutul_in_numitor(randat, ecran):
    """*„1 din 6"* ar spune că toate șase au fost evaluate. Când patru n-au fost, minte.

    Se verifică prin CIFRE, nu prin formulare: fixtura are 1 firmă CURENT cu date · 1 CURENT și
    goală · 4 de neștiut. Un `2` ar însemna că firma `invalidat` — care poartă o valoare veche — a
    fost numărată printre cele curente."""
    sumar = (randat[ecran]["sumar"] or "").strip()
    assert sumar, "%s: [anti-vacuu] ecranul n-a randat niciun sumar" % ecran
    cifre = [int(x) for x in re.findall(r"\d+", sumar)]
    assert sorted(cifre) == [1, 1, 4], (
        "%s: sumarul nu conține numărătorile [1 cu · 1 fără · 4 necunoscute]: %r -> %s"
        % (ecran, sumar, cifre))
    assert 6 not in cifre, (
        "%s: sumarul folosește totalul (6) ca numitor, deci pretinde că toate au fost evaluate: %r"
        % (ecran, sumar))
