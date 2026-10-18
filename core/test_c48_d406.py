# -*- coding: utf-8 -*-
"""[C48 în D406, comanda Costin 8.1 pct.4, 18.10.2026, verbatim în DECIZII „Comanda 8.1”] „Probe pe care browserul nu le poate face: […] C48
în D406”. C48 (lotul 7): planul de conturi al firmelor are 4092 / 4093 / 4094 (avansurile acordate pentru servicii, imobilizări corporale /
necorporale, `avansuri.CONT_AVANS`). Proba: firma nouă (din `tenant_template.sql`), o notă validată pe 4092 (avans de servicii plătit din
bancă) -> D406 pe lună: cele trei conturi în MasterFiles/GeneralLedgerAccounts, tranzacția pe 4092 în GeneralLedgerEntries, iar
validatorul oficial (DUK, `core/duk.py`) dă XML-ul valid. Temei structură: XSD SAF-T (`/opt/duk/saft/saft.xsd`); conturile admise =
planul normei (`anaf_surse/d406_nomenclatoare_anaf.properties`, `plan_conturi_bal_soc_com`: 409, 4091, 4092, 4093, 4094).
MUTAȚIE: 4092 scos din șablon (`plan_conturi`) -> contul lipsește din MasterFiles -> pică."""
import xml.etree.ElementTree as ET

import pytest

SCHEMA = "ztest_c48_d406"


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _sub(rad, nod, sectiune):
    """`nod` stă sub secțiunea `sectiune` (MasterFiles / GeneralLedgerEntries) a documentului SAF-T."""
    for s in rad.iter():
        if _local(s.tag) == sectiune and any(x is nod for x in s.iter()):
            return True
    return False


def _db_ok():
    from core import db
    try:
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c48_conturile_de_avans_ajung_in_d406_si_xml_e_valid():
    from core import db, duk, tenant_provisioning as _tp, d406
    with db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), SCHEMA))
                cur.execute("SET search_path TO %s, public" % SCHEMA)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, banca, iban, "
                    "declarant_nume, declarant_prenume, declarant_functie, platitor_tva, tip_decont, regim_fiscal) "
                    "VALUES (1, 'TEST SRL', '14399840', 'Str. Testul 1', 'Bucuresti', 'B', '6920', 'BCR', "
                    "'RO49BCRA0000000000000000', 'POPESCU', 'GHEORGHE', 'EXPERT CONTABIL', true, 'L', 'real')")
                cur.execute("INSERT INTO inregistrari (data, descriere, document_ref, status) VALUES ('2026-06-10', "
                            "'Avans servicii consultanta', 'OP 12', 'validata') RETURNING id")
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '4092', '5121', 1500)",
                            (cur.fetchone()[0],))
            xml, res = d406.genereaza(conn, SCHEMA, 2026, 6)
        finally:
            conn.rollback()
    rad = ET.fromstring(xml.encode("utf-8"))
    conturi = {e.text for e in rad.iter() if _local(e.tag) == "AccountID" and _sub(rad, e, "MasterFiles")}
    assert {"4092", "4093", "4094"} <= conturi, "conturile C48 lipsesc din MasterFiles: %s" % sorted(c for c in conturi if c.startswith("409"))
    intrari = {e.text for e in rad.iter() if _local(e.tag) == "AccountID" and _sub(rad, e, "GeneralLedgerEntries")}
    assert intrari >= {"4092"}, "tranzacția pe 4092 lipsește din GeneralLedgerEntries: %s" % sorted(intrari)
    v = duk.valideaza(xml, "d406", an=2026, luna=6, timeout=240)
    if v.get("stare") == "gri":
        pytest.skip("validator SAF-T indisponibil: %s" % v.get("temei"))
    print("DUK D406 06/2026:", v.get("stare"), "| conturi 409x în MasterFiles:", sorted(c for c in conturi if c.startswith("409")))
    assert v.get("stare") == "valid", "DUK: %s" % v
