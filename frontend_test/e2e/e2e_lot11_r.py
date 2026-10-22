# -*- coding: utf-8 -*-
"""Lotul 11, subagentul R (comanda Costin 11.1, verbatim în DECIZII „Comanda 11.1”): C77 — o a doua declarație pe aceeași perioadă pleca
la ANAF marcată „inițială” (`d_rec="0"` scris constant în generator).

Pașii contabilului, pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ (`firma_noua`) pe impozit pe profit:
  1. Declarații -> D101, anul 2025 (an încheiat — 383) -> „Continuă”: declarația e inițială (XML `d_rec="0"`, nicio mențiune);
  2. Control fiscal: D101 pe 2025 marcată „depusă în afara iConta.eu” pe 20.05.2026, recipisa 123456789 (ruta butonului, cu sesiunea
     contabilului);
  3. Declarații -> D101, 2025 -> „Continuă” din nou: ecranul spune „Rectificativă la declarația depusă în afara iConta.eu pe 20.05.2026,
     recipisa 123456789.”, iar XML-ul are `d_rec="1"` (OPANAF 206/2025 anexa 2 cap.I pct.3).

Datele de pornire, pe DRUMUL APLICAȚIEI (nimic scris direct în bază — garda `core/test_e2e_fara_date_fabricate.py`; clasa lui 429: nota
„validată” scriind direct starea ocolea validarea): Date firmă (`POST firma-profil/date`: registrul comerțului, CAEN, adresa, declarantul),
vectorul fiscal (`POST vector`: impozit pe profit, plătitoare de TVA, decont lunar) și o notă manuală din 2025 (5311 = 707, 10.000 lei)
scrisă în Registru jurnal (`POST jurnal`) și validată cu „Validează” (`POST jurnal/{id}/valideaza`, dreptul „Poate valida” al
contabilului-șef). CUI-ul firmei: `cui_cu_control` (cifra de control verificată)."""
import pytest

from conftest import firma_noua, linie_nota, sql
from e2e_bloc_c import _declaratie_pas1
from e2e_bloc_d import PATRON, _api as _api_cont

AN = 2025


def _ruta(cale, corp, ce):
    """O cerere pe ruta ecranului, cu sesiunea contabilului-șef (aceleași gărzi, același autor ca pe ecran)."""
    st, r = _api_cont(PATRON, "POST", cale, corp)
    assert st == 200 and (not isinstance(r, dict) or r.get("ok") is not False), (ce, st, r)
    return r


@pytest.fixture()
def firma_r():
    for f in firma_noua():
        tid = f["tenant_id"]
        _ruta("/tenants/%d/firma-profil/date" % tid,
              {"reg_com": "J40/1234/2020", "caen": "6920", "adresa": "Str. Probei nr. 1", "oras": "București", "judet": "București",
               "declarant_nume": "Popescu", "declarant_prenume": "Ion", "declarant_functie": "Administrator"}, "Date firmă")
        _ruta("/tenants/%d/vector" % tid, {"regim_fiscal": "profit", "platitor_tva": True, "tip_decont": "lunar", "operatiuni_ic": False},
              "vectorul fiscal")
        nid = _ruta("/tenants/%d/jurnal" % tid, {"data": "2025-06-15", "descriere": "probă C77", "document_ref": "NC E2E-C77",
                                                 "linii": [linie_nota("5311", "707", 10000)]}, "nota din 2025")["id"]
        _ruta("/tenants/%d/jurnal/%d/valideaza" % (tid, nid), {}, "validarea notei")
        assert sql('SELECT status FROM "%s".inregistrari WHERE id = %%s' % f["schema"], (nid,)) == [("validata",)]
        try:
            yield f
        finally:
            sql("DELETE FROM public.declaratii_depuse WHERE tenant_id = %s AND sursa = 'extern'", (f["tenant_id"],))


def _pas2(patron, firma):
    pg = patron.pg
    _declaratie_pas1(patron, firma["nume"], "d101", AN)
    pg.wait_for_selector(".fereastra:last-of-type details.dec-xml, .fereastra:last-of-type .dec-eroare", timeout=90000)
    t = " ".join(patron.fereastra().split())
    assert pg.locator(".fereastra:last-of-type .dec-eroare").count() == 0, t[:2000]
    xml = pg.locator(".fereastra:last-of-type details.dec-xml pre").text_content()
    return t, xml


def test_def_c77_d101_regenerata_dupa_depunere_iese_rectificativa(patron, firma_r):
    """C77. „A doua depunere pe aceeași perioadă [...] pleacă la ANAF marcată «inițială», nu «rectificativă».” Pașii: D101 2025 ->
    inițială; marcată „depusă în afara iConta.eu” (20.05.2026, recipisa 123456789); D101 2025 din nou -> „Rectificativă la declarația
    depusă în afara iConta.eu pe 20.05.2026, recipisa 123456789.” pe ecran și `d_rec="1"` în XML."""
    from e2e_bloc_a import _api, _ok
    pg = patron.pg
    t0, xml0 = _pas2(patron, firma_r)
    patron.captura("d101_initiala")
    assert 'd_rec="0"' in xml0, xml0[:600]
    assert pg.locator("#dec-rectificativa").count() == 0, t0[:1500]
    _ok(_api(patron, "POST", "/control-fiscal/%d/depusa-extern" % firma_r["tenant_id"],
             {"tip": "d101", "an": AN, "luna": 12, "data_depunere": "2026-05-20", "recipisa": "123456789"}), "marcare depusă extern")
    t1, xml1 = _pas2(patron, firma_r)
    patron.captura("d101_rectificativa")
    assert 'd_rec="1"' in xml1, xml1[:600]
    mentiune = " ".join(pg.inner_text(".fereastra:last-of-type #dec-rectificativa").split())
    assert mentiune == "Rectificativă la declarația depusă în afara iConta.eu pe 20.05.2026, recipisa 123456789.", mentiune
