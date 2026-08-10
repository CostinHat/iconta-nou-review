# -*- coding: utf-8 -*-
"""GARD D394 - pull() nu mai da NameError la achizitie cu taxare inversa fara linii (10.08.2026).

DEFECT (cod vechi): in core.d394.pull(), pentru o factura PRIMITA cu taxare inversa si FARA
linii (import / e-Factura fara detaliu, TVA=0 pe document), codul deducea cota bunului din
`cota_standard(an, luna)` - dar `an` si `luna` NU erau definite in pull() (existau doar in
calcul_d394). Rezultat: NameError la generarea D394 pentru orice firma cu o astfel de achizitie
(exact calea pe care comentariul o marcheaza ca importanta: "orice achizitie cu taxare inversa
cadea din declaratie").

FIX (core.d394.pull): `an, luna = perioada.an, perioada.luna` la intrarea in functie.

MUTATIE: pe cod vechi acest test ridica NameError (eroare, nu pass). Pe cod nou pull() intoarce
factura cu cota == cota_standard a perioadei, fara exceptie.

Fixtura: schema efemera din tenant_template.sql (rollback la final), acelasi tipar ca
core/test_d394_reconciliere.py.
"""
import pytest

from core.common import Perioada
from core import d394
from core import db as _db, tenant_provisioning as _tp

_SCHEMA = "test_d394_pull_ti"
_PER = Perioada(2026, luna=6)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn_ti():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,"
                            "iban,telefon,platitor_tva,tip_decont) VALUES (1,'PROBA SRL','14399840',"
                            "'Str 1','Buc','B','6202','BCR','RO49RNCB0000000000000001','0700000000',"
                            "true,'L')")
                # Achizitie PRIMITA cu taxare inversa, TVA=0, FARA linii (calea an/luna).
                cur.execute("INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,"
                            "tert_platitor_tva,total,tva,taxare_inversa) VALUES "
                            "('FTI','2026-06-11','primita','RO14399840','FURNIZOR TI',true,1000,0,true)")
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_pull_taxare_inversa_fara_linii_nu_da_nameerror(conn_ti):
    """pull() pe o achizitie taxare inversa fara linii: nu ridica NameError si deduce cota
    standard a perioadei. Cod vechi: NameError (an/luna nedefinite)."""
    _prof, date = d394.pull(conn_ti, _SCHEMA, _PER)
    ti = [f for f in date["facturi"] if f.get("taxare_inversa")]
    assert ti, "asteptam factura taxare inversa in rezultatul pull()"
    assert ti[0]["cota"] == d394.cota_standard(_PER.an, _PER.luna), \
        "cota deducerii trebuie sa fie standardul perioadei; gasit %r" % (ti[0]["cota"],)
