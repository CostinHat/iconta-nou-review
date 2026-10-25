# -*- coding: utf-8 -*-
"""C187 (lotul 12, pachetul fx3) — clasa 216 la descărcarea gestiunii global-valorice: nota care închide luna se scria pe luna în curs.

Regula 216 (decizia Costin 08.10.2026 pct.11 / retestul 09.10.2026, `uc_comun._cere_luna_incheiata`): nota care închide o lună se scrie
numai după încheierea ei. Salariile, amortizarea și reevaluarea în valută o respectau; descărcarea gestiunii global-valorice
(`uc_tenants.stocuri_descarcare` -> `stocuri_api.descarca_luna`, nota „Descarcare gestiune LL/AAAA”, `numar` = „DESC-GV-AAAA-LL”) nu:
„Descarcă gestiunea lunii” pe 10/2026, azi 24.10.2026, scria notele 607 / 378 / 4428.02 = 371 dintr-o lună care nu s-a terminat.

ROȘU înainte (codul de dinainte de C187): `stocuri_descarcare(…, 2099, 10, …)` cu „azi” 15.10.2099 scria notele; `note_contate_inainte`
nu le vedea (sursa „stocuri” nu era între notele care închid luna), iar migrarea C127 nu le scotea.

TEMEI: OMFP 1802/2014 pct.286 alin.(4) — coeficientul de repartizare se calculează din „Diferențe de preț aferente intrărilor în cursul
perioadei, cumulat de la începutul exercițiului financiar până la finele perioadei de referință” și „Valoarea intrărilor în cursul
perioadei la preț de înregistrare, cumulat de la începutul exercițiului financiar până la finele perioadei de referință” (textul citat în
`stocuri_api.descarca_luna`): înainte de finele lunii, rulajele ei nu sunt întregi. OMFP 1802/2014 pct.69 (nota validată nu se modifică, se
corectează printr-o notă de corecție) — de aceea nota validată se semnalează, nu se atinge.
Perioade SINTETICE 2099 (schemă efemeră din template, ștearsă la ieșire); `public.audit_log` scris de migrare numai în tranzacție anulată.
"""
import datetime
import io
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_l12_fx3_c187"
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
    """Firmă global-valorică: stoc inițial 371 1.210 / 378 400 / 4428.02 210 (K = 0,4) și o vânzare validată de mărfuri pe 15.10.2099
    (4111 = 707 500, 4111 = 4427 105). `azi` se schimbă prin `common.azi_ro` (aceeași sursă ca `inchidere_luna.luna_in_curs`)."""
    from core import auth_api, common
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("INSERT INTO %s.firma_profil (id, nume, cui, platitor_tva, metoda_stoc, tva_la_incasare, tip_decont) "
                        "VALUES (1, 'GV SRL', 'RO14399840', true, 'global_valoric', false, 'L')" % SCH)   # CUI cu cifra de control verificată
            for cont, d, k in (("371", 1210, 0), ("378", 0, 400), ("4428.02", 0, 210)):
                cur.execute("INSERT INTO %s.solduri_initiale (cont, sold_debitor, sold_creditor) VALUES (%%s, %%s, %%s)" % SCH, (cont, d, k))
            cur.execute("INSERT INTO %s.inregistrari (data, descriere, sursa, status, document_ref) VALUES "
                        "('2099-10-15', 'Vanzare marfa', 'facturi', 'validata', 'Factură GV nr. 1') RETURNING id" % SCH)
            nid = cur.fetchone()[0]
            for d, k, s in (("4111", "707", 500), ("4111", "4427", 105)):
                cur.execute("INSERT INTO %s.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, %%s, %%s, %%s)"
                            % SCH, (nid, d, k, Decimal(s)))
        c.commit()
    azi = {"d": datetime.date(2099, 10, 15)}
    monkeypatch.setattr(common, "azi_ro", lambda: azi["d"])
    monkeypatch.setattr(auth_api, "schema_tenant", lambda conn, uid, tid: SCH)
    yield azi
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def _note_descarcare():
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT id, status FROM %s.inregistrari WHERE numar = 'DESC-GV-2099-10' ORDER BY id" % SCH)
        return cur.fetchall()


def _semnalate(ids=None):
    from core import inchidere_luna as il
    with _db.get_conn() as c, c.cursor() as cur:
        return il.note_contate_inainte(cur, SCH, ids)


def _scrisa_la(ids, cand):
    """Momentul scrierii notelor (starea lăsată de codul de dinainte de C187, care scria descărcarea în luna ei)."""
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("UPDATE %s.inregistrari SET creat_la = %%s WHERE id = ANY(%%s)" % SCH, (cand, list(ids)))
        c.commit()


def _descarca_direct():
    """Descărcarea scrisă cum o scria aplicația înainte de C187 (fără verificarea lunii): `stocuri_api.descarca_luna`."""
    from core import stocuri_api as sa
    with _db.get_conn(SCH) as conn:
        ids = sa.descarca_luna(conn, SCH, 2099, 10)["inregistrari"]
    assert ids, "descărcarea trebuie să aibă note (K = 0,4, vânzări 500)"
    return ids


MESAJ_LUNA_IN_CURS = ("Descărcarea gestiunii lunii 10/2099 se contează după ce luna se încheie: luna 10/2099 nu s-a încheiat "
                      "(azi e 15.10.2099) — se închide după ultima ei zi.")

MOTIV_DESC = ("Nota a fost scrisă pe 20.10.2099, înainte ca luna 10/2099 să se încheie: cifrele ei pot să nu cuprindă tot ce s-a întâmplat "
              "în lună. Verific-o față de intrările și vânzările de mărfuri ale lunii întregi, din care se calculează descărcarea "
              "gestiunii; o diferență se corectează printr-o notă de corecție — nota validată nu se modifică.")


def test_def_c187_descarcarea_lunii_in_curs_nu_se_scrie(firma):
    """Pașii: Stocuri, luna în curs (10/2099, azi 15.10.2099) -> „Descarcă gestiunea lunii”: refuz numit, nicio notă; după ce luna s-a
    încheiat (azi 02.11.2099), aceeași descărcare scrie notele.
    TEMEI: OMFP 1802/2014 pct.286 alin.(4) — K din rulajele cumulate „până la finele perioadei de referință”.
    MUTAȚIE: linia `_uc_comun._cere_luna_incheiata(an, luna, "Descărcarea gestiunii lunii")` scoasă din `uc_tenants.stocuri_descarcare`
    -> notele se scriu pe luna în curs -> pică."""
    from core import erori, uc_tenants
    with pytest.raises(erori.CerereGresita) as ex:
        uc_tenants.stocuri_descarcare(1, 2099, 10, CTX)
    assert ex.value.detaliu == MESAJ_LUNA_IN_CURS, ex.value.detaliu
    assert _note_descarcare() == []   # nimic scris
    firma["d"] = datetime.date(2099, 11, 2)   # luna 10/2099 s-a încheiat
    r = uc_tenants.stocuri_descarcare(1, 2099, 10, CTX)
    assert r["k"] == "0.400000", r
    assert [i for i, _s in _note_descarcare()] == sorted(r["inregistrari"]), (r, _note_descarcare())


def test_c187_luna_inexistenta_se_refuza_numit(firma):
    """Luna 13 nu e „luna în curs”: se refuză ca lună inexistentă (ca la amortizare, `_cere_perioada`), nu cu motivul lunii neîncheiate."""
    from core import erori, uc_tenants
    with pytest.raises(erori.DateInvalide) as ex:
        uc_tenants.stocuri_descarcare(1, 2099, 13, CTX)
    assert ex.value.detaliu == "luna invalidă: 13 (se așteaptă 1-12)", ex.value.detaliu


def test_c187_descarcarea_scrisa_inainte_de_incheierea_lunii_e_semnalata(firma):
    """Datele existente: descărcarea scrisă pe 20.10.2099 pentru luna 10/2099 (cu cheia actului) și una de dinainte de cheie (05.10.2026:
    numai descrierea „Descarcare gestiune LL/AAAA”) se semnalează pe rândurile Registrului jurnal, cu documentul față de care se verifică;
    o altă notă de stoc (NIR) scrisă în luna ei nu; descărcarea scrisă după încheierea lunii nu.
    MUTAȚIE: ramura descărcării (`desc`) scoasă din `inchidere_luna.note_contate_inainte` -> notele nu mai sunt semnalate -> pică."""
    ids = _descarca_direct()
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("INSERT INTO %s.inregistrari (data, descriere, sursa, status, document_ref) VALUES "
                    "('2099-09-30', 'Descarcare gestiune 09/2099', 'stocuri', 'validata', 'Situație de descărcare nr. 1') RETURNING id"
                    % SCH)
        veche = cur.fetchone()[0]
        cur.execute("INSERT INTO %s.inregistrari (data, descriere, sursa, status, document_ref) VALUES "
                    "('2099-10-07', 'NIR 7 - Furnizor', 'stocuri', 'validata', 'NIR nr. 7') RETURNING id" % SCH)
        nir = cur.fetchone()[0]
        c.commit()
    _scrisa_la(ids + [nir], "2099-10-20 10:00:00+03")
    _scrisa_la([veche], "2099-09-20 10:00:00+03")
    sem = _semnalate()
    assert sorted(sem) == sorted(ids + [veche]), sem
    for i in ids:
        assert sem[i]["motiv"] == MOTIV_DESC, sem[i]["motiv"]
        assert (sem[i]["descarcare"], sem[i]["reevaluare"], sem[i]["status"], sem[i]["luna_an"]) == (True, False, "ciorna", "10/2099")
    assert (sem[veche]["descarcare"], sem[veche]["status"], sem[veche]["luna_an"]) == (True, "validata", "09/2099"), sem[veche]
    assert sorted(_semnalate(ids)) == sorted(ids)   # aceeași regulă pe rândurile Registrului jurnal (`ids`)
    _scrisa_la(ids + [veche], "2099-11-02 09:00:00+02")   # scrise după încheierea lunii: nu se semnalează
    assert _semnalate() == {}


def test_c187_migrarea_scoate_ciorna_descarcarii_si_numeste_nota_validata(firma):
    """Datele existente (`core/migrare_note_luna_neincheiata.py`): ciornele descărcării scrise pe 20.10.2099 pentru luna 10/2099 se scot
    (cu urma în `public.audit_log`), nota VALIDATĂ a descărcării de dinainte se numește și rămâne neatinsă; a doua rulare nu mai găsește
    nimic (idempotentă). Totul în tranzacție anulată (audit_log e partajat).
    MUTAȚIE: aceeași ca la semnal (ramura `desc` scoasă) -> ciornele rămân -> pică."""
    from core import migrare_note_luna_neincheiata as m
    ids = _descarca_direct()
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("INSERT INTO %s.inregistrari (data, numar, descriere, sursa, status, document_ref) VALUES "
                    "('2099-09-30', 'DESC-GV-2099-09', 'Descarcare gestiune 09/2099', 'stocuri', 'validata', 'Situație de descărcare nr. 1') "
                    "RETURNING id" % SCH)
        validata = cur.fetchone()[0]
        cur.execute("INSERT INTO %s.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, '607', '371', 10)"
                    % SCH, (validata,))
        c.commit()
    _scrisa_la(ids, "2099-10-20 10:00:00+03")
    _scrisa_la([validata], "2099-09-25 10:00:00+03")
    with _db.get_conn() as conn:
        r = m.aplica(conn, SCH)
        assert sorted(r["scoase"]) == sorted(ids), r
        assert r["validate"] == [(validata, "09/2099")] and r["ramase"] == [], r
        with conn.cursor() as cur:
            cur.execute("SELECT id, status FROM %s.inregistrari WHERE sursa = 'stocuri' ORDER BY id" % SCH)
            assert cur.fetchall() == [(validata, "validata")]
            cur.execute("SELECT count(*) FROM public.audit_log WHERE actiune = 'stergere_ciorna_luna_neincheiata' AND entitate_id = ANY(%s) "
                        "AND detalii->>'schema' = %s", (ids, SCH))
            assert cur.fetchone()[0] == len(ids)
        assert m.verifica(conn, SCH) is True
        assert m.aplica(conn, SCH)["scoase"] == []   # idempotentă
        conn.rollback()
