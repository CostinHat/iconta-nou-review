# -*- coding: utf-8 -*-
"""[lotul 12, deficiențele 626 și 627 — comanda Costin 12.2 pct.13–14, verbatim:
  626: „Date firmă / TVA la încasare: după ce scrii și golești «Aplică de la», perioada nouă rămâne obligatorie și oprește salvarea.
        Perioadă nouă doar la cerere.”
  627: „Date firmă: după o salvare parțială, «Profil incomplet» nu se actualizează.”]

Ecranul Date firmă (`date_firma.js` + `api.js` + `stil.css` REALE, în Chromium); serverul e simulat (rutele întorc JSON-ul use-case-urilor),
fiindcă aici se probează ce trimite și ce arată ecranul; scrierea o probează testele modulelor (`core/test_lot10_date_firma.py`).

CAUZA 626: `_tvaiDinFormular` compara „Aplică de la” gol cu data perioadei înregistrate (01.10.2026), deci vedea o schimbare cerută —
„aplică, fără dată” — iar `Salvează` refuza („Scrie data de la care firma aplică sistemul TVA la încasare.”) și nu salva regimul.
REPARAȚIA: pe o firmă cu perioada înregistrată, „Aplică de la” golit înseamnă data înregistrată (și câmpul o reia la ieșire); o perioadă
nouă se cere scriind data ei. Fără perioadă înregistrată, „Da” e cererea, deci data rămâne de scris (al treilea test).
CAUZA 627: la o salvare parțială (o parte refuzată), handlerul se oprea înainte de redesenare, deci „Profil incomplet” rămânea cel de la
deschidere, cu câmpurile tocmai salvate tot „lipsă”. REPARAȚIA: blocul (`#df-profil-stare`, `_blocProfil`) se recitește din bază.

Temei 626: CF art.282 alin.(3^1) (data de la care se aplică sistemul) — regula datei rămâne pe server (`core/regim_tva_incasare.py`);
aici se schimbă numai ce trimite ecranul. 627: N/A — afișare.
"""
import json
import urllib.parse

from core.test_lot11_m_ferestre_import import browser  # noqa: F401  (serverul static + Chromium)

PAGINA = """<!doctype html><html lang="ro"><head><meta charset="utf-8"><link rel="stylesheet" href="/static/stil.css"></head>
<body><div id="app" class="fereastra-corp"></div><script type="module">
sessionStorage.setItem("iconta_user", JSON.stringify({rol: "admin_firma", nume: "Probă", bun_venit_vazut: true}));
const m = await import("/static/js/ecrane/date_firma.js");
await m.randeazaDateFirma(document.getElementById("app"), {setInapoi() {}}, 1);
window._gata = true;
</script></body></html>"""

LIPSA_REG_COM = [{"camp": "reg_com", "declaratii": ["D101", "bilanț"]}]


def _profil(reg_com=None):
    return {"cui": "14399840", "reg_com": reg_com, "caen": "6920", "adresa": "Str. Probă 1", "oras": "București", "judet": "B",
            "banca": "Banca Probă", "iban": "RO49AAAA1B31007593840000", "fara_cont_bancar": False, "telefon": "0722000626",
            "declarant_nume": "Pop", "declarant_prenume": "Ana", "declarant_functie": "Administrator", "mare_contribuabil": False,
            "forma_proprietate": "34", "interes_public": False, "tip_firma": "srl", "cont_venit_implicit": "704",
            "forma_juridica": "SRL", "capital_subscris": "200", "capital_varsat": "200", "luna_preluare": {}}


def _vector(cu_perioada):
    ti = ({"curenta": {"id": 7, "de_la": "2026-10-01", "pana_la": None, "sursa": "manual"}, "fara_data": False, "aplica_azi": True,
           "perioade": [{"id": 7, "de_la": "2026-10-01", "pana_la": None, "sursa": "manual", "verificat_anaf_la": None}],
           "avertismente": [], "text": "de la 01.10.2026"} if cu_perioada else
          {"curenta": None, "fara_data": False, "aplica_azi": False, "perioade": [], "avertismente": [], "text": ""})
    return {"regim_fiscal": "micro", "platitor_tva": True, "tip_decont": "trimestrial", "operatiuni_ic": False, "inreg_art317": False,
            "tva_data_inceput": "2025-01-01", "tva_incasare": ti}


def _deschide(browser, cu_perioada=True, lipsuri_dupa=None, vector_refuzat=False):  # noqa: F811
    """Fereastra Date firmă pe serverul simulat. `cereri` = (metoda, cale, corp) pentru fiecare scriere; `lipsuri_dupa` = ce întoarce
    a doua citire a profilului (după salvare); `vector_refuzat` = salvarea vectorului refuzată (salvare parțială)."""
    b, port = browser
    pg = b.new_page(viewport={"width": 1366, "height": 900})
    cereri, citiri = [], {"profil": 0}
    erori = []
    pg.on("pageerror", lambda e: erori.append(str(e)))

    def raspuns(route):
        rq = route.request
        cale = urllib.parse.urlsplit(rq.url).path
        if cale.startswith("/static/"):
            return route.continue_()
        corp = rq.post_data_json if rq.method != "GET" and rq.post_data else None
        if rq.method != "GET":
            cereri.append((rq.method, cale, corp))

        def ok(d, st=200):
            return route.fulfill(status=st, content_type="application/json", body=json.dumps(d))
        if cale == "/tenants/1/firma-profil/date" and rq.method == "GET":
            citiri["profil"] += 1
            prima = citiri["profil"] == 1
            return ok({"profil": _profil(None if prima else "J40/626/2020"), "lipsuri": LIPSA_REG_COM if prima else (lipsuri_dupa or []),
                       "blocaje": [], "conturi_venit": {"704": "Venituri din servicii"}, "forme_juridice": [["SRL", "SRL"]],
                       "forme_proprietate": [["34", "Societăți cu răspundere limitată"]], "metode_stoc": [], "activitati_amef": [],
                       "jurnal": []})
        if cale == "/tenants/1/vector" and rq.method == "GET":
            return ok(_vector(cu_perioada))
        if cale == "/tenants/1" and rq.method == "GET":
            return ok({"id": 1, "nume": "Firmă Probă 626 SRL"})
        if cale == "/tenants/1/asociati" and rq.method == "GET":
            return ok({"asociati": [], "istoric": []})
        if cale == "/tenants/1/firma-profil/date":
            return ok({"ok": True, "lipsuri": lipsuri_dupa or []})
        if cale == "/tenants/1/vector":
            if vector_refuzat:
                return ok({"detail": {"mesaj": "Regimul fiscal nu se poate schimba: luna 09/2026 e închisă.",
                                      "erori_campuri": [{"camp": "regim_fiscal", "mesaj": "Regimul fiscal nu se poate schimba: luna 09/2026 e închisă."}]}}, 409)
            return ok({"ok": True})
        if cale == "/tenants/1/tva-incasare":
            return ok({"ok": True, "avertismente": [], "stare": {}})
        return ok({})
    pg.route("**/harness.html", lambda r: r.fulfill(status=200, content_type="text/html", body=PAGINA))
    for pref in ("/tenants/", "/auth/", "/notificari", "/versiune"):
        pg.route("**%s**" % pref, raspuns)
    pg.goto("http://127.0.0.1:%d/harness.html" % port)
    pg.wait_for_function("() => window._gata === true", timeout=20000)
    return pg, cereri, erori


def _salveaza(pg):
    pg.click("#df-salveaza")
    pg.wait_for_function("() => (document.querySelector('#df-msg') || {innerText: ''}).innerText.trim().length > 0", timeout=10000)
    pg.wait_for_selector("#df-salveaza:not([disabled])", timeout=10000)


def test_def_626_aplica_de_la_golit_nu_cere_perioada_noua(browser):  # noqa: F811
    """Firma cu perioada de la 01.10.2026 -> „Aplică de la”: scrii 01.11.2026, apoi golești -> la ieșirea din câmp revine 01.10.2026
    -> „Salvează”: salvat, fără refuz, fără nicio cerere spre regimul TVA la încasare (nimic schimbat). ROȘU înainte: refuzul „Scrie data
    de la care firma aplică sistemul TVA la încasare.” lângă câmp + „NU s-a salvat.”. MUTAȚIA: `|| c.de_la` scos din `_tvaiDinFormular`
    și reluarea la ieșire scoasă -> pică."""
    pg, cereri, erori = _deschide(browser)
    try:
        assert pg.input_value("#vf-tva_incasare_de_la") == "2026-10-01"
        pg.fill("#vf-tva_incasare_de_la", "2026-11-01")
        pg.fill("#vf-tva_incasare_de_la", "")
        pg.click("#df-telefon")                                    # ieșirea din câmp
        assert pg.input_value("#vf-tva_incasare_de_la") == "2026-10-01", "golirea nu e o perioadă nouă: câmpul reia data înregistrată"
        pg.eval_on_selector("#vf-tva_incasare_de_la", "e => { e.value = ''; }")   # golit și apăsat direct „Salvează” (fără ieșire)
        _salveaza(pg)
        msg = pg.inner_text("#df-msg")
        refuz = pg.query_selector(".refuz-salvare")
        refuz_text = refuz.inner_text() if refuz else ""
    finally:
        pg.close()
    assert not erori, erori
    assert "Scrie data de la care" not in msg + refuz_text and not refuz_text, (msg, refuz_text)
    assert not [c for c in cereri if c[1] == "/tenants/1/tva-incasare"], cereri       # „perioadă nouă doar la cerere”
    assert "salvat" in msg.lower(), msg


def test_def_626_fara_perioada_da_ramane_cerere_si_cere_data(browser):  # noqa: F811
    """Firma FĂRĂ perioadă: „Aplică sistemul TVA la încasare” = Da, „Aplică de la” gol -> refuzul lângă câmp rămâne (Da e cererea unei
    perioade, CF art.282 alin.(3^1): sistemul se aplică de la o dată). Păzește că reparația 626 nu a stins cererea explicită."""
    pg, cereri, erori = _deschide(browser, cu_perioada=False)
    try:
        pg.select_option("#vf-tva_incasare", "da")
        pg.click("#df-salveaza")
        pg.wait_for_selector('.msg-eroare[data-camp="vf-tva_incasare_de_la"]', timeout=10000)
        t = pg.inner_text('.msg-eroare[data-camp="vf-tva_incasare_de_la"]')
    finally:
        pg.close()
    assert not erori, erori
    assert t == "Scrie data de la care firma aplică sistemul TVA la încasare.", t
    assert not [c for c in cereri if c[1] == "/tenants/1/tva-incasare"], cereri


def test_def_627_salvarea_partiala_actualizeaza_profil_incomplet(browser):  # noqa: F811
    """„Profil incomplet — 1 câmp obligatoriu lipsește: Nr. registrul comerțului” -> scrii J40/626/2020 -> „Salvează”, cu vectorul
    refuzat (salvare parțială: „S-au salvat: datele firmei. Restul NU …”) -> blocul de sus spune „Profil complet”, fără Nr. registrul
    comerțului. ROȘU înainte: blocul rămânea „Profil incomplet … Nr. registrul comerțului”. MUTAȚIA: recitirea `#df-profil-stare` scoasă
    -> pică."""
    pg, cereri, erori = _deschide(browser, vector_refuzat=True)
    try:
        assert "Nr. registrul comerțului" in pg.inner_text("#df-profil-stare")
        pg.fill("#df-reg_com", "J40/626/2020")
        _salveaza(pg)
        msg = pg.inner_text("#df-msg")
        bloc = pg.inner_text("#df-profil-stare")
        ramas = pg.input_value("#df-reg_com")
    finally:
        pg.close()
    assert not erori, erori
    assert msg.startswith("S-au salvat: datele firmei."), msg                  # salvarea a fost parțială
    assert "Profil complet" in bloc and "Nr. registrul comerțului" not in bloc, bloc
    assert ramas == "J40/626/2020", ramas                                       # formularul nu s-a redesenat peste ce a scris omul
