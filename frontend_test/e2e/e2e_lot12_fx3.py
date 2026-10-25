# -*- coding: utf-8 -*-
"""Lotul 12, pachetul fx3 (comenzile 12.2 / 12.3): testele de capăt la capăt pentru C84 și C157 pe „Transformă în factură”, C196 și C187.

  · C84 — decizia Costin 12.3 pct.7, verbatim: „livrarea intracomunitară de bunuri fără dovada transportului primește avertisment la
    emitere, nu refuz.” Pachetul fisc3 a pus întrebarea pe „Emite factură”; factura născută din proformă / aviz („Transformă în factură”)
    se emitea fără întrebare și fără avertisment. Acum: aceeași casetă „Ai dovada transportului?” în zona de mesaj a detaliului, iar „Nu
    încă, emite factura” emite cu avertismentul (CF art.294 alin.(3); HG 1/2016 pct.65).
  · C157 — decizia Costin 12.3 pct.3: „fără înregistrare art. 317, avertisment la emitere, nu refuz”. Avertismentul emiterii apare și sub
    confirmarea transformării (CF art.317 alin.(1) lit.b).
  · C196 (clasa 443.1) — „transformată în <nr>” din detaliul proformei arată seria separat, ca în Istoric („F1A nr. 3”), nu lipită.
  · C187 (clasa 216) — „Descarcă gestiunea lunii” pe luna în curs se refuză: nota care închide luna se scrie după încheierea ei (OMFP
    1802/2014 pct.286 alin.(4): K din rulajele cumulate „până la finele perioadei de referință”).

Pașii pe aplicația din index, pe baza de TEST, pe firme NOI (`firma_noua`, `e2e_bloc_e.firma_gv`), pregătite pe drumul ecranelor. Documentul de
plecare (proforma / avizul) se scrie pe ruta „Emite factură” (aceeași cerere ca formularul, `tip` = proformă / aviz). `sql` doar citește."""
import datetime as _dt
import json

import pytest

from conftest import firma_noua, sql
from core.pdf_util import serie_nr as _serie_nr   # numărul facturii, ca pe ecran (443.1)
from e2e_bloc_e import firma_gv  # noqa: F401 — firma global-valorică a rulării (C187)

AZI = _dt.date.today()
COD_CLIENT_IC = "DE811907980"   # codul probelor R187 / C78 / C110 / C154 / fisc3 (VIES pe plasă)


@pytest.fixture()
def firma_fx3():
    for f in firma_noua():
        yield f


def _platitor_gv(patron, f):
    """Plătitor de TVA, stoc global-valoric (marfa fără articol de stoc: la cantitativ-valoric linia de bunuri cere articolul)."""
    from e2e_bloc_a import _api, _ok, _profil, pregateste_firma
    pregateste_firma(patron, f)
    p = _profil(f)
    p["metoda_stoc"] = "global_valoric"
    _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % f["tenant_id"], p), "Date firmă (stoc global-valoric)")


def _document(patron, f, linie, tip="proforma", **client):
    """Proforma / avizul, pe ruta „Emite factură” (corpul formularului, `tip` = proformă / aviz); întoarce id-ul documentului."""
    from e2e_bloc_a import _api, _ok
    corp = dict({"linii": [linie], "tert_nume": "KUNDE E2E GMBH", "tert_cui": COD_CLIENT_IC, "tert_adresa": "Unter den Linden 1",
                 "tert_oras": "Berlin", "tert_judet": "Berlin", "tert_tara": "DE", "moneda": "RON", "tip_operatiune": "normal",
                 "bon_fiscal_nr": None, "bon_fiscal_data": None, "data_emitere": AZI.isoformat(), "data_scadenta": None, "tip": tip},
                **client)
    return _ok(_api(patron, "POST", "/tenants/%d/facturi/emite" % f["tenant_id"], corp), tip)["factura_id"]


def _lic(tip="proforma"):
    return {"descriere": "Marfa revanzare IC E2E", "cantitate": 2, "um": "buc", "pret_unitar": 100.0, "cota_tva": 0, "cota_propusa": 0,
            "categorie_tva": "livrare_ic"}


def _apasa_transforma(patron, f, did):
    """Istoric facturi -> documentul -> „Transformă în factură”; întoarce (pagina, răspunsul primei cereri a transformării)."""
    from e2e_bloc_a import _deschide_factura
    _deschide_factura(patron, f, did)
    pg = patron.pg
    pg.wait_for_selector("#fd-transforma", timeout=20000)
    with pg.expect_response(lambda r: r.url.endswith("/transforma") and r.request.method == "POST", timeout=30000) as rr:
        pg.click("#fd-transforma")
    return pg, rr.value


# ── C84 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("tip", ["proforma", "aviz"])
def test_def_c84_transforma_in_factura_livrarea_ic_intreaba_dovada_si_avertizeaza(patron, firma_fx3, tip):
    """C84 (decizia Costin 12.3 pct.7). Pașii: firmă plătitoare de TVA -> proforma / avizul unei livrări intracomunitare de bunuri (client
    DE811907980, „Marfa revanzare IC E2E”, 2 × 100,00, cota 0%, categoria „livrare intracomunitară”) -> Istoric facturi -> documentul ->
    „Transformă în factură”: caseta „Ai dovada transportului bunurilor în alt stat membru? …”, nimic scris (documentul încă netransformat)
    -> „Nu încă, emite factura”: „Factura <nr> a fost emisă.” și sub ea avertismentul (ce lipsește, ce se întâmplă cu scutirea); factura
    200,00, TVA 0,00, linia „livrare_ic”. Înainte: factura se emitea fără întrebare și fără avertisment.
    MUTAȚIA (`mut_lot12_fx3.json`): ramura `INTREABA_DOVADA_TRANSPORT` din handlerul „Transformă în factură” oprită -> caseta nu apare ->
    ROȘU; întrebarea oprită pe server (`intreaba_dovada=False` în `uc_tenants.proforma_transforma`) -> ROȘU; avertismentul neafișat -> ROȘU."""
    from core import intracomunitar as ic
    f = firma_fx3
    s = f["schema"]
    _platitor_gv(patron, f)
    did = _document(patron, f, _lic(), tip=tip)
    pg, r0 = _apasa_transforma(patron, f, did)
    assert r0.status == 422 and "INTREABA_DOVADA_TRANSPORT" in r0.text(), (r0.status, r0.text())   # întrebarea, nimic scris
    pg.wait_for_selector("#fd-act-rez .caseta-poarta #fd-dovada-nu", timeout=30000)
    patron.captura("intrebarea")
    # CF art.294 alin.(3): „Prin ordin al ministrului finanțelor publice se stabilesc, acolo unde este cazul, documentele necesare pentru a
    # justifica scutirea de taxă pentru operațiunile prevăzute la alin. (1) și (2)”
    assert " ".join(pg.inner_text("#fd-act-rez .caseta-poarta .cp-mesaj").split()) == (
        ic.INTREBARE_DOVADA_TRANSPORT + " Dacă nu o ai încă, factura se emite și îți spune ce lipsește.")
    assert pg.is_visible("#fd-dovada-da") and pg.is_visible("#fd-transforma"), "întrebarea vine înainte: documentul încă netransformat"
    assert sql('SELECT count(*) FROM "%s".facturi WHERE tip = %%s' % s, ("factura",))[0][0] == 0, "întrebarea nu scrie nimic"
    with pg.expect_response(lambda r: r.url.endswith("/transforma") and r.request.method == "POST", timeout=30000) as rr:
        pg.click("#fd-dovada-nu")
    r = rr.value.json()
    assert json.loads(rr.value.request.post_data) == {"dovada_transport": False}, rr.value.request.post_data
    av = pg.locator("#fd-act-rez .em-avertisment-emitere")
    av.first.wait_for(timeout=20000)
    patron.captura("emisa_cu_avertisment")
    # decizia Costin 12.3 pct.7: „avertisment la emitere, nu refuz”; HG 1/2016 pct.65: scutirile „sunt aplicate în măsura în care
    # persoanele impozabile pot justifica scutirea cu documentele prevăzute de instrucțiuni”
    assert " ".join(av.first.inner_text().split()) == ic.AVERTISMENT_LIC_FARA_DOVADA
    assert " ".join(pg.inner_text("#fd-act-rez").split()).startswith("Factura %s a fost emisă." % _serie_nr(r.get("serie"), r["numar"]))
    assert sql('SELECT total::text, tva::text FROM "%s".facturi WHERE id = %%s' % s, (r["factura_id"],)) == [("200.00", "0.00")]
    assert sql('SELECT categorie_tva FROM "%s".factura_linii WHERE factura_id = %%s' % s, (r["factura_id"],)) == [("livrare_ic",)]


# ── C157 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c157_transforma_in_factura_prestarea_ic_a_neinregistratului_art317_avertizeaza(patron, firma_fx3):
    """C157 (decizia Costin 12.3 pct.3). Pașii: firmă neplătitoare de TVA, NEînregistrată art.317, cu operațiuni intracomunitare ->
    proforma unui serviciu către clientul DE811907980 („Servicii de consultanta IT E2E”, 500,00) -> Istoric facturi -> proforma ->
    „Transformă în factură”: „Factura <nr> a fost emisă.” (nu un refuz), iar sub ea avertismentul: firma nu e înregistrată art.317, Codul
    fiscal cere înregistrarea înainte de prestare, ce să facă. Înainte: confirmarea fără avertisment.
    MUTAȚIA (`mut_lot12_fx3.json`): `arataAvertismenteEmitere(zonaRez, r.avertismente);` scos din handlerul transformării -> ROȘU."""
    from core import categorii_tva
    from e2e_lot12_fisc3 import _neinregistrat_art317
    f = firma_fx3
    _neinregistrat_art317(patron, f)
    did = _document(patron, f, {"descriere": "Servicii de consultanta IT E2E", "cantitate": 1, "um": "serv.", "pret_unitar": 500.0,
                                "cota_tva": 0, "cota_propusa": 0, "categorie_tva": None})
    pg, rr = _apasa_transforma(patron, f, did)
    assert rr.status == 200, (rr.status, rr.text())
    av = pg.locator("#fd-act-rez .em-avertisment-emitere")
    av.first.wait_for(timeout=30000)
    patron.captura("avertismentul")
    # CF art.317 alin.(1) lit.b — înregistrarea neplătitorului care „prestează servicii care au locul în alt stat membru, pentru care
    # beneficiarul serviciului este persoana obligată la plata taxei [...], înainte de prestarea serviciului”
    assert " ".join(av.first.inner_text().split()) == categorii_tva.AVERTISMENT_FARA_ART317
    assert " ".join(pg.inner_text("#fd-act-rez").split()).startswith("Factura "), pg.inner_text("#fd-act-rez")
    assert pg.locator("#fd-vezi-transformata").count() == 1, "proforma e transformată (nu e un refuz)"


# ── C196 (clasa 443.1) ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c196_transformata_in_arata_seria_separat(patron, firma_fx3):
    """C196. Pașii: proforma unui serviciu către clientul român -> „Transformă în factură” -> detaliul proformei: butonul „transformată în
    <serie> nr. <număr>” (ca în Istoric, `numarCuSerie`), nu „transformată în <serie><număr>” lipit.
    MUTAȚIA (`mut_lot12_fx3.json`): `numarCuSerie(f.transformat_in_serie, f.transformat_in_numar)` -> `f.transformat_in_numar` -> ROȘU."""
    from e2e_bloc_a import CLIENT, PRODUS
    f = firma_fx3
    _platitor_gv(patron, f)
    did = _document(patron, f, {"descriere": PRODUS, "cantitate": 1, "um": "ora", "pret_unitar": 150.0, "cota_tva": 21, "cota_propusa": 21},
                    tert_nume=CLIENT["#em-nume"], tert_cui=CLIENT["#em-cui"], tert_adresa=CLIENT["#em-adresa"], tert_oras="București",
                    tert_judet="B", tert_tara="RO")
    pg, rr = _apasa_transforma(patron, f, did)
    r = rr.json()
    pg.wait_for_selector("#fd-vezi-transformata", timeout=20000)
    patron.captura("transformata_in")
    assert " ".join(pg.inner_text("#fd-vezi-transformata").split()) == "transformată în %s" % _serie_nr(r.get("serie"), r["numar"])
    assert r.get("serie") and " nr. " in _serie_nr(r.get("serie"), r["numar"]), r


# ── C187 (clasa 216) ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c187_descarcarea_gestiunii_pe_luna_in_curs_nu_se_scrie(patron, firma_gv):  # noqa: F811
    """C187. Pașii: firmă global-valorică -> Stocuri (luna în curs): „Descarcă gestiunea lunii” e inactiv, cu motivul lângă el
    („Descărcarea gestiunii lunii se face după ce luna se încheie.”, C198); cererea butonului (aceeași rută, `POST /stocuri/descarcare`)
    e refuzată: „Descărcarea gestiunii lunii LL/AAAA se contează după ce luna se încheie: luna LL/AAAA nu s-a încheiat (azi e …) — se închide
    după ultima ei zi.”, nicio notă „DESC-GV-AAAA-LL” scrisă. Luna trecută: butonul activ, fără refuzul ăsta. Înainte: notele 607 / 378 /
    4428.02 = 371 se scriau pe o lună neîncheiată.
    [C198, lotul 12 — aliniere] până la C198 refuzul se citea după clicul pe buton; acum butonul nu se mai oferă pe luna în curs, deci
    refuzul serverului se probează pe cererea lui, iar ecranul pe butonul inactiv cu motivul.
    TEMEI: OMFP 1802/2014 pct.286 alin.(4) — K din valorile cumulate „până la finele perioadei de referință”.
    MUTAȚIA (`mut_lot12_fx3.json`): `_uc_comun._cere_luna_incheiata(an, luna, "Descărcarea gestiunii lunii")` scos din
    `uc_tenants.stocuri_descarcare` -> descărcarea se scrie / alt răspuns -> ROȘU."""
    from core import inchidere_luna as il
    from e2e_bloc_a import _api
    from e2e_bloc_e import _card, _la_luna
    f = firma_gv
    pg = patron.pg
    _card(patron, f, "stocuri", "#s-desc")
    _la_luna(patron, "#s-prev", AZI.year, AZI.month)
    patron.captura("luna_in_curs_inactiv")
    assert pg.is_disabled("#s-desc") and pg.get_attribute("#s-desc", "aria-describedby") == "s-desc-motiv"           # [C198]
    assert " ".join(pg.inner_text("#s-desc-motiv").split()) == "Descărcarea gestiunii lunii se face după ce luna se încheie."
    r = _api(patron, "POST", "/tenants/%d/stocuri/descarcare?an=%d&luna=%d" % (f["tenant_id"], AZI.year, AZI.month), {})
    asteptat = "Descărcarea gestiunii lunii %02d/%d se contează după ce luna se încheie: %s" % (AZI.month, AZI.year,
                                                                                               il.luna_in_curs(AZI.year, AZI.month))
    assert r["status"] == 400 and asteptat in json.dumps(r["json"], ensure_ascii=False), r
    assert sql('SELECT count(*) FROM "%s".inregistrari WHERE numar = %%s' % f["schema"], ("DESC-GV-%d-%02d" % (AZI.year, AZI.month),)) == [(0,)]   # AZI-dat-de-test: luna pe care testul a cerut-o / a datat Z-ul
    trecuta = AZI.replace(day=1) - _dt.timedelta(days=1)
    _card(patron, f, "stocuri", "#s-desc")
    _la_luna(patron, "#s-prev", trecuta.year, trecuta.month)
    assert not pg.is_disabled("#s-desc") and pg.locator("#s-desc-motiv").count() == 0
    pg.click("#s-desc")
    pg.click("#ca-ok")
    pg.wait_for_function("() => (document.querySelector('#s-mesaj') || {innerText: ''}).innerText.trim() !== ''", timeout=60000)
    m2 = " ".join(pg.inner_text("#s-mesaj").split())
    patron.captura("luna_trecuta")
    assert "se contează după ce luna se încheie" not in m2, m2
