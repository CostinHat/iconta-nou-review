# -*- coding: utf-8 -*-
"""Lotul 10, deficiența 428, deciziile Costin 20.10.2026 (verbatim în DECIZII „Lotul 10: deciziile lui Costin la întrebările din lot”):
„Construiesc acum” — tabelă de compensări (factura emisă ↔ factura primită, suma, data) și ecran; fiecare compensare stinge cele două
facturi și mută TVA-ul prin același punct ca banca și casa. „Bifă pe client” — câmpul „persoană afiliată (art.7 pct.26)” pe client; factura
către el ia regulile generale (4427) chiar dacă firma e în sistem.

Pașii contabilului pe aplicația din index, pe baza de TEST, pe firma nouă a fișierului (`firma_e2e`), firma în sistemul TVA la încasare de
la începutul lunii (perioada scrisă direct — ecranul ei are testul lui, `e2e_lot10_date_firma`). Ecranele: „Compensări” (`#fa-compensari`,
`static/js/ecrane/compensari_ecran.js`) și „Clienți” (`#fa-clienti`, `static/js/ecrane/clienti_ecran.js`), legate din meniul firmei.
Partenerii: X (CUI 18547290) și clientul afiliat A (CUI 24736200) — cifra de control verificată cu algoritmul din CLAUDE.md."""
import io

from conftest import sql
from e2e_bloc_a import AZI, PRODUS, _api, _ok, pregateste_firma

_X = {"tert_nume": "Partener Compensare E2E SRL", "tert_cui": "18547290", "tert_adresa": "Str. Probei 1", "tert_oras": "Sector 1",
      "tert_judet": "B", "tert_tara": "RO"}
_A = {"tert_nume": "Client Afiliat E2E SRL", "tert_cui": "24736200", "tert_adresa": "Str. Probei 2", "tert_oras": "Sector 2",
      "tert_judet": "B", "tert_tara": "RO"}


def _in_sistem(firma):
    s = firma["schema"]
    sql('INSERT INTO "%s".tva_incasare_perioade (de_la) SELECT %%s WHERE NOT EXISTS (SELECT 1 FROM "%s".tva_incasare_perioade)' % (s, s),
        (AZI.replace(day=1).isoformat(),))


def _emite(e, tid, partener, pret):
    corp = dict(partener, linii=[{"descriere": PRODUS, "cantitate": 1, "um": "ora", "pret_unitar": float(pret), "cota_tva": 21,
                                   "cota_propusa": 21, "articol_id": None, "categorie_tva": None}],
                moneda="RON", tip_operatiune="normal", bon_fiscal_nr=None, bon_fiscal_data=None, data_emitere=AZI.isoformat(),
                data_scadenta=AZI.isoformat(), tip="factura")
    return _ok(_api(e, "POST", "/tenants/%d/facturi/emite" % tid, corp), "factura către %s" % partener["tert_nume"])["factura_id"]


def _primita_contata(firma, partener, baza):
    """Factura primită de la partener (500 + 21%), contată: firma în sistem -> 4428 = 401 (CF art.297 alin.(3))."""
    from core import contare_facturi as _cf, db
    s = firma["schema"]
    [(fid,)] = sql('INSERT INTO "%s".facturi (numar, serie, data_emitere, directie, total, tva, total_lei, tva_lei, curs_bnr, moneda, tert_nume, '
                   "tert_cui, tert_tara, tert_platitor_tva, status) VALUES ('P-E2E-1', 'FZ', %%s, 'primita', %%s, %%s, %%s, %%s, 1, 'RON', "
                   "%%s, %%s, 'RO', true, 'emisa') RETURNING id" % s,
                   (AZI.isoformat(), baza * 1.21, baza * 0.21, baza * 1.21, baza * 0.21, partener["tert_nume"], partener["tert_cui"]))
    sql('INSERT INTO "%s".factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva, cont_cheltuiala) '
        "VALUES (%%s, 'servicii', 1, %%s, 21, '628')" % s, (fid, baza))
    with db.get_conn(s) as c:
        with _cf.cursor_dict(c) as cur:
            _cf.contabilizeaza(cur, "", fid, automat=True, cont_cheltuiala=None)
        c.commit()
    return fid


def _linii_compensare(schema):
    return sql('SELECT l.cont_debit, l.cont_credit, l.suma::text FROM "%s".compensari z JOIN "%s".inregistrari_linii l '
               "ON l.inregistrare_id = z.inregistrare_id ORDER BY l.id" % (schema, schema))


def test_def_428_compensarea_muta_tva_la_incasare(patron, firma_e2e):
    """428 (compensarea). Pașii: firma în sistem; factura emisă către X 1.000 + 21% și factura primită de la X 500 + 21%, contate ->
    meniul firmei -> „Compensări”: partenerul X, perechea propusă cu 605,00 (restul cel mai mic) -> data de azi, „Ordin de compensare”
    nr 7 -> „Generează compensarea” -> confirmarea numește ordinul și nota -> nota: 401 = 4111 605, 4428 = 4427 105 (emisa), 4426 = 4428
    105 (primita); factura emisă e „încasată parțial” (605 din 1.210), cea primită „plătită”."""
    s, tid = firma_e2e["schema"], firma_e2e["tenant_id"]
    pregateste_firma(patron, firma_e2e, platitor=True, regim_fiscal="profit")
    _in_sistem(firma_e2e)
    fe = _emite(patron, tid, _X, 1000)
    fp = _primita_contata(firma_e2e, _X, 500)
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    pg.click("#fa-compensari")
    # partenerul se ALEGE (DS cap.17, „— alege —”; nu e preselectat) — apoi apar perechile lui
    pg.wait_for_selector("#cz-partener", timeout=20000)
    pg.select_option("#cz-partener", _X["tert_cui"])
    pg.wait_for_selector("#cz-tabel", timeout=20000)
    # Codul civil art.1616: „până la concurenţa celei mai mici dintre ele” — perechea propusă cu 605,00
    assert pg.input_value("#cz-suma-0").replace(",", ".") in ("605.00", "605"), pg.input_value("#cz-suma-0")
    assert "Partener Compensare E2E SRL" in pg.locator("#cz-partener option:checked").inner_text()
    pg.fill("#cz-data", AZI.isoformat())
    pg.fill("#cz-numar", "7")
    patron.captura("propunerea")
    pg.click("#cz-genereaza")
    pg.wait_for_function("() => (document.querySelector('#cz-mesaj') || {}).innerText && "
                         "document.querySelector('#cz-mesaj').innerText.includes('Ordin de compensare nr 7')", timeout=20000)
    patron.captura("confirmarea")
    assert "605,00 lei compensați" in pg.inner_text("#cz-mesaj")
    # HG 1/2016 pct.26 alin.(7): încasarea se face și prin „compensarea”; CF art.282 alin.(8) — 605 include TVA-ul 105
    assert _linii_compensare(s) == [("401", "4111", "605.00"), ("4428", "4427", "105.00"), ("4426", "4428", "105.00")], _linii_compensare(s)
    assert sql('SELECT document_ref, status FROM "%s".inregistrari WHERE id = (SELECT inregistrare_id FROM "%s".compensari)' % (s, s)) == \
        [("Ordin de compensare nr 7 din %s" % AZI.strftime("%d.%m.%Y"), "ciorna")]   # AZI-dat-de-test (#cz-data)
    # „fiecare compensare stinge cele două facturi”
    e = _ok(_api(patron, "GET", "/tenants/%d/facturi/%d" % (tid, fe)), "factura emisă")
    p = _ok(_api(patron, "GET", "/tenants/%d/facturi/%d" % (tid, fp)), "factura primită")
    assert (e["stare_incasare"]["stare"], e["stare_incasare"]["incasat"]) == ("partial", "605.00"), e["stare_incasare"]
    assert p["stare_incasare"]["stare"] == "incasata", p["stare_incasare"]
    # după generare, partenerul nu mai are nimic de compensat (P1 plătită integral)
    pg.wait_for_selector("#cz-gol, #cz-fara-perechi, #cz-alege", timeout=20000)


def _client_a(patron, firma):
    """Fișa clientului A (persoană juridică), cu bifa „Persoană afiliată” pe Nu — starea de pornire (firma e2e se refolosește)."""
    s, tid = firma["schema"], firma["tenant_id"]
    gasit = sql('SELECT id FROM "%s".clienti WHERE cui = %%s' % s, ("RO" + _A["tert_cui"],))   # fișa există deja (alt test al modulului)
    cid = gasit[0][0] if gasit else _ok(_api(patron, "POST", "/tenants/%d/clienti" % tid, {"nume": _A["tert_nume"], "cui": "RO" + _A["tert_cui"]}),
                                         "fișa clientului")["client_id"]
    sql('UPDATE "%s".clienti SET afiliat = false WHERE id = %%s' % s, (cid,))
    return cid


def test_def_c72_bifa_persoana_afiliata_se_salveaza_din_ecran(patron, firma_e2e):
    """C72 (găsită de e2e la 428). Pașii: meniul firmei -> „Clienți” -> la clientul A „Persoană afiliată (Cod fiscal art.7 pct.26)”: Da ->
    „Salvează” devine activ -> clic -> confirmarea „… bifat ca persoană afiliată …”, iar fișa clientului are bifa. Până la C72 butonul
    rămânea inactiv: selectul pierdea clasa `cl-afiliat` (al doilea atribut `class`, ignorat de browser), deci alegerea nu era văzută.
    MUTAȚIA: `api.selectDaNu` cu forma veche (`<select class="camp-input" … ${atribute}>`) -> ROȘU (butonul rămâne inactiv)."""
    s = firma_e2e["schema"]
    cid = _client_a(patron, firma_e2e)
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    pg.click("#fa-clienti")
    pg.wait_for_selector("#cl-afiliat-c%d" % cid, timeout=20000)
    pg.select_option(".fereastra:last-of-type #cl-afiliat-c%d" % cid, "true")   # Da / Nu cu „— alege —” (DS cap.17), nu căsuță
    pg.click(".fereastra:last-of-type #cl-salveaza-c%d" % cid, timeout=10000)
    pg.wait_for_function("() => (document.querySelector('#cl-mesaj') || {}).innerText && "
                         "document.querySelector('#cl-mesaj').innerText.includes('bifat ca persoană afiliată')", timeout=20000)
    patron.captura("bifa")
    assert sql('SELECT afiliat FROM "%s".clienti WHERE id = %%s' % s, (cid,)) == [(True,)]


def test_def_428_clientul_afiliat_ramane_pe_regulile_generale(patron, firma_e2e):
    """428 (beneficiarul afiliat). Pașii: firma în sistem; clientul A are fișă, bifat „persoană afiliată” (salvarea bifei din ecran e
    testul C72) -> „Emite factură” 1.000 + 21% către A -> nota 4111 = 4427 210 (nu 4428), PDF-ul fără „TVA la încasare” (CF art.282
    alin.(6) lit.d)."""
    import pypdf
    s, tid = firma_e2e["schema"], firma_e2e["tenant_id"]
    pregateste_firma(patron, firma_e2e, platitor=True, regim_fiscal="profit")
    _in_sistem(firma_e2e)
    cid = _client_a(patron, firma_e2e)
    sql('UPDATE "%s".clienti SET afiliat = true WHERE id = %%s' % s, (cid,))
    fid = _emite(patron, tid, _A, 1000)
    # CF art.282 alin.(6) lit.d): beneficiarul afiliat -> regulile generale: TVA exigibil la emitere, 4427
    note = sql('SELECT l.cont_debit, l.cont_credit, l.suma::text FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l '
               "ON l.inregistrare_id = i.id WHERE i.factura_id = %%s ORDER BY l.id" % (s, s), (fid,))
    assert ("4111", "4427", "210.00") in note and not any("4428" in (d, c) for d, c, _v in note), note
    assert sql('SELECT beneficiar_afiliat FROM "%s".facturi WHERE id = %%s' % s, (fid,)) == [(True,)]
    from e2e_lot10_tva_incasare import _pdf
    text = "".join(x.extract_text() for x in pypdf.PdfReader(io.BytesIO(_pdf(patron, "/tenants/%d/facturi/%d/pdf" % (tid, fid)))).pages)
    assert "TVA la încasare" not in text, text


def test_def_c73_clientul_cu_cui_existent_e_refuzat_numit_nu_500(patron, firma_e2e):
    """C73 (găsită de e2e la 428). Pașii: clientul A are fișă -> a doua fișă cu același CUI (alt tab / alt drum care creează fișa):
    răspunsul e refuzul numit „Există deja clientul … cu CUI-ul … (în lista Clienți) …”, cu clientul existent, nu eroarea 500 a bazei
    (`clienti_cui_uniq`); fișa nu se dublează. Garda fixturii prinde orice cerere 5xx a paginii.
    MUTAȚIA: `refuza_dublura` scos din `clienti_api.creeaza_client` -> ROȘU (500)."""
    s, tid = firma_e2e["schema"], firma_e2e["tenant_id"]
    cid = _client_a(patron, firma_e2e)
    r = _api(patron, "POST", "/tenants/%d/clienti" % tid, {"nume": _A["tert_nume"] + " (a doua)", "cui": "RO" + _A["tert_cui"]})
    patron.captura()
    assert r["status"] == 409, r
    assert "Există deja clientul" in str(r["json"]) and "RO" + _A["tert_cui"] in str(r["json"]), r
    assert sql('SELECT count(*) FROM "%s".clienti WHERE cui = %%s' % s, ("RO" + _A["tert_cui"],)) == [(1,)], cid
