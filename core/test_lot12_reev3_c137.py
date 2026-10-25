# -*- coding: utf-8 -*-
"""C137 (lotul 12, pachetul reev3) — clasa 216 la reevaluarea în valută: nota de reevaluare scrisă înainte ca luna ei să se încheie.

Decizia Costin 12.3 pct.2, verbatim: „C137: fără marcă nouă acum; notele de reevaluare folosesc tipul de document existent. Revenim după
pilot dacă apare nevoia.” Nota de reevaluare are sursa „operatiuni” și documentul intern „Notă de calcul” — amândouă comune tuturor
operațiunilor speciale —, deci semnalul C127 (`inchidere_luna.note_contate_inainte`, după sursă) n-o vedea. Fără schemă nouă, nota se
recunoaște după rândurile ei din `reevaluari_valuta` (legătura existentă, scrisă odată cu nota din lotul 10), iar cele de dinainte de
legătură (formularul manual, 04.07–21.10.2026) după descrierea pe care o scria aplicația.

ROȘU înainte (codul de dinainte de C137): nota de reevaluare scrisă pe 25.07 pentru luna 07 nu era în `note_contate_inainte`, iar
migrarea C127 n-o scotea.

Temei: OMFP 1802/2014 pct.325 alin.(1) — „La finele fiecărei luni, creanțele și datoriile în valută se evaluează la cursul de schimb al
pieței valutare, comunicat de Banca Națională a României din ultima zi bancară a lunii în cauză” (textul citat și în
`core/test_lot10_reevaluare.py`): o notă scrisă înainte de ultima zi bancară a lunii nu poate avea cursul ei. OMFP 1802/2014 pct.69 (nota
validată nu se modifică, se corectează printr-o notă de corecție) — de aceea nota validată se semnalează, nu se atinge.
Perioade SINTETICE 07/2097 (schemă efemeră din template, ștearsă la ieșire; cursul BNR din 31.07.2097 scris și șters de test).
"""
import datetime
import io

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov

SCH = "efemer_l12_reev3"
CURS = ("2097-07-31", "EUR", "5.0000")
CTX = {"uid": 1, "firm": 1}


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture()
def firma(monkeypatch):
    """Factura emisă 1.000 EUR la 4,97 (10.07.2097), neîncasată: 4111 = 707 4.970,00 (validată). Cursul BNR la 31.07.2097 (miercuri):
    EUR 5,0000 -> diferența 30,00 pe 765."""
    from core import auth_api, common, uc_curs_bnr
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
            cur.execute("INSERT INTO firma_profil (id, nume, cui) VALUES (1, 'F SRL', 'RO14399840')")   # CUI cu cifra de control verificată
            cur.execute("INSERT INTO facturi (numar, serie, data_emitere, total, tva, moneda, directie, status, tert_nume, curs_bnr, "
                        "total_lei, tva_lei, data_curs) VALUES ('1', 'EX', '2097-07-10', 1000, 0, 'EUR', 'emisa', 'emisa', 'Client GmbH', "
                        "4.97, 4970, 0, '2097-07-09') RETURNING id")
            fe = cur.fetchone()[0]
            cur.execute("INSERT INTO inregistrari (data, factura_id, descriere, sursa, status, document_ref) VALUES "
                        "('2097-07-10', %s, 'Contare EX 1', 'facturi', 'validata', 'Factură EX nr. 1') RETURNING id", (fe,))
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '4111', '707', 4970)",
                        (cur.fetchone()[0],))
            cur.execute("INSERT INTO public.curs_bnr_zilnic (data, moneda, curs) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING", CURS)
        c.commit()
    monkeypatch.setattr(common, "azi_ro", lambda: datetime.date(2097, 9, 15))
    monkeypatch.setattr(auth_api, "schema_tenant", lambda conn, uid, tid: SCH)
    monkeypatch.setattr(uc_curs_bnr, "asigura_cursul", lambda *a, **k: None)
    yield fe
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute("DELETE FROM public.curs_bnr_zilnic WHERE data = %s AND moneda = %s", CURS[:2])
        c.commit()


def _genereaza():
    """Nota de reevaluare a lunii 07/2097, pe drumul aplicației (`uc_reevaluare.reevaluare_valuta_genereaza`)."""
    from core import uc_reevaluare
    r = uc_reevaluare.reevaluare_valuta_genereaza(1, {"an": 2097, "luna": 7}, CTX)
    assert (r["venit"], r["elemente"]) == ("30.00", 1), r
    return r["inregistrare_id"]


def _scrisa_la(nid, cand):
    """Momentul scrierii notei (starea lăsată de codul de dinainte de 216 / C137, care scria nota în luna ei)."""
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("UPDATE %s.inregistrari SET creat_la = %%s WHERE id = %%s" % SCH, (cand, nid))
        c.commit()


def _semnalate(ids=None):
    from core import inchidere_luna as il
    with _db.get_conn() as c, c.cursor() as cur:
        return il.note_contate_inainte(cur, SCH, ids)


MOTIV_REEV = ("Nota a fost scrisă pe 25.07.2097, înainte ca luna 07/2097 să se încheie: cifrele ei pot să nu cuprindă tot ce s-a întâmplat în "
              "lună. Verific-o față de soldurile în valută de la sfârșitul lunii și de cursul BNR din ultima ei zi bancară; o diferență se "
              "corectează printr-o notă de corecție — nota validată nu se modifică.")


def test_c137_nota_de_reevaluare_scrisa_inainte_de_incheierea_lunii_e_semnalata(firma):
    """MUTAȚIE: scoaterea ramurii `reevaluari_valuta` din `inchidere_luna.note_contate_inainte` -> nota nu mai e semnalată -> pică."""
    nid = _genereaza()
    _scrisa_la(nid, "2097-07-25 10:00:00+03")
    sem = _semnalate()
    assert list(sem) == [nid], sem
    assert sem[nid]["motiv"] == MOTIV_REEV, sem[nid]["motiv"]
    assert (sem[nid]["reevaluare"], sem[nid]["status"], sem[nid]["luna_an"]) == (True, "ciorna", "07/2097"), sem[nid]
    assert list(_semnalate([nid])) == [nid]   # aceeași regulă pe rândurile Registrului jurnal (`ids`)
    # scrisă după ce luna s-a încheiat (02.08.2097): nu e semnalată
    _scrisa_la(nid, "2097-08-02 09:00:00+03")
    assert _semnalate() == {}


def test_c137_alta_nota_de_calcul_scrisa_in_luna_ei_nu_e_semnalata(firma):
    """Tipul de document („Notă de calcul”) e comun tuturor operațiunilor speciale: o notă de calcul fără rânduri de reevaluare (dividende,
    leasing, provizioane…), scrisă în luna ei, nu închide luna și nu se semnalează — altfel ecranul ar induce în eroare (CLAUDE.md §9).
    MUTAȚIE: recunoașterea după documentul „Notă de calcul” în locul rândurilor `reevaluari_valuta` -> și nota asta e semnalată -> pică."""
    from core import documente_interne as di, repo_contabilitate as rc
    nid = _genereaza()
    with _db.get_conn() as c, c.cursor() as cur:
        alta = rc.nota_operatiune_ciorna(cur, SCH, "2097-07-31", "Dividende propuse 2097")[0]
        rc.adauga_linie_partener(cur, SCH, alta, "117", "457", 1000, None, None)
        c.commit()
    for x in (nid, alta):
        _scrisa_la(x, "2097-07-25 10:00:00+03")
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT id, document_ref FROM %s.inregistrari WHERE id = ANY(%%s) ORDER BY id" % SCH, ([nid, alta],))
        docs = cur.fetchall()
    assert [di.e_generat(d, "nota_calcul") for _i, d in docs] == [True, True], docs   # același tip de document pe amândouă
    assert list(_semnalate()) == [nid]


def test_c137_notele_vechi_de_reevaluare_fara_randuri_se_recunosc_dupa_descrierea_aplicatiei(firma):
    """Datele existente: formularul manual (04.07–21.10.2026, scos în lotul 11) scria „Reevaluare solduri valuta la <data> (OMFP 1802 …”,
    întâi cu sursa „banca” (`nota_banca_ciorna`), apoi „operatiuni” — fără rânduri în `reevaluari_valuta` înainte de lotul 10. Amândouă,
    validate și scrise în luna lor, se semnalează; aceeași descriere pe o notă manuală (scrisă de om) nu."""
    with _db.get_conn() as c, c.cursor() as cur:
        ids = []
        for sursa, desc in (("banca", "Reevaluare solduri valuta la 2097-07-31 (OMFP 1802 pct. 316, curs BNR)"),
                            ("operatiuni", "Reevaluare solduri valuta la 2097-07-31 (OMFP 1802/2014 pct.325, curs BNR)"),
                            ("manual", "Reevaluare solduri valuta la 2097-07-31 (OMFP 1802/2014 pct.325, curs BNR)")):
            # documentul: validarea îl cere (`regula_nota`); notele vechi îl aveau scris de om sau de documentul intern (06.10.2026)
            cur.execute("INSERT INTO %s.inregistrari (data, descriere, sursa, status, document_ref, creat_la) VALUES ('2097-07-31', %%s, %%s, "
                        "'ciorna', 'Notă de calcul nr 9 din 31.07.2097', '2097-07-31 12:00:00+03') RETURNING id" % SCH, (desc, sursa))
            ids.append(cur.fetchone()[0])
            cur.execute("INSERT INTO %s.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, '4111', '765', 30)"
                        % SCH, (ids[-1],))
            cur.execute("UPDATE %s.inregistrari SET status = 'validata' WHERE id = %%s" % SCH, (ids[-1],))
        c.commit()
    sem = _semnalate()
    assert sorted(sem) == ids[:2], sem
    assert [sem[i]["reevaluare"] for i in ids[:2]] == [True, True]


def test_c137_migrarea_scoate_ciorna_de_reevaluare_si_numeste_nota_validata(firma):
    """Datele existente (regula 3a): `core/migrare_note_luna_neincheiata.py` — ciorna de reevaluare scrisă în luna ei se scoate (rândurile
    ei din `reevaluari_valuta` cad cu ea, urma în `public.audit_log`), nota de reevaluare VALIDATĂ rămâne și se numește. A doua rulare:
    nimic. Tranzacția migrării se anulează la ieșire.
    MUTAȚIE: aceeași cu primul test (ramura `reevaluari_valuta` scoasă) -> `scoase == []` -> pică."""
    from core import migrare_note_luna_neincheiata as mig
    nid = _genereaza()
    _scrisa_la(nid, "2097-07-25 10:00:00+03")
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("INSERT INTO %s.inregistrari (data, descriere, sursa, status, document_ref, creat_la) VALUES ('2097-06-30', "
                    "'Reevaluare solduri valuta la 2097-06-30 (OMFP 1802 pct. 316, curs BNR)', 'banca', 'ciorna', 'Extras de cont 6', "
                    "'2097-06-30 12:00:00+03') RETURNING id" % SCH)
        v = cur.fetchone()[0]
        cur.execute("INSERT INTO %s.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, '4111', '765', 20)"
                    % SCH, (v,))
        cur.execute("UPDATE %s.inregistrari SET status = 'validata' WHERE id = %%s" % SCH, (v,))
        c.commit()
    with _db.get_conn() as c:
        try:
            r = mig.aplica(c, SCH)
            assert r == {"scoase": [nid], "validate": [(v, "06/2097")], "ramase": []}, r
            with c.cursor() as cur:
                cur.execute("SELECT count(*) FROM %s.inregistrari WHERE id = %%s" % SCH, (nid,))
                assert cur.fetchone()[0] == 0
                cur.execute("SELECT count(*) FROM %s.reevaluari_valuta" % SCH)
                assert cur.fetchone()[0] == 0   # rândurile ciornei au căzut cu ea (ON DELETE CASCADE)
                cur.execute("SELECT detalii->>'motiv', detalii->'linii' FROM public.audit_log WHERE actiune = "
                            "'stergere_ciorna_luna_neincheiata' AND detalii->>'schema' = %s", (SCH,))
                assert cur.fetchall() == [(mig.MOTIV, [["4111", "765", "30.00"]])]
            assert mig.verifica(c, SCH) is True
            assert mig.aplica(c, SCH) == {"scoase": [], "validate": [(v, "06/2097")], "ramase": []}
        finally:
            c.rollback()
