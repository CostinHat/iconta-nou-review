# -*- coding: utf-8 -*-
"""Lotul 17.5-S — pozițiile Pilot deschise pe ecran: ce vede contabilul, cu textele, formatele și cifrele impuse de comandă.

Temei: N/A — texte și afișări de interfață (DS cap.4, cap.9); cifrele statului de plată și textul notei Z vin din aceleași funcții ca ecranul.
Ecranele reale rulează în Chromium (serverul de fișiere statice al depozitului; API-ul simulat cu `page.route`); numai ce nu e ecran (titlul
notei, textul mesajelor serverului) se judecă direct în Python. Fiecare test numește MUTAȚIA care îl face să pice.
"""
import functools
import http.server
import json
import os
import socketserver
import threading
from urllib.parse import urlparse

import pytest

from core import capital_social as cs
from core import jurnal_api

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: răspunsurile API-ului simulat, pe cale; un test le schimbă înainte să deschidă ecranul
RASP = {}


def _handler(route, request):
    cale = urlparse(request.url).path
    r = RASP.get(cale)
    if r is None:
        route.fulfill(status=404, content_type="application/json", body="{}")
    elif callable(r):
        r(route, request)
    else:
        route.fulfill(status=200, content_type="application/json", body=json.dumps(r))


@pytest.fixture(scope="module")
def pagina():
    from playwright.sync_api import sync_playwright
    from core.test_emitere_randuri_dinamice import _lanseaza_chromium
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=_RAD))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    pw = sync_playwright().start()
    br = _lanseaza_chromium(pw)
    if br is None:
        pw.stop()
        srv.shutdown()
        pytest.fail("GARD headless nu poate rula: chromium indisponibil. NU e skip verde-fals.")
    pg = br.new_page()
    pg.route("**/tenants/**", _handler)
    pg.route("**/notificari/**", _handler)
    pg.route("**/coada", _handler)
    pg.goto("http://127.0.0.1:%d/static/" % srv.server_address[1])
    try:
        yield pg
    finally:
        br.close()
        pw.stop()
        srv.shutdown()


NAV = """const nav = { deschide(t, f) { const d = document.createElement('div'); document.body.appendChild(d); f(d, nav); }, inapoi() {}, inapoiPas() {}, mergi() {}, setInapoi() {} };"""


# ── (i) 640.1: fișa partenerului o singură dată pentru client și furnizor ────────────────────────────────────────────────
def _fisa(pg, fise):
    RASP["/tenants/7/parteneri-firma/fisa"] = {"nume": "DANTE INTERNATIONAL SA", "cui": "14399840", "rol": "client și furnizor", "fise": fise,
                                               "sold": {"conturi": []}, "documente": []}
    return pg.evaluate("""async () => {
      const m = await import('/static/js/ecrane/clienti_ecran.js');
      document.body.innerHTML = '<div id="mount"></div>';
      %s
      await m.ecranFisaPartener(document.getElementById('mount'), nav, { id: 7, regim_contabil: 'dubla' }, 'k');
      return [...document.querySelectorAll('#mount .pf-frand')].map((e) => e.innerText.replace(/\\s+/g, ' ').trim());
    }""" % NAV)


def _fise(**diferit_furnizor):
    comun = {"nume": "DANTE INTERNATIONAL SA", "adresa": "Str. Exemplului 1", "oras": "Sector 2 Mun. București", "judet": "B", "email": "", "telefon": ""}
    return [dict(comun, fel="clienti", id=1, afiliat=True), dict(comun, fel="furnizori", id=1, **diferit_furnizor)]


def test_fisa_client_si_furnizor_cu_aceleasi_date_e_o_singura_casuta(pagina):
    """640.1: clientul și furnizorul cu aceleași date -> o casetă «Fișa de client și de furnizor: …», adresa o singură dată, bifa de afiliere rămâne.
    MUTAȚIE: `fiseDeAfisat` întoarce mereu ambele fișe -> două casete, adresa de două ori -> pică."""
    casete = _fisa(pagina, _fise())
    assert len(casete) == 1, casete
    assert casete[0].startswith("Fișa de client și de furnizor: DANTE INTERNATIONAL SA"), casete
    assert casete[0].count("Str. Exemplului 1") == 1 and "persoană afiliată" in casete[0], casete
    assert "Fișa de furnizor" not in casete[0]


def test_fisa_cu_date_diferite_ramane_pe_doua_casete(pagina):
    """640.1: când adresa (sau orașul, județul, emailul, telefonul) diferă, rămân două casete, ca până acum, fiecare cu datele ei.
    MUTAȚIE: compararea câmpurilor scoasă (se unește mereu) -> o casetă care ascunde adresa furnizorului -> pică."""
    casete = _fisa(pagina, _fise(adresa="Str. Altfel 9"))
    assert [c.split(":")[0] for c in casete] == ["Fișa de client", "Fișa de furnizor"], casete
    assert "Str. Exemplului 1" in casete[0] and "Str. Altfel 9" in casete[1], casete


# ── (ii) 563: clopoțelul — N notele de validat, singular/plural, insigna = necitite + de validat ─────────────────────────
_BARA = """async () => {
  document.body.innerHTML = '<div id="bara"><button id="nav-clopot"><span id="nav-clopot-badge"></span></button></div>';
  const { urmaresteClopotul } = await import('/static/js/navigator.js');
  await urmaresteClopotul(document.getElementById('bara'))(false);
  return document.getElementById('nav-clopot-badge').textContent;
}"""


def _nota(membri=None):
    return {"fel": "nota", "stare": "la_senior", "id": 1, "membri_ids": membri or []}


def test_insigna_clopotelului_e_necitite_plus_note_de_validat(pagina):
    """563: 2 necitite + 3 note de validat (un document cu 2 note + o notă) = 5, cu aceeași numărătoare ca cifra cardului (`noteDeValidatInCoada`).
    Declarațiile din coadă nu se numără. MUTAȚIE: insigna numără elementele cozii (2), nu notele (3) -> 4 -> pică."""
    RASP["/notificari/contor"] = {"ok": True, "necitite": 2}
    RASP["/coada"] = {"coada": [_nota([1, 2]), _nota(), {"fel": "d300", "stare": "la_senior"}]}
    assert pagina.evaluate(_BARA) == "5"


def test_insigna_arata_numai_necititele_cand_coada_nu_se_poate_citi(pagina):
    """563: dacă GET /coada eșuează, insigna arată ca azi numai necititele; nimic nu se ascunde. MUTAȚIE: eroarea cozii ascunde insigna -> pică."""
    RASP["/notificari/contor"] = {"ok": True, "necitite": 2}
    RASP["/coada"] = lambda route, req: route.fulfill(status=500, content_type="application/json", body="{}")
    assert pagina.evaluate(_BARA) == "2"


def test_randul_din_clopotel_la_singular_si_plural(pagina):
    """563: «1 notă de validat», «6 note de validat», «20 de note de validat» (regula lui `cate`). MUTAȚIE: pluralul fix «note» -> «1 note» -> pică."""
    r = pagina.evaluate("""async () => { const { textNoteDeValidat } = await import('/static/js/navigator.js'); return [1, 6, 20].map(textNoteDeValidat); }""")
    assert r == ["1 notă de validat", "6 note de validat", "20 de note de validat"], r


# ── (iii) 738: pastila «fără scadență»; suma pastilelor = rândurile listei ────────────────────────────────────────────────
def _linie(stare, nr):
    return {"factura_id": nr, "numar": "F%d" % nr, "tert": "Client %d" % nr, "suma": 100, "rest": 100, "stare": stare, "zile": None,
            "data_scadenta": None, "data_emitere": "2026-10-01", "cui": "1", "moneda": "RON"}


def test_pastila_fara_scadenta_si_suma_pastilelor_e_numarul_randurilor(pagina):
    """738: a patra pastilă, ultima, «<N> fără scadență» (N = rezumat.fara_scadenta); restanțe + scadențe + în termen + fără scadență = rândurile listei.
    MUTAȚIE: pastila scoasă -> suma pastilelor 3 față de 4 rânduri -> pică."""
    linii = [_linie("restanta", 1), _linie("in_termen", 2), _linie("fara_scadenta", 3), _linie("fara_scadenta", 4)]
    RASP["/tenants/7/scadentar"] = {"linii": linii, "rezumat": {"restanta": 1, "scade_curand": 0, "in_termen": 1, "fara_scadenta": 2}, "clienti": [], "optin": False}
    r = pagina.evaluate("""async () => {
      const m = await import('/static/js/ecrane/facturi_ecran.js');
      document.body.innerHTML = '<div id="mount"></div>';
      %s
      await m.scadentarEcran(document.getElementById('mount'), nav, 7, {});
      return [[...document.querySelectorAll('#mount .cf-sumar .cf-pastila')].map((e) => e.innerText.trim()), document.querySelectorAll('#sc-lista .pf-frand').length];
    }""" % NAV)
    pastile, randuri = r
    assert pastile[-1] == "2 fără scadență", pastile
    assert sum(int(p.split()[0]) for p in pastile) == randuri == 4, r


# ── (iv) 752: statul de plată cu coloana «Diurnă peste plafon» numai când există excedent ──────────────────────────────────
def _stat(pg, exces):
    rand = {"id": 7, "nume": "IONESCU VASILE", "zile_lucrate": 19, "zile_lucratoare_luna": 22, "brut": 5700.34, "net_de_plata": 2618.34, "cost_total": 5211.34, "semne": []}
    RASP["/tenants/1/stat-plata"] = {"stat": [dict(rand, exces_diurna=exces), dict(rand, id=8, nume="POPESCU ELENA", brut=3000, net_de_plata=1800, cost_total=3100, exces_diurna=0)]}
    return pg.evaluate("""async () => {
      const m = await import('/static/js/ecrane/firme.js');
      document.body.innerHTML = '<div id="mount"></div>';
      %s
      await m.ecranSalariati(document.getElementById('mount'), nav, { id: 1 });
      for (let i = 0; i < 50 && !document.querySelector('#sp-tabel'); i++) await new Promise((ok) => setTimeout(ok, 100));
      const t = (s) => [...document.querySelectorAll(s)].map((e) => e.innerText.replace(/\\s+/g, ' ').trim());
      return { antet: t('#sp-tabel thead th'), ionescu: t('#sp-tabel tbody tr:first-child td'), total: t('#sp-tabel tfoot td') };
    }""" % NAV)


def test_statul_are_coloana_diurna_peste_plafon_numai_cu_excedent(pagina):
    """752: cu excedent (Ionescu 885,00): «Brut salarial» = brut − excedent (5.700,34 − 885,00 = 4.815,34) + «Diurnă peste plafon» 885,00 (0,00 la cei fără);
    net și cost neschimbate. MUTAȚIE: coloana rămâne «Brut» cu 5.700,34 -> pică."""
    r = _stat(pagina, 885)
    assert r["antet"] == ["Salariat", "Zile lucrate", "Brut salarial", "Diurnă peste plafon", "Net de plată", "Cost angajator", "Semnele lunii"], r["antet"]
    assert r["ionescu"][2:6] == ["4.815,34", "885,00", "2.618,34", "5.211,34"], r["ionescu"]
    assert r["total"][2:4] == ["7.815,34", "885,00"], r["total"]   # 4.815,34 + 3.000,00 și excedentul total


def test_statul_fara_excedent_ramane_ca_azi(pagina):
    """752: niciun salariat cu excedent -> «Brut», fără coloana nouă, cifrele brute. MUTAȚIE: coloana apare și fără excedent -> pică."""
    r = _stat(pagina, 0)
    assert r["antet"] == ["Salariat", "Zile lucrate", "Brut", "Net de plată", "Cost angajator", "Semnele lunii"], r["antet"]
    assert r["ionescu"][2] == "5.700,34", r["ionescu"]


# ── (v) 749: eticheta declarației o singură dată ───────────────────────────────────────────────────────────────────────
def test_eticheta_d205_nu_se_repeta_in_motiv(pagina):
    """749: motivul serverului începe cu «D205 — nu se poate verifica: …»; ecranul pune tipul și domeniul o singură dată, fără prefixul repetat. Un motiv care
    nu începe cu eticheta, sau cu alta, rămâne neatins. MUTAȚIE: motivul pus întreg -> «D205 — D205 — …» -> pică."""
    r = pagina.evaluate("""async () => {
      const { motivFaraEticheta } = await import('/static/js/ecrane/control_verdict.js');
      return [motivFaraEticheta({ tip: 'd205', motiv: 'D205 — nu se poate verifica: lipsesc note validate pe 2025' }),
              motivFaraEticheta({ tip: 'd205', motiv: 'nu se poate verifica: altceva' }),
              motivFaraEticheta({ tip: 'd301', motiv: 'D205 — alt tip' }), motivFaraEticheta({ tip: 'd205' })]; }""")
    assert r == ["nu se poate verifica: lipsesc note validate pe 2025", "nu se poate verifica: altceva", "D205 — alt tip", ""], r


# ── (vi) 603: diacritice la afișarea documentului mișcării și la titlul achiziției necorporale ───────────────────────────
def test_documentul_miscarii_se_afiseaza_cu_diacritice_iar_cheia_din_baza_ramane(pagina):
    """603 (a): fișa articolului arată «sold inițial (import)»; cheia din bază («sold initial (import)», citită literal de audit_preluare) NU se schimbă;
    alt document nu se atinge. MUTAȚIE: cheia scrisă cu diacritice în articole_import_api -> auditul nu mai găsește mișcările -> pică."""
    r = pagina.evaluate("""async () => { const { documentMiscare } = await import('/static/js/ecrane/firme.js');
      return [documentMiscare('sold initial (import)'), documentMiscare('NIR 12'), documentMiscare('sold initial')]; }""")
    assert r == ["sold inițial (import)", "NIR 12", "sold initial"], r
    for fisier in ("articole_import_api.py", "audit_preluare.py"):
        assert "sold initial (import)" in open(os.path.join(_RAD, "core", fisier), encoding="utf-8").read(), fisier


def test_titlul_notei_la_achizitia_necorporala_are_diacritice():
    """603 (b): nota achiziției necorporale se numește «Achiziție necorporală <tip>: <denumire> (amortizare …)». MUTAȚIE: textul vechi fără diacritice -> pică."""
    from core import test_achizitii_factura as t
    if not t._DB:
        pytest.skip("DB indisponibil")
    import main
    from core import db
    db.init_pool()
    mp = pytest.MonkeyPatch()
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                t._scratch(cur)
            conn.commit()
        mp.setattr(main.auth_api, "schema_tenant", lambda conn, uid, tid: t._SCH)
        r = main.achizitie_necorporala(1, {"data": "2026-06-10", "denumire": "Licenta X", "valoare": 5000, "tip": "software", "cota": 21,
                                           "furnizor_cui": "RO14399840", "furnizor_nume": "SOFT SRL", "numar": "F-SOFT-2"}, {"uid": 1})
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute("SET search_path TO %s" % t._SCH)
            cur.execute("SELECT descriere FROM inregistrari WHERE id = %s", (r["inregistrare_id"],))
            descriere = cur.fetchone()[0]
    finally:
        mp.undo()
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % t._SCH)
            conn.commit()
    assert descriere.startswith("Achiziție necorporală software: Licenta X (amortizare"), descriere


# ── (vii) 618: nota Z validată scrisă înainte de 618, arătată cu data românească; textul din bază nu se atinge ─────────────
def test_nota_z_cu_data_iso_se_arata_cu_titlul_de_azi():
    """618.1: «Raport Z 2026-10-22 casa 8000000001 nr 0050» -> «Vânzări din raportul Z nr 0050 din 22.10.2026, casa 8000000001» (aceeași funcție ca notele noi,
    `explicatie_raport_z`); funcția nu scrie nimic (textul din bază rămâne cel scris). Forma AMEF (cu sufix) și alte texte -> None.
    MUTAȚIE: potrivirea neancorată (prefix) -> forma AMEF e prinsă și își pierde sufixul «de verificat» -> pică."""
    scris = "Raport Z 2026-10-22 casa 8000000001 nr 0050"
    assert jurnal_api.raport_z_iso_afisat(scris) == jurnal_api.explicatie_raport_z("2026-10-22", "8000000001", "0050") \
        == "Vânzări din raportul Z nr 0050 din 22.10.2026, casa 8000000001"
    assert jurnal_api.raport_z_iso_afisat(scris + " (12 bonuri) - de verificat cu Z tiparit") is None
    assert jurnal_api.raport_z_iso_afisat("Vânzări din raportul Z nr 0042 din 20.10.2026, casa 8000000001") is None
    assert jurnal_api.raport_z_iso_afisat(None) is None


# ── (viii) 11: un singur mesaj cu tot ce cere Date firmă; emiterea nu devine blocată de regim sau operațiuni ────────────────
SRL_NOU = {"tip_firma": "srl", "forma_juridica": "SRL", "capital_subscris": None, "capital_varsat": None, "regim_fiscal": None, "platitor_tva": False,
           "operatiuni_ic": None, "tip_decont": None}


def test_mesajul_lipsurilor_numeste_capitalul_regimul_si_operatiunile():
    """11 (a): profil fără capital, regim și operațiuni: mesajul de la deschidere și refuzul de la emitere au, imediat după propoziția lor, «La salvarea în Date firmă se cer
    și: regimul fiscal (micro sau profit), operațiunile intracomunitare (Da sau Nu).»; propoziția de azi rămâne. MUTAȚIE: propoziția scoasă din refuz -> pică."""
    lipsuri = cs.lipsa(SRL_NOU)
    assert lipsuri == ["capitalul social"]
    la_salvare = cs.lipsuri_la_salvare(SRL_NOU)
    assert la_salvare == ["regimul fiscal (micro sau profit)", "operațiunile intracomunitare (Da sau Nu)"]
    propozitie = "La salvarea în Date firmă se cer și: regimul fiscal (micro sau profit), operațiunile intracomunitare (Da sau Nu)."
    assert cs.propozitie_la_salvare(la_salvare) == propozitie
    deschidere = cs.mesaj_la_deschidere(lipsuri, None, None, la_salvare)
    assert "în Date firmă lipsește capitalul social, iar fără ea factura nu se poate emite" in deschidere
    assert "pe factura unei societăți se menționează capitalul social). " + propozitie in deschidere, deschidere
    refuz = cs.mesaj_refuz(lipsuri, la_salvare)
    assert "Legea 31/1990 art. 74 alin. (3)). " + propozitie + " Completează-l în Date firmă" in refuz, refuz
    # ramura „forma juridică lipsește”: propoziția stă după propoziția ramurii
    fara_forma = dict(SRL_NOU, forma_juridica=None)
    refuz_forma = cs.mesaj_refuz(cs.lipsa(fara_forma), cs.lipsuri_la_salvare(fara_forma))
    assert "capitalul subscris și cel vărsat). " + propozitie + " Completează forma" in refuz_forma, refuz_forma


def test_mesajul_numeste_numai_ce_lipseste_efectiv_si_la_singular_cere():
    """11 (a): cu regimul setat, numai operațiunile («se cere»); la plătitorul de TVA fără periodicitate, periodicitatea; complet: nicio propoziție.
    MUTAȚIE: lista fixă (regim și operațiuni mereu) -> pică."""
    profil = dict(SRL_NOU, regim_fiscal="micro")
    assert cs.propozitie_la_salvare(cs.lipsuri_la_salvare(profil)) == "La salvarea în Date firmă se cere și: operațiunile intracomunitare (Da sau Nu)."
    platitor = dict(profil, platitor_tva=True, operatiuni_ic=False)
    assert cs.lipsuri_la_salvare(platitor) == ["periodicitatea decontului TVA (lunar sau trimestrial)"]
    nedeclarat = dict(profil, platitor_tva=None, operatiuni_ic=False)
    assert cs.lipsuri_la_salvare(nedeclarat) == ["dacă firma e înregistrată în scopuri de TVA (Da sau Nu)"]
    complet = dict(platitor, tip_decont="lunar")
    assert cs.lipsuri_la_salvare(complet) == [] and cs.propozitie_la_salvare([]) == ""
    assert "La salvarea" not in cs.mesaj_la_deschidere(["capitalul social"], None, None, [])
    # partida simplă n-are regim fiscal de ales
    pfa = {"tip_firma": "pfa", "forma_juridica": None, "regim_fiscal": None, "platitor_tva": False, "operatiuni_ic": False}
    assert cs.lipsuri_la_salvare(pfa) == []


def test_regimul_si_operatiunile_nu_blocheaza_emiterea():
    """11 (a): regimul și operațiunile sunt numite ca «le va cere și salvarea», nu devin condiții de emitere: `lipsa` (singura care blochează) nu le citește.
    MUTAȚIE: `lipsa` cere regimul -> profilul cu capital și fără regim devine blocat -> pică."""
    cu_capital = dict(SRL_NOU, capital_subscris=200)
    assert cs.lipsa(cu_capital) == []
    assert cs.lipsuri_la_salvare(cu_capital) == ["regimul fiscal (micro sau profit)", "operațiunile intracomunitare (Da sau Nu)"]
