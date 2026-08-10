# -*- coding: utf-8 -*-
"""core/test_d205_imp_manual.py — GARD d1 (CATALOG_INVALIDITATE): consistenta interna imp1 pt.
beneficiari MANUALI.

CLASA OARBA inchisa: un beneficiar MANUAL (manual["beneficiari"], introdus de contabil) cu
imp1 != round(cota_dividend x baza1) trecea generatorul SI DUK. Cauza:
  - d205_reconciliere.reconciliaza returna TACIT divergente=[] pe calea manuala (nicio sursa in
    457 de recalculat), deci poarta A DOUA CALE nu vedea nimic;
  - DUK verifica DOAR Timp=Σimp1 (totalul sectiunii), NU cota per beneficiar (regula DUK-invizibila).
Rezultat: declaratie MATERIAL gresita acceptata end-to-end (imp1=9999 pe baza 10000 in loc de 1600).

FIX (core/d205_reconciliere.py): _consistenta_interna() confrunta imp1 cu round(cota_dividend x
baza1) per beneficiar (cota din common.cota('impozit_dividend'), period-aware, ACEEASI sursa ca
d205; toleranta rotunjire 1 leu), fara ledger - e o regula fiscala INTERNA, nu un recalcul din
sursa. Divergenta -> ReconciliereD205 (Valueare) care numeste beneficiarul si AMBELE valori.

NON-TAUTOLOGIE: proba de mutatie principala (imp1 gresit -> RIDICA) NU atinge DB - construieste
res prin calcul_d205 si cheama poarta pe calea manuala (care nu foloseste conn). Probele
DUK-valid (manual corect + auto neschimbat) sunt gardate pe DB/DUK.
"""
import pytest

from core.common import Perioada
from core import d205 as _d205
from core import db as _db, tenant_provisioning as _tp, duk as _duk
from core.d205_reconciliere import (reconciliaza, verifica_reconciliere,
                                    ReconciliereD205, _consistenta_interna)

_CNP = "1900101410011"   # CNP rezident checksum-valid (folosit si in smoke DUK)


def _manual(imp, baza=10000):
    return {"beneficiari": [{"categ": "1.a", "nume": "POPESCU ION", "cif": _CNP,
                             "baza": baza, "imp": imp, "divid_d": baza, "divid_p": baza,
                             "tip_plata": "2"}]}


# ---------- PROBA DE MUTATIE (fara DB): imp1 gresit -> RIDICA (inainte: TACIT) ----------

def test_manual_imp_gresit_ridica_fara_db():
    """MUTATIE d1: beneficiar manual baza 10000, imp 9999 (in loc de 1600 = 16% x 10000).
    Inainte: reconciliaza returna divergente=[] tacit -> generator + DUK acceptau. Acum RIDICA
    ReconciliereD205 care numeste beneficiarul si AMBELE valori. Nu atinge DB (cale manuala)."""
    man = _manual(imp=9999)
    res = _d205.calcul_d205({}, 2026, man["beneficiari"])
    # poarta pe calea manuala nu foloseste conn -> None e suficient (proba non-DB).
    with pytest.raises(ReconciliereD205) as ei:
        verifica_reconciliere(None, "s", Perioada(2026), res, man)
    msg = str(ei.value)
    assert _CNP in msg, msg
    assert "imp1=9999 dar rate×baza1=1600" in msg, msg


def test_manual_imp_corect_nu_ridica_fara_db():
    """CONTROL: beneficiar manual imp 1600 = 16% x 10000 -> poarta NU ridica, zero divergente."""
    man = _manual(imp=1600)
    res = _d205.calcul_d205({}, 2026, man["beneficiari"])
    rap = reconciliaza(None, "s", Perioada(2026), res, man)
    assert rap["acoperit"] is False, rap          # §8: baza NU e recalculata din sursa
    assert rap["divergente"] == [], rap["divergente"]
    verifica_reconciliere(None, "s", Perioada(2026), res, man)   # nu ridica


def test_toleranta_rotunjire_1_leu_fara_db():
    """imp1 la +/-1 leu de round(cota x baza) = rotunjire acceptata; peste = eroare."""
    res_ok = _d205.calcul_d205({}, 2026, _manual(imp=1601)["beneficiari"])
    assert reconciliaza(None, "s", Perioada(2026), res_ok, _manual(imp=1601))["divergente"] == []
    res_rau = _d205.calcul_d205({}, 2026, _manual(imp=1602)["beneficiari"])
    assert reconciliaza(None, "s", Perioada(2026), res_rau, _manual(imp=1602))["divergente"], "2 lei = eroare"


# ---------- PROBE DUK (gardate pe DB/DUK) ----------

_SCHEMA = "ztest_d205_imp_manual"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


_DBOK = _db_ok()


@pytest.fixture
def conn_t():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,"
                            "declarant_nume,declarant_prenume,declarant_functie) VALUES "
                            "(1,'TEST SRL','14399840','Str 1','Buc','B','POP','ION','ADMINISTRATOR')")
                # asociat + dividend 457 pentru calea AUTO (baza 10000 -> 60/40)
                cur.execute("INSERT INTO asociati (nume,cnp,cota) VALUES "
                            "('POPESCU',%s,60),('IONESCU','2900101410011',40)", (_CNP,))
                cur.execute("INSERT INTO inregistrari (data,descriere,status) "
                            "VALUES ('2026-04-01','div','validata') RETURNING id")
                nid = cur.fetchone()[0]
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id,cont_debit,cont_credit,suma) "
                            "VALUES (%s,'457','5121',10000)", (nid,))
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _DBOK or not _duk.poate_valida("d205"), reason="DB/DUK d205")
def test_manual_corect_genereaza_si_duk_valid(conn_t):
    """Beneficiar manual VALID (imp=1600=16% x 10000): genereaza trece poarta si DUK il accepta."""
    xml, res = _d205.genereaza(conn_t, _SCHEMA, Perioada(2026), manual=_manual(imp=1600))
    assert int(res.beneficiari[0].imp1) == 1600
    r = _duk.valideaza(xml, "d205", an=2026, timeout=110)
    assert r["stare"] == "valid", (r.get("erori") or "")[:200]


@pytest.mark.skipif(not _DBOK, reason="DB indisponibil")
def test_manual_gresit_blocheaza_generarea_pe_db(conn_t):
    """End-to-end pe DB: manual imp gresit -> genereaza() RIDICA (nu mai emite XML tacit)."""
    with pytest.raises(ReconciliereD205):
        _d205.genereaza(conn_t, _SCHEMA, Perioada(2026), manual=_manual(imp=9999))


@pytest.mark.skipif(not _DBOK or not _duk.poate_valida("d205"), reason="DB/DUK d205")
def test_auto_neschimbat_si_duk_valid(conn_t):
    """Calea AUTO (fara manual) neschimbata: baza/imp derivate din 457+cota, DUK valid."""
    xml, res = _d205.genereaza(conn_t, _SCHEMA, Perioada(2026))
    porc = {b.cif: (int(b.baza1), int(b.imp1)) for b in res.beneficiari}
    assert porc.get(_CNP) == (6000, 960), porc
    assert porc.get("2900101410011") == (4000, 640), porc
    r = _duk.valideaza(xml, "d205", an=2026, timeout=110)
    assert r["stare"] == "valid", (r.get("erori") or "")[:200]
