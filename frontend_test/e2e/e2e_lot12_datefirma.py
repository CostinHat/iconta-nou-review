# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.1 (verbatim în DECIZII „Comanda 12.1”), pachetul datefirma — Date firmă și chitanțe:

  * 147 „Luna preluării” editabilă, cu propunere și limită — drumul neacoperit până azi: luna aleasă (08) și, DUPĂ alegere, o notă mai veche
    (06): luna efectivă e acum plafonată la luna primei note, iar ecranul spune de ce (decizia Costin 08.10 §6 pct.4: „niciodată după luna
    primei note”);
  * 169 „Luna preluării” arată „---------- ----” — câmpul golit de contabil (așa arată Chromium o lună goală) revine, la ieșirea din câmp,
    la propunere;
  * 168 descrierea notei chitanței doar numele clientului — retest 08.10 pct.19: „trebuie să conțină chitanța și factura stinsă”; drumul
    neacoperit: încasarea facturii din Casă (456), care emite singură chitanța.

Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ de test (`firma_noua` + `pregateste_firma`). DATELE DE PORNIRE
scrise pe drumul aplicației (declarate): nota manuală din 06/2026 intră prin funcția Registrului jurnal (`jurnal_api.creeaza`, ca la 147 din
blocul E); factura prin ruta formularului de emitere (`emite_api`). Clientul DANTE INTERNATIONAL SA, CUI 14399840 — cifra de control
verificată cu algoritmul din CLAUDE.md.

Temei: 147 / 169 — N/A, regulă de produs (decizia Costin 08.10.2026 §6 pct.4); 168 — OMFP 2634/2015 anexa 2, Chitanța (cod 14-4-1):
„documente justificative de înregistrare în registrul de casă [...] și în contabilitate a încasărilor și plăților efectuate în numerar”.
"""
import datetime as _dt

import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import AZI, CLIENT, emite_api, pregateste_firma
from e2e_bloc_e import _asteapta_text, _nota, _sterge_note
from e2e_lot11_a455 import _casa, _dispozitie


@pytest.fixture(scope="module")
def firma_df():
    for f in firma_noua():
        yield f


def _explicatii_jurnal(e):
    """[lotul 12, 617] Explicația fiecărei note din Registrul jurnal de pe ecran: celula „Explicație” a rândului (`tbody.tn-nota >
    tr.tn-rand`, a treia: Nr. crt., Data, Explicație) — locul unde antetul vechi al notei (`.pf-frand-nume`, citit de
    `e2e_bloc_e._randuri_jurnal`) arăta descrierea ei."""
    return e.pg.evaluate("() => [...[...document.querySelectorAll('.fereastra')].pop().querySelectorAll('tbody.tn-nota[data-nota-id] > tr.tn-rand')]"
                         ".map((r) => r.cells[2].innerText)")


def _date_firma(e, f):
    e.firma(f["nume"])
    e.pg.click("#fa-datefirma")
    e.pg.wait_for_selector("#df-luna_preluare", timeout=30000)


def _ajutor_lunii(e):
    return e.pg.locator("label.camp:has(#df-luna_preluare) .camp-ajutor").inner_text()


def _salveaza(e):
    """„Salvează” -> mesajul salvării (oricare: „Datele firmei au fost salvate” sau „Salvat. Lipsesc …”)."""
    pg = e.pg
    pg.click("#df-salveaza")
    pg.wait_for_function("() => { const m = document.querySelector('.fereastra:last-of-type #df-msg'); "
                         "return !!m && /alvat/.test(m.innerText); }", timeout=30000)
    m = pg.inner_text(".fereastra:last-of-type #df-msg")
    assert "NU s-a salvat" not in m, m


def test_def_147_luna_aleasa_dupa_o_nota_mai_veche_arata_luna_notei(patron, firma_df):
    """147. Pașii: firma fără note -> Date firmă -> „Luna preluării” 08/2026 -> „Salvează” (se salvează: nicio notă) -> în Registrul jurnal
    se scrie o notă din 15.06.2026 -> Date firmă: câmpul arată 06/2026 (luna efectivă), iar ajutorul spune „Luna aleasă, 08/2026, e după
    prima notă din jurnal (06/2026, scrisă după alegere): luna preluării se socotește 06/2026.” -> „Salvează” fără să atingă luna: niciun
    refuz lângă câmp (înainte: „nu poate fi după luna primei note”, deci nicio salvare în Date firmă nu mai trecea), luna aleasă rămâne."""
    f = firma_df
    s = f["schema"]
    pregateste_firma(patron, f)
    pg = patron.pg
    nid = None
    try:
        assert sql('SELECT count(*) FROM "%s".inregistrari' % s) == [(0,)]          # firma nouă: nicio notă
        _date_firma(patron, f)
        pg.fill("#df-luna_preluare", "2026-08")
        _salveaza(patron)
        assert sql('SELECT luna_preluare FROM "%s".firma_profil WHERE id = 1' % s) == [(_dt.date(2026, 8, 1),)]
        nid = _nota(f, "2026-06-15", [{"debit": "5311", "credit": "1012", "suma": "100.00"}])
        _date_firma(patron, f)
        assert pg.input_value("#df-luna_preluare") == "2026-06", pg.input_value("#df-luna_preluare")
        ajutor = _ajutor_lunii(patron)
        # decizia Costin 08.10 §6 pct.4: „niciodată după luna primei note”
        assert ("Luna aleasă, 08/2026, e după prima notă din jurnal (06/2026, scrisă după alegere): luna preluării se socotește 06/2026."
                in ajutor), ajutor
        pg.locator("#df-luna_preluare").scroll_into_view_if_needed()
        patron.captura("luna_plafonata_la_prima_nota")
        _salveaza(patron)
        assert pg.locator('.fereastra:last-of-type .msg-eroare[data-camp="df-luna_preluare"]').count() == 0
        assert sql('SELECT luna_preluare FROM "%s".firma_profil WHERE id = 1' % s) == [(_dt.date(2026, 8, 1),)]
        patron.captura("salvat_fara_refuz")
    finally:
        # date-de-pornire: curățenie după probă — luna preluării a firmei de probă înapoi la nealeasă (nu date ale probei)
        sql('UPDATE "%s".firma_profil SET luna_preluare = NULL WHERE id = 1' % s)
        if nid:
            _sterge_note(f, [nid])


def test_def_169_luna_golita_revine_la_propunere(patron, firma_df):
    """169. Pașii: firma cu o notă din 15.06.2026 și luna preluării nealeasă -> Date firmă: câmpul arată 06/2026 (propunerea) -> contabilul
    golește câmpul și iese din el: câmpul arată iar 06/2026, nu „---------- ----” (luna goală în Chromium) -> „Salvează”: luna rămâne
    propunere (nimic fixat în bază)."""
    f = firma_df
    s = f["schema"]
    pregateste_firma(patron, f)
    pg = patron.pg
    nid = _nota(f, "2026-06-15", [{"debit": "5311", "credit": "1012", "suma": "100.00"}])
    try:
        assert sql('SELECT luna_preluare FROM "%s".firma_profil WHERE id = 1' % s) == [(None,)]
        _date_firma(patron, f)
        assert pg.input_value("#df-luna_preluare") == "2026-06"
        pg.fill("#df-luna_preluare", "")
        assert pg.input_value("#df-luna_preluare") == ""                 # golit (pe ecran: „---------- ----”)
        pg.locator("#df-luna_preluare").blur()
        assert pg.input_value("#df-luna_preluare") == "2026-06", "câmpul golit rămâne „---------- ----”"
        assert "Completată cu propunerea: 06/2026" in _ajutor_lunii(patron)
        pg.locator("#df-luna_preluare").scroll_into_view_if_needed()
        patron.captura("golit_revine_la_propunere")
        _salveaza(patron)
        assert sql('SELECT luna_preluare FROM "%s".firma_profil WHERE id = 1' % s) == [(None,)]
    finally:
        _sterge_note(f, [nid])


def test_def_168_incasarea_facturii_din_casa_numeste_chitanta_in_nota(patron, firma_df):
    """168. Pașii: factura emisă azi -> Casă -> „+ Dispoziție nouă”: încasare de la client, factura bifată, fără document -> „Adaugă” ->
    „Chitanța E2ECH nr. … a fost emisă” -> Registrul jurnal (luna curentă): nota încasării spune chitanța (seria-numărul) și factura stinsă,
    nu doar clientul / factura (înainte: „Încasare de la client — factura … — DANTE INTERNATIONAL SA”, fără chitanță)."""
    f = firma_df
    s = f["schema"]
    pregateste_firma(patron, f)                     # seria chitanțelor E2ECH (Date firmă)
    fac = emite_api(patron, f)
    fid = fac["factura_id"]
    (total,) = sql('SELECT total::text FROM "%s".facturi WHERE id = %%s' % s, (fid,))[0]
    pg = patron.pg
    _casa(patron, f)
    _dispozitie(pg, "incasare_client", total, cui=CLIENT["#em-cui"], factura_id=fid)
    _asteapta_text(patron, "a fost emisă")
    ((serie, nr),) = sql('SELECT serie, numar FROM "%s".chitante WHERE factura_id = %%s AND NOT anulata' % s, (fid,))
    eticheta = "chitanța %s-%s" % (serie, nr)
    (ser_f, nr_f) = sql('SELECT serie, numar FROM "%s".facturi WHERE id = %%s' % s, (fid,))[0]
    factura = "factura %s nr. %s din %s" % (ser_f, nr_f[len(ser_f):] if ser_f and nr_f.startswith(ser_f) else nr_f,
                                            AZI.strftime("%d.%m.%Y"))   # AZI-dat-de-test (data emiterii și a dispoziției)
    patron.firma(f["nume"])
    pg.click("#fa-jurnal")
    _asteapta_text(patron, eticheta)
    nota = [n for n in _explicatii_jurnal(patron) if eticheta in n]
    assert len(nota) == 1, _explicatii_jurnal(patron)
    # retest 08.10 pct.19: „trebuie să conțină chitanța și factura stinsă”
    assert "Încasare de la client — %s — %s" % (eticheta, factura) in nota[0], nota[0]
    assert "DANTE INTERNATIONAL SA" in nota[0], nota[0]
    pg.locator(".fereastra:last-of-type [data-nota-id]", has_text=eticheta).first.scroll_into_view_if_needed()
    patron.captura("nota_incasarii_din_casa")
