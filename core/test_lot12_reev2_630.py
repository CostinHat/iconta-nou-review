# -*- coding: utf-8 -*-
"""[lotul 12, comanda 12.2 pct.17, deficiența 630] Reevaluare valută (F1, 10/2026).

Ce spunea ecranul: la luna neîncheiată Curs BNR și Diferență goale, cu „mai vechi cu 8 zile… flux întrerupt”; „Cursul găsit: 5.3495” cu
punct; „De completat: 1” fără să spună ce; F1A nr. 8 fără stornarea ei, F1A nr. 9; soldul în lei 323,64 față de 323,65 pe nota F1A nr. 14.

Temei — OMFP 1802/2014 (`anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`): pct.325 alin.(1) „La finele fiecărei luni, creanțele și
datoriile în valută se evaluează la cursul de schimb al pieței valutare, comunicat de Banca Națională a României din ultima zi bancară a
lunii în cauză.”; alin.(2) lit.b „cursul de schimb al pieței valutare comunicat de Banca Națională a României, din ultima zi bancară a lunii
în cauză, pentru evaluarea creanțelor și datoriilor în valută, a disponibilităților în valută”. Până la publicarea cursului acelei zile,
diferența e provizorie și nu se înregistrează.

Schemă efemeră din template, perioadă SINTETICĂ 06/2099 (30.06.2099 marți = ultima zi bancară), moneda GBP (niciun alt test nu scrie
cursuri GBP 2099); cursurile scrise în `public.curs_bnr_zilnic` sunt șterse la ieșire. Partenerul: DANTE INTERNATIONAL SA, CUI 14399840
(cifra de control verificată cu algoritmul din CLAUDE.md).
"""
import datetime
import io

import pytest

from core import db as _db
from core import reevaluare_valuta as _rv
from core import tenant_provisioning as _tprov

SCH = "efemer_630"
CTX = {"uid": 1, "firm": 1}
CHEIE = "p:4111:14399840:GBP"
ZILE_CURS = ("2099-06-22", "2099-06-26", "2099-06-30")


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def _nota(cur, data, linii, factura_id=None, sursa="manual", status="validata"):
    cur.execute("INSERT INTO inregistrari (data, factura_id, descriere, sursa, status, document_ref) VALUES (%s,%s,'t',%s,%s,'t') "
                "RETURNING id", (data, factura_id, sursa, status))
    nid = cur.fetchone()[0]
    for d, c, s in linii:
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)", (nid, d, c, s))
    return nid


def _factura(cur, numar, data, total, curs, total_lei, storno_din=None):
    cur.execute("INSERT INTO facturi (numar, serie, data_emitere, total, tva, moneda, directie, status, tert_nume, tert_cui, curs_bnr, "
                "total_lei, tva_lei, data_curs, storno_din_id) VALUES (%s, 'EX', %s, %s, 0, 'GBP', 'emisa', 'emisa', "
                "'DANTE INTERNATIONAL SA', '14399840', %s, %s, 0, %s, %s) RETURNING id",
                (numar, data, total, curs, total_lei, data, storno_din))
    return cur.fetchone()[0]


def _cursuri(*zile_curs):
    """Cache-ul BNR pentru GBP în 06/2099: exact zilele date (celelalte șterse)."""
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("DELETE FROM public.curs_bnr_zilnic WHERE moneda = 'GBP' AND data = ANY(%s::date[])", (list(ZILE_CURS),))
        for d, k in zile_curs:
            # fixtura-sintetica-ok: anul 2099, moneda GBP — nicio zi reală; șters la ieșire
            cur.execute("INSERT INTO public.curs_bnr_zilnic (data, moneda, curs) VALUES (%s, 'GBP', %s)", (d, k))
        c.commit()


@pytest.fixture()
def firma(monkeypatch):
    """EX nr. 8 (10.06.2099): 121,00 GBP la 5,3272, `total_lei` 644,59; nota VALIDATĂ 4111 = 707 532,72 + 4111 = 4427 111,87.
    EX nr. 9 (12.06.2099): stornarea lui EX nr. 8, −121,00 GBP, nota în CIORNĂ 4111 = 707 −532,72 + 4111 = 4427 −111,87.
    EX nr. 14 (20.06.2099): 60,50 GBP la 5,3495, `total_lei` 323,64 (rotunjit pe total); nota VALIDATĂ pe cote: 4111 = 707 267,48 +
    4111 = 4427 56,17 = 323,65 — soldul din 4111, la ban. Contul 5124.GBP („Cont BT GBP”) cu 1.000,00 lei: soldul în valută se cere."""
    from core import auth_api, uc_curs_bnr
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
            cur.execute("INSERT INTO firma_profil (id, nume, cui) VALUES (1, 'F SRL', 'RO14399840')")
            cur.execute("INSERT INTO plan_conturi (simbol, denumire) VALUES ('5124.GBP', 'Cont BT GBP')")
            f8 = _factura(cur, "8", "2099-06-10", 121, "5.3272", "644.59")
            f9 = _factura(cur, "9", "2099-06-12", -121, "5.3272", "-644.59", storno_din=f8)
            f14 = _factura(cur, "14", "2099-06-20", "60.50", "5.3495", "323.64")
            _nota(cur, "2099-06-10", [("4111", "707", "532.72"), ("4111", "4427", "111.87")], f8, sursa="facturi")
            n9 = _nota(cur, "2099-06-12", [("4111", "707", "-532.72"), ("4111", "4427", "-111.87")], f9, sursa="facturi", status="ciorna")
            _nota(cur, "2099-06-20", [("4111", "707", "267.48"), ("4111", "4427", "56.17")], f14, sursa="facturi")
            _nota(cur, "2099-06-05", [("5124.GBP", "456", "1000")])
        c.commit()
    monkeypatch.setattr(auth_api, "schema_tenant", lambda conn, uid, tid: SCH)
    monkeypatch.setattr(uc_curs_bnr, "asigura_cursul", lambda *a, **k: None)   # fără rețea: cache-ul e cel scris de test
    yield {"f8": f8, "f9": f9, "f14": f14, "n9": n9}
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        cur.execute("DELETE FROM public.curs_bnr_zilnic WHERE moneda = 'GBP' AND data = ANY(%s::date[])", (list(ZILE_CURS),))
        c.commit()


def _azi(monkeypatch, zi):
    from core import common
    monkeypatch.setattr(common, "azi_ro", lambda: zi)


def _propunere(**kw):
    from core import uc_reevaluare
    return uc_reevaluare.reevaluare_valuta_propunere(1, 2099, 6, CTX, **kw)


def _el(p, cheie=CHEIE):
    return next(e for e in p["elemente"] if e["cheie"] == cheie)


def _valideaza_storno(n9):
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("UPDATE %s.inregistrari SET status = 'validata' WHERE id = %%s" % SCH, (n9,))
        c.commit()


def test_def_630_soldul_in_lei_e_cel_din_4111_la_ban_iar_stornarea_e_numita(firma, monkeypatch):
    """Stornarea EX nr. 9 în ciornă: soldul e cel din 4111 VALIDAT (644,59 + 323,65 = 968,24; 121,00 + 60,50 = 181,50 GBP), iar EX nr. 9
    apare la „nu intră”, numită ca stornarea lui EX nr. 8. Validată: intră lângă EX nr. 8, iar soldul e 323,65 (nota), nu 323,64 (totalul
    facturii). MUTAȚIE: `lei` din `facturi.total_lei` în loc de nota de contare -> 968,23 / 323,64 -> pică."""
    _azi(monkeypatch, datetime.date(2099, 7, 2))
    _cursuri(("2099-06-30", "5.4000"))
    p = _propunere()
    e = _el(p)
    # OMFP 1802/2014 pct.325 alin.(1): se evaluează creanța din evidență — 4111 al partenerului, din notele validate
    assert (e["sold_valuta"], e["lei_evidenta"]) == ("181.50", "968.24"), e
    assert e["document"] == "Factură EX nr. 8 din 10.06.2099, Factură EX nr. 14 din 20.06.2099", e
    neinc = {n["document"]: n["motiv"] for n in p["neincluse"]}
    assert neinc == {"Factură EX nr. 9 din 12.06.2099 (stornarea EX nr. 8)":
                     "nota ei de contare e ciornă — valideaz-o în Registrul jurnal, apoi reevaluarea o cuprinde"}, neinc
    _valideaza_storno(firma["n9"])
    e = _el(_propunere())
    assert (e["sold_valuta"], e["lei_evidenta"]) == ("60.50", "323.65"), e
    assert e["document"] == ("Factură EX nr. 8 din 10.06.2099, Factură EX nr. 9 din 12.06.2099 (stornarea EX nr. 8), "
                             "Factură EX nr. 14 din 20.06.2099"), e
    # pct.325 alin.(1): 60,50 × 5,4000 = 326,70; 326,70 − 323,65 = 3,05 -> 765 (curs final: fără marcaj provizoriu)
    assert (e["curs_bnr"], e["data_curs"], e["diferenta"], e["cont_diferenta"], e.get("curs_provizoriu")) == (
        "5.4000", "2099-06-30", "3.05", "765", None), e


def test_def_630_luna_neincheiata_arata_diferenta_provizorie_la_ultimul_curs(firma, monkeypatch):
    """Azi 23.06.2099, ultimul curs publicat 22.06 (vechime față de 30.06: 8 zile — înainte: „mai vechi cu 8 zile… flux întrerupt”,
    Curs BNR și Diferență goale). Acum: cursul și diferența la 22.06, marcate provizorii, cu textul simplu; generarea e refuzată.
    MUTAȚIE: `curs_provizoriu` întoarce None -> elementul n-are marcajul (și, la cursul vechi, iar n-are curs) -> pică."""
    from core import erori, uc_reevaluare
    _valideaza_storno(firma["n9"])
    _azi(monkeypatch, datetime.date(2099, 6, 23))
    _cursuri(("2099-06-22", "5.3495"))
    p = _propunere()
    e = _el(p)
    text = ("Cursul BNR din ultima zi bancară a lunii (30.06.2099) nu e publicat încă. Diferența e provizorie, la ultimul curs publicat: "
            "5,3495 din 22.06.2099; nota se generează cu cursul din 30.06.2099.")
    # 60,50 × 5,3495 = 323,64475 -> 323,64 (ROUND_HALF_UP); 323,64 − 323,65 = −0,01 -> 665 (diferența provizorie)
    assert (e["curs_bnr"], e["data_curs"], e["diferenta"], e["cont_diferenta"], e["curs_provizoriu"], e.get("motiv_curs")) == (
        "5.3495", "2099-06-22", "-0.01", "665", text, None), e
    assert p["curs_provizoriu"] == [text] and p["totaluri"]["provizoriu"] is True, p["totaluri"]
    with pytest.raises(erori.CerereGresita):   # luna în curs: nota se generează după ultima zi a lunii
        uc_reevaluare.reevaluare_valuta_genereaza(1, {"an": 2099, "luna": 6, "completari": {"c5124.GBP": {"sold_valuta": "180"}}}, CTX)


def test_def_630_luna_incheiata_fara_cursul_ultimei_zile_nu_genereaza(firma, monkeypatch):
    """Azi 02.07.2099, luna încheiată, dar în aplicație e numai cursul din 26.06 (înainte: luat ca final, vechime 4 zile ≤ 5). Acum:
    provizoriu („nu e încă în aplicație”), închiderea rămâne oprită, generarea e refuzată cu textul. Cu cursul din 22.06 (10 zile față de
    azi): fluxul e întrerupt — fără cifră, cu „Cursul găsit: 5,3495” (virgulă, nu punct)."""
    from core import erori, uc_reevaluare
    _valideaza_storno(firma["n9"])
    _azi(monkeypatch, datetime.date(2099, 7, 2))
    _cursuri(("2099-06-26", "5.3800"))
    e = _el(_propunere())
    assert e["curs_provizoriu"].startswith("Cursul BNR din ultima zi bancară a lunii (30.06.2099) nu e încă în aplicație"), e
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)   # pe tranzacție: nu rămâne pe conexiunea din pool (lotul 10, 430)
        assert [x["cheie"] for x in _rv.de_reevaluat(_rv.propunere(cur, SCH, 2099, 6, cu_ciorna_lunii=True))].count(CHEIE) == 1
    with pytest.raises(erori.Conflict) as ei:   # OMFP 1802/2014 pct.325 alin.(2) lit.b: numai cu cursul ultimei zile bancare
        uc_reevaluare.reevaluare_valuta_genereaza(1, {"an": 2099, "luna": 6, "completari": {"c5124.GBP": {"sold_valuta": "180"}}}, CTX)
    assert ei.value.detaliu["mesaj"] == e["curs_provizoriu"], ei.value.detaliu
    _cursuri(("2099-06-22", "5.3495"))
    e = _el(_propunere())
    assert e["curs_bnr"] is None and e.get("curs_provizoriu") is None, e
    assert e["motiv_curs"].endswith("Cursul găsit: 5,3495."), e["motiv_curs"]


def test_def_630_de_completat_spune_ce(firma, monkeypatch):
    """„De completat: 1” -> ce anume: soldul în valută al contului 5124.GBP. Elementul fără curs nu mai e numărat ca „de completat”
    (cursul nu-l scrie contabilul)."""
    _azi(monkeypatch, datetime.date(2099, 6, 23))
    _cursuri(("2099-06-22", "5.3495"))
    t = _propunere()["totaluri"]
    assert (t["de_completat"], t["de_completat_ce"]) == (1, ["soldul în valută pe contul 5124.GBP (Cont BT GBP)"]), t
    _cursuri()
    t = _propunere()["totaluri"]
    assert (t["de_completat"], t["de_completat_ce"]) == (1, ["soldul în valută pe contul 5124.GBP (Cont BT GBP)"]), t


def test_def_630_curs_provizoriu_pur():
    """Funcția pură, pe calendarul legal (`curs_bnr.ziua_bancara_asteptata`, regula sfârșitului de lună)."""
    d = datetime.date
    # 31.10.2026 sâmbătă -> ultima zi bancară 30.10.2026; azi 24.10, ultimul curs 23.10 (cazul lui Costin pe F1)
    assert _rv.curs_provizoriu(d(2026, 10, 31), d(2026, 10, 23), "5.3495", d(2026, 10, 24)) == (
        "Cursul BNR din ultima zi bancară a lunii (30.10.2026) nu e publicat încă. Diferența e provizorie, la ultimul curs publicat: "
        "5,3495 din 23.10.2026; nota se generează cu cursul din 30.10.2026.")
    assert _rv.curs_provizoriu(d(2026, 10, 31), d(2026, 10, 30), "5.3495", d(2026, 11, 2)) is None        # cursul ultimei zile: final
    assert _rv.curs_provizoriu(d(2026, 10, 31), d(2026, 10, 29), "5.3", d(2026, 10, 30)) == (
        "Cursul BNR din ultima zi bancară a lunii (30.10.2026) se publică abia azi. Diferența e provizorie, la ultimul curs publicat: "
        "5,3000 din 29.10.2026; nota se generează cu cursul din 30.10.2026.")
