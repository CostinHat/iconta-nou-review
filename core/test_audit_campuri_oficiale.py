# -*- coding: utf-8 -*-
"""GARD AUDIT SEMANTIC — numele campurilor emise = campuri OFICIALE (01.08.2026, Conditia 2 Costin).

D101 a dovedit: "trece DUK" != "campurile corecte". calcul_d101 folosea o numerotare P INVENTATA
(p11=impozit) mapata pe nume oficiale cu MEANING gresit. DUK valideaza STRUCTURA, nu semantica ->
istoricul "toate valide DUK" era suspect pana la verificarea numelor contra structurii oficiale.

AUDIT 01.08 pe cele 8 valide (d100,d112,d205,d300,d301,d390,d394,d406): TOATE emit doar campuri
oficiale (regasite in anaf_surse/*_struct_anaf.txt), inclusiv randurile numerotate (d300 R, d112
B/E, d394). Trei atribute lipseau din struct.txt dar sunt CONFIRMATE in constant pool-ul validatorului
(versiune mai noua): d301 temei, d394 tvaDedAI11/tvaDedAI21. d101 = SINGURA cu numerotare proprie.

Gardul face reaparitia clasei IMPOSIBILA: daca un generator emite un atribut care NU e nici oficial
(in struct.txt) nici boilerplate XML nici pe allowlist-ul confirmat-in-validator, testul PICA.
"""
import re
import pytest

from core.common import Perioada
from core import db as _db, tenant_provisioning as _tp
from core import d100, d112, d205, d300, d301, d390, d394

_SCHEMA = "ztest_audit_campuri"
_BOILERPLATE = {"encoding", "version", "xmlns", "xsi", "schemaLocation"}
# Atribute reale ABSENTE din struct.txt (versiune veche) dar CONFIRMATE in constant pool-ul
# validatorului oficial la 01.08.2026 (strings pe D301Validator/D394Validator.jar):
_ALLOWLIST = {
    "d301": {"temei"},                          # D301Validator: _temei (regula d_rec)
    "d394": {"tvaDedAI11", "tvaDedAI21"},        # D394Validator v5: tvaDedAI* (TVA dedus achizitii intracom.)
}


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


_GEN = {
    "d100": lambda c: d100.genereaza(c, _SCHEMA, Perioada(2026, trim=2), {"cota": "16"}),
    "d112": lambda c: d112.genereaza(c, _SCHEMA, 2026, 6),
    "d205": lambda c: d205.genereaza(c, _SCHEMA, Perioada(2026)),
    "d300": lambda c: d300.genereaza(c, _SCHEMA, Perioada(2026, luna=6)),
    "d301": lambda c: d301.genereaza(c, _SCHEMA, Perioada(2026, luna=6)),
    "d390": lambda c: d390.genereaza(c, _SCHEMA, 2026, 6, None),
    "d394": lambda c: d394.genereaza(c, _SCHEMA, Perioada(2026, luna=6)),
}


@pytest.fixture
def conn_audit():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute(
                    "INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,email,telefon,"
                    "regim_fiscal,platitor_tva,tip_decont,baza_contabila,declarant_nume,declarant_prenume,declarant_functie) VALUES "
                    "(1,'PROBA SRL','14399840','Str. Test 1','Bucuresti','B','6202','BCR','RO49RNCB0000000000000001',"
                    "'a@b.ro','0700000000','profit',true,'L','A','Pop','Ion','administrator') ON CONFLICT (id) DO UPDATE SET nume=EXCLUDED.nume")
                cur.execute("INSERT INTO salariati (cnp,nume,prenume,data_angajare,salariu_brut,ore_zi,judet_casa) VALUES ('1900101410011','P','I','2024-01-01',5000,8,'B')")
                cur.execute("INSERT INTO asociati (nume,cnp,cota) VALUES ('A','1900101410011',100)")
                cur.execute("INSERT INTO inregistrari (data,status,sursa,descriere) VALUES ('2026-05-15','validata','t','V') RETURNING id"); i1 = cur.fetchone()[0]
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id,cont_debit,cont_credit,suma) VALUES (%s,'4111','704',100000)", (i1,))
                cur.execute("INSERT INTO inregistrari (data,status,sursa,descriere) VALUES ('2026-03-10','validata','t','D') RETURNING id"); i2 = cur.fetchone()[0]
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id,cont_debit,cont_credit,suma) VALUES (%s,'457','5121',50000)", (i2,))
                cur.execute("INSERT INTO facturi (numar,data_emitere,total,tva,directie,tert_nume,tert_cui) VALUES ('F1','2026-06-15',10000,0,'emisa','EU','DE811128135')")
                cur.execute("INSERT INTO facturi (numar,data_emitere,total,tva,directie,tert_nume,tert_cui) VALUES ('F2','2026-06-20',6050,1050,'emisa','RO CLI','RO14399840')")
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
@pytest.mark.parametrize("tip", list(_GEN.keys()))
def test_campurile_emise_sunt_oficiale(conn_audit, tip):
    """Fiecare atribut emis de build_xml trebuie sa fie campanie oficiala (struct.txt) sau boilerplate
    XML sau allowlist confirmat-in-validator. Un atribut inventat (clasa d101) PICA aici."""
    out = _GEN[tip](conn_audit)
    xml = out[0] if isinstance(out, tuple) else out
    doc = open("anaf_surse/%s_struct_anaf.txt" % tip, encoding="utf-8", errors="replace").read().lower()
    attrs = sorted(set(re.findall(r'([A-Za-z_][A-Za-z0-9_]*)="', xml)))
    allow = _ALLOWLIST.get(tip, set())
    inventate = [a for a in attrs if a not in _BOILERPLATE and a not in allow and a.lower() not in doc]
    assert not inventate, (
        "%s emite atribute NEoficiale (posibil numerotare proprie, clasa d101): %s "
        "- verifica in anaf_surse/%s_struct_anaf.txt sau in constant pool-ul validatorului" % (tip, inventate, tip))
