# -*- coding: utf-8 -*-
"""[lotul 11, deficiențele 424 și 446 — comanda Costin 11.1 pct.13–14, verbatim în DECIZII „Comanda 11.1”] Previzualizările importurilor
de migrare, desenate de `migrare.js` + `navigator.js` + `stil.css` REALE, în Chromium, la 1280×720 (ecranul pe care Costin a cerut, la
394, „totul încape într-un ecran, fără derulare”).

Verbatim 424: „la importurile de migrare se derulează toată fereastra, plus separat tabelul. Trebuie: rezumat fix sus, acțiune fix jos,
derulare doar pe tabel.” Verbatim 446: „la confirmarea duplicatelor, avertismentul apare de două ori, tabelul se strânge la un rând, iar
«Salvează salariații» rămâne activ lângă «Actualizez fișele». Avertismentul nu e eroare.”

CAUZA 424 (măsurată aici, pe codul lotului 10): rezumatul lipit sus al balanței avea 611 px într-un corp de 661 (nota „ce s-a citit”, caseta
înlocuirii îngustă), iar bara de jos 560 px la confirmare — un element lipit mai înalt decât fereastra nu mai stă lipit, deci derula tot;
rețetele, articolele și RIP-ul se desenau SUB zona de încărcare, deci intro-ul și zona de încărcare derulau deasupra rezumatului. De ce
e2e-ul lotului 10 a trecut: măsura numai importul salariaților, fără balanță existentă și fără confirmare, și numai că butonul se vede și
că nu există derulare laterală — nu cât loc rămâne tabelului.

Ce păzește, pe fiecare previzualizare (balanță, parteneri, salariați, asociați, mijloace fixe, istoric, articole, rețete, RIP):
  1. un singur element derulează (corpul ferestrei), niciunul lateral;
  2. după derularea la capăt, rezumatul e lipit sus și bara jos (lipirea ține), iar între ele tabelul are cel puțin `LOC_MIN` px;
  3. pe importurile care înlocuiesc ce exista: avertismentul apare O DATĂ, cu stilul avertismentului (`msg-avert`, DS cap.6), nu al
     erorii; la salvare, confirmarea e o întrebare (nu încă o dată avertismentul), butonul principal e ascuns cât e deschisă, iar tabelul
     păstrează cel puțin `LOC_MIN_CONFIRMARE` px; „Renunță” readuce butonul.

Datele: rândurile vin din funcțiile REALE de citire (`extrage`) pe fișierele-model ale ecranului; backendul e simulat (rutele întorc
JSON-ul pe care l-ar întoarce use-case-ul), fiindcă aici se măsoară așezarea, nu scrierea (scrierea o probează testele modulelor).

Temei: N/A — regulă de UI (DS cap.9 v2.96–v2.97 „Fereastra cu tabel”, DS cap.6 mesajele de stare).
"""
import functools
import http.server
import json
import urllib.parse
import os
import socketserver
import threading

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAT, INALT = 1280, 720
LOC_MIN = 240               # px de tabel cu rezumatul și bara lipite (≈ 6 rânduri de 37 px): „derulare doar pe tabel”
LOC_MIN_CONFIRMARE = 150    # px cu întrebarea de confirmare deschisă în bara de jos („tabelul se strânge la un rând” = 37 px)
AVERT = ("Firma are deja date pentru acest pas; din cele din fișier, unele există deja: POPESCU ANA, IONESCU RADU, GEORGESCU MIHAI. "
         "Salvarea le înlocuiește cu datele din fișier — valorile, datele, conturile și sumele — iar ce nu e în fișier nu se șterge. "
         "Pentru aceste date sunt deja emise documente pe lunile trecute, calculate pe datele vechi.")

PAGINA = """<!doctype html><html lang="ro"><head><meta charset="utf-8"><link rel="stylesheet" href="/static/stil.css"></head>
<body><div id="app"></div><script type="module">
sessionStorage.setItem("iconta_user", JSON.stringify({rol: "admin_firma", nume: "Probă", bun_venit_vazut: true}));
const m = await import("/static/js/navigator.js"); const mig = await import("/static/js/ecrane/migrare.js");
window._nav = m.creeazaNavigator(document.getElementById("app"), () => {}); window._mig = mig; window._gata = true;
</script></body></html>"""

MASOARA = """() => {
  const c = [...document.querySelectorAll('.fereastra-corp')].pop();
  const rez = c.querySelector('.rezumat-fix'), bara = c.querySelector('.bara-fixa');
  const derul = [...document.querySelectorAll('*')].filter((e) => { const s = getComputedStyle(e);
    return (['auto', 'scroll'].includes(s.overflowY) && e.scrollHeight > e.clientHeight + 1)
        || (['auto', 'scroll'].includes(s.overflowX) && e.scrollWidth > e.clientWidth + 1); });
  const deruleaza = c.scrollHeight > c.clientHeight + 1;
  c.scrollTop = 0;
  const deasupra = Math.round(rez.getBoundingClientRect().top - c.getBoundingClientRect().top);   // ce stă deasupra rezumatului
  c.scrollTop = 1e7;
  const r = (e) => e.getBoundingClientRect();
  const principal = bara && bara.querySelector('button.mig-buton');
  return {derulante: derul.map((e) => e.className || e.tagName), lateral: c.scrollWidth > c.clientWidth + 1,
          rez_sus: Math.round(r(rez).top - r(c).top), bara_jos: Math.round(r(c).bottom - r(bara).bottom),
          deruleaza, deasupra,
          // locul tabelului: înălțimea pe care o are corpul în fereastră (până la marginea ei de jos), minus rezumatul și bara
          loc: Math.round(r(c.closest('.fereastra')).bottom - r(c).top - rez.offsetHeight - bara.offsetHeight), text: c.closest('.fereastra').innerText,
          principal_ascuns: !!principal && (principal.hidden || !principal.offsetParent),
          avert: [...c.querySelectorAll('#mig-inlocuire')].map((e) => e.className)};
}"""


class _Tacut(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright
    from core.test_emitere_randuri_dinamice import _lanseaza_chromium
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(_Tacut, directory=RAD))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    pw = sync_playwright().start()
    b = _lanseaza_chromium(pw)
    if b is None:
        pw.stop()
        srv.shutdown()
        pytest.fail("GARD headless nu poate rula: chromium indisponibil. NU e skip verde-fals.")
    try:
        yield b, srv.server_address[1]
    finally:
        b.close()
        pw.stop()
        srv.shutdown()


# ── datele previzualizărilor: rândurile din citirea reală a fișierelor-model ────────────────────────────────────────────────────
def _ok(rr):
    for r in rr:
        r.setdefault("stare", "ok")
        r.setdefault("motive", [])
    return rr


def _balanta():
    from core import solduri_api
    from core.test_lot11_m_balanta_saga import fisier
    d = solduri_api.extrage_balanta_detaliat(fisier("rulaje_precedente"), "b.csv")
    td, tc = sum(r["debit"] for r in d["randuri"]), sum(r["credit"] for r in d["randuri"])
    return dict(randuri=_ok(d["randuri"]), total_debit=td, total_credit=tc, valida=True, coloane=d["coloane"], ignorate=d["ignorate"],
                sintetice_inlocuite=d["sintetice_inlocuite"], fara_sold=d["fara_sold"], data_propusa="2026-09-30", conturi_in_afara=[],
                rulaje=True, perechi=d["perechi"], forma_rulaje=d["forma_rulaje"], avertisment_rulaje=None, cere_metoda_stoc=True,
                metode_stoc=[["global_valoric", "global-valoric"], ["cantitativ_valoric", "cantitativ-valoric"]], note_dupa=None)


def _cui(baza):
    """CUI cu cifra de control calculată după algoritmul oficial (CLAUDE.md, „Date de test”): numai în memorie, nu se scrie nicăieri."""
    ch, corp = [7, 5, 3, 2, 1, 7, 5, 3, 2], str(baza).rjust(9, "0")
    r = sum(int(corp[i]) * ch[i] for i in range(9)) * 10 % 11
    return "%d%d" % (baza, 0 if r == 10 else r)


def _parteneri():
    from core import solduri_parteneri_api as sp
    rr = sp.extrage(("cont;cui;denumire;sold debitor;sold creditor\n" + "".join(
        "4111;%s;CLIENT %02d SA;%d;0\n" % (_cui(1000001 + i), i, 100 + i) for i in range(18))).encode(), "p.csv")
    return {"randuri": _ok(rr), "total_debit": sum(r["debit"] for r in rr), "total_credit": 0, "ignorate": [], "erori": [],
            "coerenta": [{"cont": "4111", "suma_parteneri": 1953, "sold_balanta": 1953, "sursa": "balanța de deschidere",
                          "data": "2026-09-30", "coincide": True, "diferenta": 0}]}


def _salariati():
    from core import salariati_import_api as si
    cnp = ["1900101410011", "1960101078916", "2900215410011"]   # cifra de control verificată (CLAUDE.md)
    rr = si.extrage(("nume;prenume;cnp;data angajare;brut;judet;cor\n" + "".join(
        "POP%s;ANA;%s;2024-01-15;5000;B;251401\n" % (i, c) for i, c in enumerate(cnp))).encode(), "s.csv")
    for r in rr:
        r["din_fisa"] = list(r["de_verificat"])
    return {"randuri": si.eticheteaza(rr), "total": 3, "valizi": 3, "invalizi": 0, "erori": []}


def _asociati():
    from core import asociati_import_api as ai
    rr = ai.extrage("nume;cnp/cui;cota %\nPopescu Ana;2900215410011;60\nIonescu Radu;1960101078916;40\n".encode(), "a.csv")
    return {"randuri": _ok(rr), "total": 2, "erori": [], "coerenta": None}


def _mijloace():
    from core import mijloace_fixe_import_api as mf
    rr = mf.extrage(("cod;denumire;valoare intrare;data PIF;durata luni;metoda;cont imobilizare;cont amortizare;amortizare cumulata;"
                     "valoare reziduala\n" + "".join("MF%03d;Laptop %d;6000;2024-03-15;36;liniara;2131;2813;3300;0\n" % (i, i)
                                                       for i in range(12))).encode(), "m.csv")
    return {"randuri": _ok(rr), "total": len(rr), "erori": [], "total_valoare": 72000.0, "respinse": 0, "semnalate": 0,
            "data_preluare": "2026-09-30", "reconciliere": None, "inlocuire_refuzata": None}


def _istoric():
    from core import istoric_declaratii_import_api as ist
    rr = ist.extrage(("tip;an;luna;data depunere;suma de plata\n" + "".join(
        "D300;2026;%d;2026-%02d-25;\n" % (l, l + 1) for l in range(1, 9)) + "".join(
        "D112;2026;%d;2026-%02d-25;\n" % (l, l + 1) for l in range(1, 9))).encode(), "i.csv")
    return {"randuri": _ok(rr), "total": len(rr), "erori": [], "respinse": 0, "semnalate": 0}


def _articole():
    from core import articole_import_api as ar
    rr = ar.extrage(("denumire;um;cantitate;pret;cont stoc;cont cheltuiala\n" + "".join(
        "Marfa %02d;buc;10;2,50;371;607\n" % i for i in range(20))).encode(), "a.csv")
    return {"randuri": _ok(rr), "rezumat": {"cu_stoc": 20, "valoare_totala": 500}, "erori": [], "data_sold": "2026-09-30",
            "reconciliere": None}


def _retete():
    from core import retete_import_api as rt
    rr = rt.extrage(("reteta;pret vanzare;ingredient;cantitate\n" + "".join(
        "Reteta %02d;18;Făină albă tip 000;0,08\n" % i for i in range(20))).encode(), "r.csv")
    return {"randuri": _ok(rr), "rezumat": {"valide": 20, "total": 20}, "erori": []}


def _rip():
    from core import rip_migrare_api as rip
    rr = rip.extrage(("data;tip;explicatie;suma;categorie;metoda\n" + "".join(
        "2026-01-%02d;incasare;Factura %d client;1500;venituri;banca\n" % (i + 1, i) for i in range(20))).encode(), "r.csv")
    return {"randuri": _ok(rr), "total": len(rr), "erori": []}


#: pasul din meniu, ruta încărcării, butonul principal, datele, tipul firmei; `True` = importul înlocuiește ce exista (426 / 446)
PASI = {
    "balanta": ("Solduri ini", "/solduri/incarca", "#mig-salveaza-sold", _balanta, "srl", True),
    "parteneri": ("Solduri parteneri", "/parteneri/incarca", "#mig-salveaza-part", _parteneri, "srl", True),
    "salariati": ("Salaria", "/salariati-import/incarca", "#mig-salveaza-sal", _salariati, "srl", True),
    "asociati": ("Asocia", "/asociati-import/incarca", "#mig-salveaza-asoc", _asociati, "srl", True),
    "mijloace_fixe": ("Mijloace fixe", "/mijloace-fixe-import/incarca", "#mig-salveaza-mf", _mijloace, "srl", True),
    "istoric": ("Istoric declara", "/istoric-declaratii-import/incarca", "#mig-salveaza-ist", _istoric, "srl", True),
    "articole": ("Articole", "/articole-import/incarca", "#mig-importa", _articole, "srl", False),
    "retete": ("Rețete", "/retete-import/incarca", "#mig-importa", _retete, "srl", False),
    "rip": ("Import RIP", "/rip-import/incarca", "#mig-salveaza-rip", _rip, "pfa", False),
}
STRATURI = ["vector_fiscal", "solduri", "solduri_parteneri", "salariati", "asociati", "mijloace_fixe", "istoric_declaratii",
            "plan_conturi", "rip", "articole", "retete"]


def _deschide(browser, pas, cu_existenta):
    b, port = browser
    titlu, ruta, buton, date_fn, tip, _ = PASI[pas]
    date = date_fn()
    if cu_existenta:
        date.update(existenta={"randuri": 3, "total": 3, "are_solduri": True}, avertisment_inlocuire=AVERT)
    pg = b.new_page(viewport={"width": LAT, "height": INALT})
    erori = []
    pg.on("pageerror", lambda e: erori.append(str(e)))

    def raspuns(route):
        u = route.request.url
        cale = urllib.parse.urlsplit(u).path   # calea cererii, nu un sub-șir al URL-ului întreg (core/test_garzi_pe_text.py)
        if cale.startswith("/static/"):
            return route.continue_()
        if cale.endswith("/migrare/straturi"):
            return route.fulfill(status=200, content_type="application/json", body=json.dumps({"straturi": STRATURI}))
        if ruta in u:
            return route.fulfill(status=200, content_type="application/json", body=json.dumps(date))
        return route.fulfill(status=200, content_type="application/json", body="{}")
    pg.route("**/harness.html", lambda r: r.fulfill(status=200, content_type="text/html", body=PAGINA))
    for pref in ("/tenants/", "/migrare/", "/auth/", "/notificari", "/versiune"):
        pg.route("**%s**" % pref, raspuns)
    pg.goto("http://127.0.0.1:%d/harness.html" % port)
    pg.wait_for_function("() => window._gata === true", timeout=20000)
    pg.evaluate("(tip) => window._nav.deschide('Firmă', (c) => window._mig.meniuMigrarePerFirma(c, window._nav, "
                "{tenant_id: 1, nume: 'Firmă Probă Migrare SRL', tip_firma: tip}))", tip)
    pg.wait_for_selector(".mig-frand", timeout=10000)
    pg.locator(".mig-frand", has_text=titlu).first.click()
    pg.wait_for_selector("#mig-file", state="attached", timeout=10000)
    pg.set_input_files("#mig-file", files=[{"name": "f.csv", "mimeType": "text/csv", "buffer": b"x"}])
    pg.wait_for_selector(buton, timeout=10000)
    pg.wait_for_timeout(300)
    assert not erori, erori
    return pg


@pytest.mark.parametrize("pas", sorted(PASI))
def test_def_424_previzualizarea_are_rezumatul_sus_actiunea_jos_si_deruleaza_numai_tabelul(browser, pas):
    """ROȘU înainte (balanța): rezumatul lipit avea 611 px din 661, deci lipirea nu ținea — `loc` negativ (-383 px); rețetele /
    articolele / RIP: rezumatul se lipea numai în `#mig-preview`, sub zona de încărcare. MUTAȚIA: nota „ce s-a citit” desfăcută în
    rezumat, sau `const zona = corp.querySelector("#mig-preview")` la loc -> pică."""
    pg = _deschide(browser, pas, cu_existenta=False)
    try:
        o = pg.evaluate(MASOARA)
    finally:
        pg.close()
    assert set(o["derulante"]) <= {"fereastra-corp", "zona-derulare"} and not o["lateral"], o["derulante"]  # un singur element derulează, niciodată lateral
    # deasupra rezumatului stă numai titlul ferestrei (h2 ≈ 70 px): nu zona de încărcare, care ar derula înaintea tabelului
    assert o["deasupra"] <= 80, (pas, o["deasupra"])
    # după derularea la capăt, rezumatul și bara sunt încă în fereastră: „rezumat fix sus, acțiune fix jos” (lipite, dacă tabelul derulează)
    assert o["rez_sus"] >= 0 and o["bara_jos"] >= 0, (pas, o["rez_sus"], o["bara_jos"])
    if o["deruleaza"] and o["rez_sus"]:
        assert o["rez_sus"] <= 80, (pas, o["rez_sus"])                     # numai titlul ferestrei (h2) n-a ieșit încă de tot
    assert o["loc"] >= LOC_MIN, (pas, o["loc"])         # „derulare doar pe tabel”: locul tabelului între rezumat și bară


@pytest.mark.parametrize("pas", sorted(p for p in PASI if PASI[p][5]))
def test_def_446_avertismentul_o_data_confirmarea_fara_al_doilea_buton(browser, pas):
    """ROȘU înainte: textul avertismentului de 2 ori în fereastră (caseta de sus și confirmarea), amândouă în caseta roșie a refuzului;
    „Salvează salariații” vizibil lângă „Actualizez fișele”; bara confirmării lua tabelul. MUTAȚIA: `confirmaCaseta(zona,
    esc(date.avertisment_inlocuire), …)` la loc, sau butonul lăsat vizibil -> pică."""
    pg = _deschide(browser, pas, cu_existenta=True)
    try:
        o = pg.evaluate(MASOARA)
        # [lotul 14, 687] avertismentul e un card-rezumat sub titlu; textul serverului, galben (nu eroare), O SINGURĂ DATĂ, în fereastra cardului
        assert o["avert"] == ["sir-carduri"], (pas, o["avert"])
        pg.click("#mig-inlocuire [data-card]")
        pg.wait_for_selector("#mig-inlocuire-text.msg-avert", timeout=5000)
        assert pg.evaluate("() => [...document.querySelectorAll('.fereastra')].pop().innerText").count(AVERT[:60]) == 1, pas
        pg.click(".fereastra:last-of-type .nav-sageata.nav-inapoi")
        pg.wait_for_selector("#mig-inlocuire [data-card]", timeout=5000)
        if pg.query_selector("#mig-metoda-stoc"):
            pg.select_option("#mig-metoda-stoc", "cantitativ_valoric")      # balanța cu sold pe 371 cere metoda înainte de salvare
        pg.click(PASI[pas][2])
        pg.wait_for_selector("#ca-ok", timeout=5000)
        c = pg.evaluate(MASOARA)
        assert c["text"].count(AVERT[:60]) <= 1, pas                         # „avertismentul apare de două ori” (acum: cardul, nu textul)
        assert c["principal_ascuns"], pas                                    # o singură acțiune activă
        assert c["loc"] >= LOC_MIN_CONFIRMARE, (pas, c["loc"])                # „tabelul se strânge la un rând”
        assert c["rez_sus"] >= 0 and c["bara_jos"] >= 0, (pas, c["rez_sus"], c["bara_jos"])
        pg.click("#ca-nu")
        assert pg.is_visible(PASI[pas][2]), pas                              # „Renunță” readuce butonul
    finally:
        pg.close()
