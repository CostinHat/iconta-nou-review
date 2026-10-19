# -*- coding: utf-8 -*-
"""Lotul 9, închiderea (Costin 19.10.2026, verbatim în DECIZII „Închiderea lotului 9: comanda și deciziile”): C63 și C61 — pașii
contabilului pe aplicația din index, pe baza de TEST, pe firma nouă cu stoc cantitativ-valoric a lui `e2e_lot92` (`firma_cv`).

- C63: „la transformarea în factură se pune aceeași întrebare ca la orice factură, «Pleacă marfa acum?»” — proforma / avizul cu articol
  de stoc -> „Transformă în factură” -> întrebarea emiterii; „Da” descarcă marfa o dată, „Nu” nu atinge stocul.
- C61: „Da, câmpuri și la român” — localitatea și județul clientului român, precompletate din ANAF la „Verifică”, modificabile, scrise
  pe factură și pe PDF fără dublarea localității.

Răspunsul ANAF la „Verifică” e servit de probă, ca serviciu extern (`page.route`), cu structura rutei `/tenants/{id}/verifica-cui/{cui}`
(`anaf_api.valideaza_cui`); valorile sunt sintetice. CUI-ul 14399840 are cifra de control verificată (algoritmul din CLAUDE.md)."""
import datetime as _dt
import json
import re

from e2e_lot92 import firma_cv, firma_cv_noua  # noqa: F401 — fixturi (firma nouă, stoc cantitativ-valoric)

AZI = _dt.date.today()

#: răspunsul rutei „Verifică” pentru clientul român: adresa ANAF cuprinde deja localitatea și județul domiciliului fiscal
ANAF_RO = {"cui": "14399840", "denumire": "DANTE INTERNATIONAL SA", "adresa": "MUNICIPIUL BUCUREŞTI, SECTOR 2, STR. SINTETICA NR.1",
           "localitate": "Sector 2 Mun. Bucureşti", "judet": "B", "platitor_tva": True, "inactiv": False, "gasit": True}


def _stoc(patron, firma, aid):
    from e2e_bloc_a import _api, _ok
    arts = _ok(_api(patron, "GET", "/tenants/%d/stocuri/articole" % firma["tenant_id"]), "articole")["articole"]
    return float(next(a for a in arts if a["id"] == aid)["stoc"])


def _document_cu_articol(patron, firma, tip):
    """O proformă / un aviz către DANTE, cu 2 buc din articolul de stoc, pe ruta formularului; întoarce (id document, id articol)."""
    from e2e_bloc_a import ARTICOL, CLIENT, _api, _ok, articol_in_stoc
    aid = articol_in_stoc(patron, firma, cantitate=22, pret=10)
    corp = {"linii": [{"descriere": ARTICOL, "cantitate": 2, "um": "buc", "pret_unitar": 20.0, "cota_tva": 21, "cota_propusa": 21,
                       "articol_id": aid}],
            "tert_nume": CLIENT["#em-nume"], "tert_cui": CLIENT["#em-cui"], "tert_adresa": CLIENT["#em-adresa"], "moneda": "RON",
            "tert_tara": "RO", "tip_operatiune": "normal", "bon_fiscal_nr": None, "bon_fiscal_data": None,
            "data_emitere": AZI.isoformat(), "data_scadenta": None, "tip": tip}
    return _ok(_api(patron, "POST", "/tenants/%d/facturi/emite" % firma["tenant_id"], corp), tip)["factura_id"], aid


def _transforma_pana_la_intrebare(patron, firma, tip):
    """Detaliul documentului -> „Transformă în factură”: caseta „Pleacă marfa acum?” apare în zona de mesaj a detaliului."""
    from e2e_bloc_a import _deschide_factura
    did, aid = _document_cu_articol(patron, firma, tip)
    stoc0 = _stoc(patron, firma, aid)
    _deschide_factura(patron, firma, did)
    pg = patron.pg
    pg.wait_for_selector("#fd-transforma", timeout=20000)
    pg.click("#fd-transforma")
    pg.wait_for_selector("#fd-act-rez .caseta-poarta #fd-poarta-da", timeout=30000)
    t = " ".join(pg.inner_text("#fd-act-rez .caseta-poarta .cp-mesaj").split())
    assert t == ("Pleacă marfa acum? 1 articol de pe factură se descarcă din gestiune dacă marfa pleacă fizic azi. Dacă e avans, "
                 "livrare ulterioară sau serviciu, alege „Nu, doar factură\"."), t
    assert pg.is_visible("#fd-poarta-nu") and pg.is_visible("#fd-transforma"), "întrebarea vine înainte: documentul încă netransformat"
    assert _stoc(patron, firma, aid) == stoc0, "fără răspuns nu se descarcă nimic"
    return pg, aid, stoc0


# ── C63 — „Transformă în factură” întreabă „Pleacă marfa acum?” ──────────────────────────────────────────────────────────
def test_def_c63_proforma_cu_articol_intreaba_si_da_descarca_marfa_o_data(patron, firma_cv):
    """C63 (decizia Costin 19.10.2026). Pașii: proforma cu 2 buc din articolul de stoc -> detaliul -> „Transformă în factură”: întrebarea
    „Pleacă marfa acum?” (textul emiterii), stocul neatins; „Da, pleacă marfa” -> „Factura <nr> a fost emisă · 1 articol descărcat din
    gestiune.”, „transformată în <nr>”, iar stocul articolului scade cu 2 (o singură dată).
    MUTAȚIE (core/uc_tenants.py, ancora `intreaba_marfa=poarta_ceruta, pleaca_marfa=pleaca_marfa, **antet_din_proforma(f))` -> `pleaca_
    marfa=pleaca_marfa, **antet_din_proforma(f))`): transformarea nu mai întreabă -> `#fd-poarta-da` nu apare -> ROȘU."""
    pg, aid, stoc0 = _transforma_pana_la_intrebare(patron, firma_cv, "proforma")
    patron.captura("intrebarea")
    with pg.expect_response(lambda r: r.url.endswith("/transforma") and r.request.method == "POST", timeout=30000) as rr:
        pg.click("#fd-poarta-da")
    r = rr.value.json()
    assert json.loads(rr.value.request.post_data) == {"pleaca_marfa": True}, rr.value.request.post_data
    pg.wait_for_function("(t) => ((document.querySelector('#fd-act-rez') || {}).textContent || '') === t",
                         arg="Factura %s a fost emisă · 1 articol descărcat din gestiune." % r["numar"], timeout=20000)
    patron.captura("da")
    assert " ".join(pg.inner_text("#fd-vezi-transformata").split()) == "transformată în %s" % r["numar"], pg.inner_text(".fd-antet")
    assert _stoc(patron, firma_cv, aid) == stoc0 - 2, (stoc0, _stoc(patron, firma_cv, aid))


def test_def_c63_aviz_cu_articol_intreaba_si_nu_lasa_stocul(patron, firma_cv):
    """C63 (decizia Costin 19.10.2026: aviz și proformă, „aceeași întrebare ca la orice factură”). Pașii: aviz cu 2 buc din articolul de
    stoc -> detaliul -> „Transformă în factură”: aceeași întrebare; „Nu, doar factură” -> „Factura <nr> a fost emisă.” (fără descărcare),
    iar stocul articolului rămâne cel dinainte.
    MUTAȚIE (static/js/ecrane/facturi_ecran.js, ancora `.length, transforma, { da: "fd-poarta-da"` -> `.length, () => transforma(true),
    { da: "fd-poarta-da"`): „Nu” trimite „Da” -> marfa se descarcă -> stocul scade -> ROȘU."""
    pg, aid, stoc0 = _transforma_pana_la_intrebare(patron, firma_cv, "aviz")
    with pg.expect_response(lambda r: r.url.endswith("/transforma") and r.request.method == "POST", timeout=30000) as rr:
        pg.click("#fd-poarta-nu")
    r = rr.value.json()
    pg.wait_for_function("(t) => ((document.querySelector('#fd-act-rez') || {}).textContent || '') === t",
                         arg="Factura %s a fost emisă." % r["numar"], timeout=20000)
    patron.captura("nu")
    assert "descarcare" not in r, r
    assert _stoc(patron, firma_cv, aid) == stoc0, (stoc0, _stoc(patron, firma_cv, aid))


# ── C61 — localitatea și județul clientului român ──────────────────────────────────────────────────────────────────────
def test_def_c61_clientul_roman_are_localitatea_si_judetul_din_anaf_pe_factura_fara_dublare(patron, firma_cv):
    """C61 (decizia Costin 19.10.2026, „Da, câmpuri și la român”). Pașii: Emite factură -> la clientul român se văd „Localitatea
    clientului” și „Județul clientului” (lista județelor), nu „Regiunea”; CUI -> „Verifică”: localitatea și județul domiciliului fiscal se
    completează (Sector 2 Mun. Bucureşti, București), modificabile -> linia de servicii -> „Emite factură”: factura le poartă (B = codul),
    iar adresa clientului din detaliu și de pe PDF e cea din ANAF, fără „Sector 2 Mun. Bucureşti” și fără „B” repetate după ea
    (CF art.319 alin.(20) lit.f: „denumirea/numele și adresa beneficiarului”).
    MUTAȚIE (static/js/ecrane/emitere_ecran.js, ancora `        if (r.localitate) corp.querySelector("#em-oras").value = r.localitate;`
    -> gol): localitatea nu se mai completează -> așteptarea pe `#em-oras` expiră -> ROȘU."""
    from e2e_bloc_a import PRODUS, _api, _deschide_emiterea, _deschide_factura, _octeti, _ok, _pdf_text
    tid = firma_cv["tenant_id"]
    _deschide_emiterea(patron, firma_cv["nume"])
    pg = patron.pg
    assert pg.inner_text("#em-oras-et") == "Localitatea clientului" and pg.is_visible("#em-oras")
    assert pg.is_visible("#em-judet") and pg.inner_text("label[for='em-judet']") == "Județul clientului"
    assert pg.is_hidden("#em-regiune"), "la clientul român nu se cere regiunea"
    pg.route("**/verifica-cui/**", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(ANAF_RO)))
    try:
        pg.fill("#em-cui", "14399840")
        pg.click("#em-verifica")
        pg.wait_for_function("() => document.querySelector('#em-oras').value !== ''", timeout=15000)
    finally:
        pg.unroute("**/verifica-cui/**")
    patron.captura("precompletat")
    judet_ales = pg.eval_on_selector("#em-judet", "s => s.options[s.selectedIndex].textContent")
    assert (pg.input_value("#em-oras"), pg.input_value("#em-judet"), judet_ales) == ("Sector 2 Mun. Bucureşti", "B", "București"), (
        pg.input_value("#em-oras"), pg.input_value("#em-judet"), judet_ales)
    assert pg.input_value("#em-adresa") == ANAF_RO["adresa"]
    pg.fill("#em-l0-descriere", PRODUS)
    pg.wait_for_function("() => document.querySelector('#em-l0-pret_unitar').value !== ''", timeout=20000)
    pg.fill("#em-l0-cantitate", "2")   # ca `e2e_bloc_a._completeaza_factura`: linia are și cantitatea
    with pg.expect_response(lambda r: r.url.endswith("/facturi/emite") and r.request.method == "POST", timeout=30000) as rr:
        pg.click("#em-emite")
    corp = json.loads(rr.value.request.post_data)
    assert (corp["tert_oras"], corp["tert_judet"]) == ("Sector 2 Mun. Bucureşti", "B"), corp
    fid = rr.value.json()["factura_id"]
    pg.wait_for_selector("#em-rezultat.em-bun", timeout=30000)
    f = _ok(_api(patron, "GET", "/tenants/%d/facturi/%d" % (tid, fid)), "detaliu")
    assert (f["tert_oras"], f["tert_judet"], f["tert_adresa_completa"]) == ("Sector 2 Mun. Bucureşti", "B", ANAF_RO["adresa"]), f
    _deschide_factura(patron, firma_cv, fid)
    assert " ".join(pg.inner_text(".fd-antet .tip-micut").split()) == ANAF_RO["adresa"], pg.inner_text(".fd-antet")
    patron.captura("detaliu")
    text, _titlu = _pdf_text(_octeti(patron, "/tenants/%d/facturi/%d/pdf" % (tid, fid)))
    assert "STR. SINTETICA NR.1" in text and "Sector 2 Mun." not in text, text
    assert not re.search(r"SINTETICA NR\.1, B\b", text), text


def test_def_c61_clientul_strain_pastreaza_localitatea_si_regiunea(patron, firma_cv):
    """C61, partea clientului străin (neschimbată): țara Germania -> „Localitatea clientului (adresa de livrare din e-Factura)” și
    „Regiunea clientului”; lista județelor nu se mai vede; înapoi la România -> județul revine, regiunea dispare.
    MUTAȚIE (static/js/ecrane/emitere_ecran.js, ancora `    corp.querySelectorAll(".em-ro").forEach((e) => { e.hidden = s; });` -> gol):
    lista județelor rămâne la clientul german -> ROȘU."""
    from e2e_bloc_a import _deschide_emiterea
    _deschide_emiterea(patron, firma_cv["nume"])
    pg = patron.pg
    pg.select_option("#em-tara", "DE")
    pg.wait_for_selector("#em-regiune", state="visible", timeout=5000)
    patron.captura("strain")
    assert pg.inner_text("#em-oras-et") == "Localitatea clientului (adresa de livrare din e-Factura)"
    assert pg.is_hidden("#em-judet"), "lista județelor nu e pentru clientul străin"
    pg.select_option("#em-tara", "RO")
    pg.wait_for_selector("#em-judet", state="visible", timeout=5000)
    assert pg.is_hidden("#em-regiune") and pg.inner_text("#em-oras-et") == "Localitatea clientului"
