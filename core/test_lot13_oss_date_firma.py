# -*- coding: utf-8 -*-
"""[lotul 13, deficiența 595; decizia Costin 26.10.2026, verbatim: „6 da” la propunerea „595 — înregistrarea OSS se întreabă în Date firmă,
nu în formularul D398”] O singură sursă de adevăr pentru „firma e înregistrată în regimul special OSS”: `firma_profil.inregistrat_oss`
(Da / Nu / NULL = nedeclarat), scris din Date firmă și citit la generarea D398 (`declaratii_api._d398`, care are conexiunea).

Temei: CF art.315 alin.(3): „În cazul în care România este statul membru de înregistrare, persoana impozabilă respectivă trebuie să depună
în format electronic o declarație de începere a activității sale supuse regimului special la organul fiscal competent.” (textul e în
corpus: `anaf_surse/cod_fiscal_227_2015_consolidat.html`, căutat de `test_595_*` din `core/test_lot13_decl_logica.py`).

MUTAȚII (probate, vezi raportul): `d398.refuz_oss` întoarce mereu None -> `test_nedeclarat_*` și `test_nu_*` pică; `_d398` nu mai
cheamă `refuz_oss` -> aceleași pică; `inregistrat_oss` scos din `CAMPURI_OSS` -> `test_date_firma_salveaza_*` pică.
"""
import io
import re

import pytest

from core import d398, declaratii_api as DA, firma_profil_api as fp
from core.erori import RefuzGenerare
from core.test_d398_formular import _m

_SCHEMA = "ztest_l13_oss"


def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture
def conn():
    from core import db, tenant_provisioning as tp
    db.init_pool()
    with db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('Cabinet sintetic L13 OSS') RETURNING id")
                fid = cur.fetchone()[0]
                cur.execute("INSERT INTO public.tenants (schema_name, nume, accounting_firm_id, creat_la) VALUES (%s, 'FIRMA OSS SRL', %s, "
                            "'2020-01-01')", (_SCHEMA, fid))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
                # plătitoare de TVA (are cod: D398 nu e „neaplicabilă” prin art.315 alin.(4)); `inregistrat_oss` NU se completează
                cur.execute("INSERT INTO firma_profil (id, nume, cui, regim_fiscal, platitor_tva, tip_decont, operatiuni_ic) "
                            "VALUES (1, 'FIRMA OSS SRL', '14399840', 'profit', true, 'trimestrial', false)")
            yield c
        finally:
            c.rollback()


def _cerere():
    return {"an": 2026, "trim": 2, "manual": _m()}


def _raspunde(conn, valoare):
    r = fp.salveaza_date(conn, {"inregistrat_oss": valoare}, user_id=1)
    assert r["ok"] is True, r
    return r


def test_firma_noua_e_nedeclarata_si_coloana_e_in_template(conn):
    """Fără răspuns implicit (DS cap.17 v2.79 / 504): NULL, nu „Nu”."""
    with conn.cursor() as cur:
        cur.execute("SELECT inregistrat_oss FROM firma_profil WHERE id = 1")
        assert cur.fetchone()[0] is None
    assert fp.citeste_date(conn)["profil"]["inregistrat_oss"] is None


def test_nedeclarat_nu_genereaza_si_trimite_la_date_firma(conn):
    with pytest.raises(RefuzGenerare) as ei:
        DA.genereaza(conn, _SCHEMA, "d398", _cerere())
    d = ei.value.detaliu()
    assert (d["ecran"], d["camp_ecran"]) == ("date_firma", "df-inregistrat_oss"), d   # butonul „Date firmă” cu câmpul adus în vedere
    assert d["mesaj"] == d398.MOTIV_OSS_NEDECLARAT, d["mesaj"]


def test_nu_nu_genereaza_cu_motivul_legii(conn):
    _raspunde(conn, "0")
    with pytest.raises(RefuzGenerare) as ei:
        DA.genereaza(conn, _SCHEMA, "d398", _cerere())
    d = ei.value.detaliu()
    assert (d["ecran"], d["camp_ecran"]) == ("date_firma", "df-inregistrat_oss")
    assert d["mesaj"] == d398.MOTIV_OSS_NU, d["mesaj"]


def test_da_genereaza_xml_d398(conn):
    _raspunde(conn, "1")
    xml, res = DA.genereaza(conn, _SCHEMA, "d398", _cerere())
    assert re.search(r"<d398 [^>]*xmlns=\"mfp:anaf:dgti:d398:declaratie:v1\"", xml), xml[:300]
    assert res.grand_total_vat_due == "190.00"   # 1000 x 19% (formularul din `_m`)


def test_formularul_nu_trimite_si_nu_mai_intreaba_inregistrarea():
    """Câmpul din formular dispare (o singură sursă): nici cheia în cerere, nici controlul pe ecran."""
    js = io.open("static/js/ecrane/declaratii.js", encoding="utf-8").read()
    assert "inregistrat_oss" not in js and "d398-oss" not in js
    assert "inregistrat_oss" not in _m()
    assert DA.valideaza_cerere("d398", {"an": 2026, "trim": 2, "manual": _m()}) == []


def test_date_firma_salveaza_da_nu_si_golul_ramane_nedeclarat(conn):
    assert _raspunde(conn, "1")["profil"]["inregistrat_oss"] is True
    assert _raspunde(conn, "0")["profil"]["inregistrat_oss"] is False
    assert _raspunde(conn, "")["profil"]["inregistrat_oss"] is None   # „— alege —” = nedeclarat, nu „Nu” tacit
    r = fp.salveaza_date(conn, {"inregistrat_oss": "poate"}, user_id=1)
    assert r["ok"] is False and r["camp"] == "inregistrat_oss", r
    with conn.cursor() as cur:   # schimbarea rămâne în jurnalul Date firmă (cine, când, vechi -> nou)
        cur.execute("SELECT count(*) FROM firma_profil_jurnal WHERE camp = 'inregistrat_oss'")
        assert cur.fetchone()[0] >= 2


def test_nu_intra_in_profil_incomplet():
    """Decizie de produs: nu e obligatoriu oricărei firme (ar umple „Profil incomplet” la fiecare firmă care nu face OSS); îl cere doar D398."""
    assert "inregistrat_oss" not in fp.OBLIGATORII
    assert "inregistrat_oss" not in {x["camp"] for x in fp.lipsuri({"tip_firma": "srl"})}


def test_migrarea_e_idempotenta_si_nu_completeaza_nimic(conn):
    from core import migrare_inregistrat_oss as mig
    mig.aplica(conn, _SCHEMA)
    mig.aplica(conn, _SCHEMA)
    assert mig.verifica(conn, _SCHEMA)
    with conn.cursor() as cur:
        cur.execute("SELECT inregistrat_oss FROM firma_profil WHERE id = 1")
        assert cur.fetchone()[0] is None   # firmele existente rămân nedeclarate
