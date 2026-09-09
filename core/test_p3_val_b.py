# -*- coding: utf-8 -*-
"""GARD P3 · VALUL B — un necunoscut nu se randează ca un „nu".

**CE PAZEȘTE.** Ecranele de migrare citesc modelul de citire P2, care spune pentru fiecare firmă
în ce stare e rezumatul ei. Până la valul B, JS-ul ignora starea — deci o firmă al cărei rezumat
**încă nu fusese calculat** arăta identic cu una măsurată și găsită goală: *„fără parteneri încă",
„de încărcat"*. Un NECUNOSCUT prezentat ca un NU hotărât (interdicția 32 / R39).

**CUM O PAZEȘTE, și de ce așa.** Nu căutând formulări. Proprietatea apărată nu e *„scrie «încă
necunoscut»"* — aia e o alegere de cuvinte, care se poate schimba mâine fără ca nimic să se strice.
Proprietatea e **DISTINCȚIA**: cele cinci stări trebuie să producă cinci randări diferite între
ele, iar niciuna dintre cele trei stări de neștiut n-are voie să coincidă cu «măsurat și gol».
*Se compară randări între ele, nu randări cu șiruri* — deci garda supraviețuiește oricărei
reformulări și cade exact când semantica se pierde. (METODA §23: structură, nu text.)

Rulează modulul REAL, în chromium, prin cererea reală a ecranului — nu o reimplementare a lui.
"""
import functools
import http.server
import json
import os
import socketserver
import subprocess
import sys
import threading

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

#: Al patrulea strat din meniu („Solduri parteneri"). Indicele vine din `STRATURI`, citit de
#: gardă din modul — nu scris aici, ca o reordonare a straturilor să nu ducă proba pe alt ecran.
STRAT_CHEIE = "solduri_parteneri"

#: CELE CINCI STĂRI, fiecare cu firma ei. `randuri` e ACELAȘI (7) la nonempty și la toate cele
#: neștiute: dacă randarea ar folosi cifra fără să se uite la stare, rândurile ar ieși identice
#: — și proba ar cădea. *Fixtura e construită ca să nu poată trece din întâmplare.*
FIRME = [
    {"tenant_id": 1, "nume": "CURENT CU DATE SRL", "cui": "1", "are_parteneri": True,
     "randuri": 7, "prospetime": {"stare": "curent", "calculat_la": "2026-09-09T10:00:00+03:00"}},
    {"tenant_id": 2, "nume": "CURENT SI GOALA SRL", "cui": "2", "are_parteneri": False,
     "randuri": 0, "prospetime": {"stare": "curent", "calculat_la": "2026-09-09T10:00:00+03:00"}},
    {"tenant_id": 3, "nume": "LIPSESTE SRL", "cui": "3", "are_parteneri": False,
     "randuri": 0, "prospetime": {"stare": "lipseste", "calculat_la": None}},
    {"tenant_id": 4, "nume": "INVALIDAT SRL", "cui": "4", "are_parteneri": True,
     "randuri": 7, "prospetime": {"stare": "invalidat", "calculat_la": "2026-09-08T10:00:00+03:00"}},
    {"tenant_id": 5, "nume": "EROARE SRL", "cui": "5", "are_parteneri": False,
     "randuri": 0, "prospetime": {"stare": "eroare", "calculat_la": "2026-09-09T09:00:00+03:00"}},
    # NEVER_COMPUTED, în forma în care chiar ajunge la ecran: ruta n-a găsit rând, deci n-a pus
    # deloc câmpul. Dacă JS-ul ar citi `prospetime.stare` fără apărare, aici ar arunca sau ar
    # cădea pe „curent" — și firma ar apărea ca «măsurată și goală».
    {"tenant_id": 6, "nume": "NECALCULAT NICIODATA SRL", "cui": "6", "are_parteneri": False,
     "randuri": 0},
]
IDX = {"curent_cu_date": 0, "curent_goala": 1, "lipseste": 2, "invalidat": 3, "eroare": 4,
       "necalculat": 5}

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
    clasa: (el.querySelector('.mig-stare') || {}).className || '',
  }));
  const sumar = corp.querySelector('.mig-progres');
  return { randuri, sumar: sumar ? sumar.textContent : null };
}"""


#: Răspunsurile ciotului, pe CALEA cererii. Un dicționar pe cale exactă, nu o scară de `in url`:
#: `"/migrare/status" in url` ar prinde și `/migrare/status-vechi`, iar dispecerul ar servi tăcut
#: altceva decât crede proba. *Calea se ia din URL-ul PARSAT, nu dintr-o potrivire de șir.*
_RASPUNSURI = {
    "/migrare/parteneri": lambda: {"firme": FIRME},
    "/migrare/status": lambda: {"status": {}},
    "/tenants": lambda: {"tenants": []},
}


def _ruteaza(route, request):
    from urllib.parse import urlparse
    cale = urlparse(request.url).path.rstrip("/") or "/"
    fac = _RASPUNSURI.get(cale)
    corp = fac() if fac else {}
    route.fulfill(status=200, content_type="application/json",
                  body=json.dumps(corp, ensure_ascii=False))


def _lanseaza_chromium(pw):
    """Lansează; dacă nu merge, INSTALEAZĂ și mai încearcă o dată.

    Fără nicio potrivire pe textul excepției: formularea playwright-ului („executable doesn't
    exist", „please run install"…) se schimbă între versiuni, iar o gardă care depinde de ea ar
    ceda tăcut la un upgrade — și ar ceda către *skip verde-fals*, cel mai prost fel de a ceda.
    Instalarea e idempotentă și ieftină când binarul e deja acolo, deci încercarea a doua nu costă
    nimic în cazul normal."""
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
    """Randările celor șase firme, o dată — proba e despre ele, nu despre browser."""
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
    try:
        pg = br.new_page()
        # NUMAI rutele de date. Un `**/*` ar prinde și modulul JS și l-ar servi ca `{}` —
        # ecranul n-ar mai exista, iar proba ar muri fără să spună de ce.
        for tipar in ("**/migrare/**", "**/tenants", "**/tenants?*"):
            pg.route(tipar, _ruteaza)
        pg.goto("http://127.0.0.1:%d/static/" % port)
        rez = pg.evaluate(MONTEAZA, ["/static/js/ecrane/migrare.js", STRAT_CHEIE])
        assert not rez.get("eroare"), rez.get("eroare")
        assert len(rez["randuri"]) == len(FIRME), (
            "[anti-vacuu] s-au randat %d rânduri din %d — proba n-ar măsura ce cred"
            % (len(rez["randuri"]), len(FIRME)))
        for i, f in enumerate(FIRME):
            assert f["nume"] in rez["randuri"][i]["nume"], (
                "rândul %d nu e firma așteptată — indicii de mai jos ar arăta altceva" % i)
        yield rez
    finally:
        br.close(); pw.stop(); srv.shutdown()


def _randare(rez, cheie):
    """Randarea unei firme, ca pereche (subtitlu, insignă) — asta VEDE omul."""
    r = rez["randuri"][IDX[cheie]]
    return (r["sub"].strip(), r["insigna"].strip())


# ============================================================================
#  CELE CINCI ASERȚIUNI CERUTE, fiecare ca DISTINCȚIE
# ============================================================================
def test_MISSING_nu_se_randeaza_ca_gol(randat):
    """`MISSING_IS_NOT_RENDERED_AS_EMPTY`. O firmă al cărei rezumat lipsește n-are voie să arate
    ca una măsurată și găsită goală."""
    assert _randare(randat, "lipseste") != _randare(randat, "curent_goala"), (
        "«lipsește» și «măsurat și gol» se randează identic: %r — un necunoscut arătat ca un nu"
        % (_randare(randat, "lipseste"),))


def test_NEVER_COMPUTED_nu_se_randeaza_ca_gol(randat):
    """`NEVER_COMPUTED_IS_NOT_RENDERED_AS_EMPTY`. Firma fără niciun câmp de prospețime — forma în
    care chiar ajunge la ecran când modelul n-a calculat-o niciodată."""
    assert _randare(randat, "necalculat") != _randare(randat, "curent_goala"), (
        "«niciodată calculat» și «măsurat și gol» se randează identic: %r"
        % (_randare(randat, "necalculat"),))


def test_INVALIDATED_nu_se_randeaza_ca_CURENT(randat):
    """`INVALIDATED_IS_NOT_RENDERED_AS_CURRENT`. Firma are o valoare veche (7 parteneri) și sursa
    s-a schimbat de atunci. Valoarea veche NU se arată drept curentă — nici ca «are», nici ca
    «n-are»."""
    inv = _randare(randat, "invalidat")
    assert inv != _randare(randat, "curent_cu_date"), (
        "«invalidat» se randează exact ca «curent cu date»: %r — stale arătat drept current" % (inv,))
    assert inv != _randare(randat, "curent_goala"), (
        "«invalidat» se randează exact ca «curent și gol»: %r" % (inv,))


def test_ERROR_nu_se_randeaza_ca_gol(randat):
    """`ERROR_IS_NOT_RENDERED_AS_EMPTY`. Ultima încercare a eșuat: nu se știe, și nu se pretinde
    altceva."""
    assert _randare(randat, "eroare") != _randare(randat, "curent_goala"), (
        "«eroare» și «măsurat și gol» se randează identic: %r" % (_randare(randat, "eroare"),))


def test_CURENT_gol_ramane_gol(randat):
    """`CURRENT_EMPTY_REMAINS_EMPTY`. **Direcția a doua**, fără de care toate cele de sus s-ar
    putea trece arătând „necunoscut" la TOATĂ lumea. O firmă chiar măsurată și chiar goală trebuie
    să rămână distinctă și de «are date», și de fiecare stare de neștiut."""
    gol = _randare(randat, "curent_goala")
    assert gol != _randare(randat, "curent_cu_date"), (
        "«gol» și «are 7 parteneri» se randează identic: %r" % (gol,))
    for cheie in ("lipseste", "invalidat", "eroare", "necalculat"):
        assert gol != _randare(randat, cheie), (
            "«măsurat și gol» a fost înghițit de starea %r: %r" % (cheie, gol))


def test_cele_cinci_stari_sunt_DISTINCTE_intre_ele(randat):
    """Proprietatea întreagă, dintr-o bucată: fiecare stare își are randarea ei.

    Cele patru probe de mai sus sunt perechile pe care le-a cerut comanda; asta e matricea. Dacă
    două stări oarecare ajung să arate la fel, omul nu le mai poate deosebi — indiferent care
    două."""
    toate = {c: _randare(randat, c) for c in IDX}
    # `lipseste` și `necalculat` SUNT aceeași stare în model (`lipseste`) — se așteaptă să arate
    # la fel, și se scrie aici ca să fie o alegere, nu o scăpare.
    toate.pop("necalculat")
    perechi = [(a, b) for a in toate for b in toate if a < b and toate[a] == toate[b]]
    assert not perechi, "stări care se randează identic: %s" % [
        (a, b, toate[a]) for a, b in perechi]


def test_sumarul_nu_topeste_necunoscutul_in_numitor(randat):
    """*„7 din 14"* spune că toate 14 au fost evaluate. Când patru n-au fost, minte.

    Se verifică prin CIFRE, nu prin formulare: numărul firmelor cu parteneri (1) și numărul celor
    necunoscute (4) trebuie amândouă să apară în sumar, iar numărul total (6) NU are voie să apară
    ca numitor al celor cu parteneri."""
    import re
    sumar = (randat["sumar"] or "").strip()
    assert sumar, "[anti-vacuu] ecranul n-a randat niciun sumar"
    cifre = [int(x) for x in re.findall(r"\d+", sumar)]
    # Fixtura: 1 firmă CURENT cu parteneri · 1 CURENT și goală · 4 de neștiut
    # (lipseste, invalidat, eroare, necalculat). Se cer CIFRELE, nu formularea.
    assert sorted(cifre) == [1, 1, 4], (
        "sumarul nu conține exact numărătorile așteptate [1 cu · 1 fără · 4 necunoscute]: "
        "%r -> %s" % (sumar, cifre))
    # Firma `invalidat` are `are_parteneri = true` cu o valoare veche. Dacă agregatul ar număra-o,
    # ar apărea un 2 — o valoare care nu mai e curentă, afirmată drept curentă.
    assert 2 not in cifre, (
        "sumarul numără o firmă `invalidat` printre cele cu parteneri: %r" % sumar)
    assert 6 not in cifre, (
        "sumarul folosește totalul (6) ca numitor, deci pretinde că toate au fost evaluate: %r"
        % sumar)
