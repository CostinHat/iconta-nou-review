# -*- coding: utf-8 -*-
"""Lotul 10, comanda 10.1 (Costin 20.10.2026), deficiența 428 — PRIORITAR — TVA la încasare (CF art.282): „facturile emise poartă
mențiunea obligatorie și înregistrează TVA pe 4428; fiecare încasare (bancă, casă, compensare) legată de factură mută automat partea
încasată în 4427; D300 și D394 urmează exigibilitatea”.

Pașii contabilului pe aplicația din index, pe baza de TEST, pe firma nouă a fișierului (`firma_e2e`): firma aplică sistemul de azi
(perioada din „Date firmă”, scrisă direct — ecranul ei e al subagentului F și are testul lui) -> „Emite factură” 1.000 + 210 TVA către
un client din România -> PDF-ul facturii poartă „TVA la încasare” și nota e 4111 = 704 + 4111 = 4428 -> Casă -> „+ Dispoziție nouă”:
încasare de la client 605 lei, factura bifată -> „Adaugă” -> nota încasării are 4428 = 4427 105 -> D300 al lunii: rd.9 (21%) 500 / 105.
Clientul: CUI 18547290 — cifra de control verificată cu algoritmul din CLAUDE.md."""
import base64
import io

from conftest import sql
from e2e_bloc_a import AZI, PRODUS, _api, _ok, pregateste_firma

_CLIENT = {"tert_nume": "Client Incasare E2E SRL", "tert_cui": "18547290", "tert_adresa": "Str. Probei 1", "tert_oras": "Sector 1",
           "tert_judet": "B", "tert_tara": "RO"}


def _pdf(e, cale):
    """PDF-ul facturii, din pagina contului (aceeași sesiune ca ecranul)."""
    b64 = e.pg.evaluate("""async (c) => { const t = sessionStorage.getItem('iconta_token');
        const x = await fetch(c, {headers: {Authorization: 'Bearer ' + t}}); const b = new Uint8Array(await x.arrayBuffer());
        let s = ''; b.forEach((v) => { s += String.fromCharCode(v); }); return btoa(s); }""", cale)
    return base64.b64decode(b64)


def _note_factura(schema, fid):
    return sql('SELECT l.cont_debit, l.cont_credit, l.suma::text FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l '
               "ON l.inregistrare_id = i.id WHERE i.factura_id = %%s ORDER BY i.id, l.id" % (schema, schema), (fid,))


def test_def_428_factura_in_sistem_are_mentiunea_si_incasarea_din_casa_muta_tva(patron, firma_e2e):
    """428. Pașii: firma aplică TVA la încasare de azi -> „Emite factură” 1.000 + 21% -> PDF: „TVA la încasare”; nota 4111 = 4428 210 ->
    Casă -> dispoziție: încasare de la client 605 lei, factura bifată -> „Adaugă” -> nota: 5311 = 4111 605 și 4428 = 4427 105 -> D300
    al lunii: rândul 9 (21%) bază 500, TVA 105 (partea încasată), nu 1.000 / 210."""
    import pypdf
    s, tid = firma_e2e["schema"], firma_e2e["tenant_id"]
    pregateste_firma(patron, firma_e2e, platitor=True, regim_fiscal="profit")
    sql('INSERT INTO "%s".tva_incasare_perioade (de_la) VALUES (%%s)' % s, (AZI.replace(day=1).isoformat(),))
    corp = dict(_CLIENT, linii=[{"descriere": PRODUS, "cantitate": 1, "um": "ora", "pret_unitar": 1000.0, "cota_tva": 21, "cota_propusa": 21,
                                 "articol_id": None, "categorie_tva": None}],
                moneda="RON", tip_operatiune="normal", bon_fiscal_nr=None, bon_fiscal_data=None, data_emitere=AZI.isoformat(),
                data_scadenta=AZI.isoformat(), tip="factura")
    fid = _ok(_api(patron, "POST", "/tenants/%d/facturi/emite" % tid, corp), "factura în sistem")["factura_id"]
    # CF art.319 alin.(20) lit.p): mențiunea „TVA la încasare” pe factură
    text = "".join(p.extract_text() for p in pypdf.PdfReader(io.BytesIO(_pdf(patron, "/tenants/%d/facturi/%d/pdf" % (tid, fid)))).pages)
    assert "TVA la încasare" in text, text
    # CF art.282 alin.(3): TVA-ul facturii e neexigibil până la încasare -> 4428
    assert ("4111", "4428", "210.00") in _note_factura(s, fid), _note_factura(s, fid)
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    pg.click("#fa-casa")
    pg.wait_for_selector("#c-toggle", timeout=20000)
    pg.click("#c-toggle")
    pg.fill("#c-data", AZI.isoformat())
    pg.select_option("#c-cat", "incasare_client")
    pg.fill("#c-suma", "605")
    pg.fill("#c-cui", _CLIENT["tert_cui"])
    pg.dispatch_event("#c-campuri", "change")
    pg.wait_for_selector("#c-facturi [data-cf='%d']" % fid, timeout=20000)
    pg.check("#c-facturi [data-cf='%d']" % fid)
    patron.captura("dispozitia")
    pg.click("#c-adauga")
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('605,00')", timeout=20000)
    patron.captura("dupa")
    # CF art.282 alin.(8): „fiecare încasare totală sau parțială se consideră că include și taxa aferentă” — 605 -> 105 trece în 4427
    note = _note_factura(s, fid)
    assert ("5311", "4111", "605.00") in note and ("4428", "4427", "105.00") in note, note
    sql('UPDATE "%s".inregistrari SET status = \'validata\' WHERE factura_id = %%s' % s, (fid,))
    from core import d300, db
    from core.common import Perioada
    with db.get_conn(s) as c:
        prof, fac = d300.pull(c, s, Perioada(AZI.year, luna=AZI.month))
        res = d300.calcul_d300(prof, Perioada(AZI.year, luna=AZI.month), fac)
    assert (res.R.get("R9_1"), res.R.get("R9_2")) == (500, 105), res.R
