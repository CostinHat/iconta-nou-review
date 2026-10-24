# -*- coding: utf-8 -*-
"""[lotul 12, deficiența 461, comanda Costin 12.1 pct.8: „461 lista de parteneri” cerută] Partenerii firmei: lista (clienți și furnizori, din
toate documentele) și fișa partenerului — datele, documentele lui, soldul din contabilitate.

Pe o schemă efemeră (din tenant_template.sql, în ROLLBACK), cu documente pe toate drumurile din care firma își cunoaște partenerii:
  * DANTE INTERNATIONAL SA (CUI 14399840, cifra de control verificată): fișă de client; factura emisă F1 (1.210 lei, nota 4111 = 707 / 4427
    validată); încasarea în numerar de 500 lei (5311 = 4111, validată, cu operațiunea de casă); o linie de extras bancar alocată facturii;
    soldul de preluare pe parteneri 4111 debitor 100 lei (balanța de deschidere 4111 debitor 100 lei, la 31.01.2026); o ciornă 4111 = 707
    de 50 lei (nu intră în sold, R36);
  * ALTEX ROMANIA SRL (CUI 2864518, cifra de control verificată): factura primită de 242 lei (601 / 4426 = 401, validată) și o notă manuală
    401 = 5121 de 42 lei, cu partenerul scris pe linie „RO2864518” (forma brută; aceeași cheie ca factura);
  * POPESCU ION (persoană fizică, fără cod): un borderou de achiziție — partenerul se ține după nume;
  * o notă manuală validată 4111 = 758 de 70 lei fără partener (de dinainte de 381): în balanță, în soldul niciunui partener — fișa o spune.

Soldul DANTE la zi = 100 (preluare) + 1.210 (factura) − 500 (casa) = 810 debitor pe 4111; ALTEX = 242 − 42 = 200 creditor pe 401. Aceeași
regulă ca balanța / bilanțul (`bilant_api.sold_la`): soldul de preluare + notele VALIDATE de după data lui.
Temei: OMFP 1802/2014 pct.594 (planul de conturi: grupa 40 „Furnizori și conturi asimilate”, grupa 41 „Clienți și conturi asimilate”) —
rolul partenerului după cont; OMFP 2634/2015 anexa 2 (balanța de verificare: soldurile inițiale, rulajele, soldurile finale) — soldul.
MUTAȚII (raportate): `_rol_cont` cu grupele inversate -> pică rolul și soldul; notele ciornă numărate în sold -> pică 810; potrivirea
partenerului pe CUI-ul brut (fără `cheie_partener`) -> nota manuală cu „RO2864518” iese partener separat."""
import io
import os

import pytest

from core import clienti_api as ca
from core import db as _db, tenant_provisioning as _tp

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCH = "efemer_lot12_prod_parteneri"
DANTE, ALTEX = "14399840", "2864518"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _nota(cur, data, status, linii, factura_id=None, numar=None, descriere="nota"):
    cur.execute("INSERT INTO inregistrari (data, numar, descriere, sursa, status, factura_id) VALUES (%s, %s, %s, 'manual', %s, %s) "
                "RETURNING id", (data, numar, descriere, status, factura_id))
    nid = cur.fetchone()[0]
    for d, c, s, *p in linii:
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma, partener_cui, partener_nume) "
                    "VALUES (%s, %s, %s, %s, %s, %s)", (nid, d, c, s, p[0] if p else None, p[1] if len(p) > 1 else None))
    return nid


@pytest.fixture
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), _SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCH)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva) VALUES (1, 'CAT SRL', '18547290', true)")
                cur.execute("INSERT INTO clienti (nume, cui, oras, judet) VALUES ('DANTE INTERNATIONAL SA', %s, 'București', 'B')", (DANTE,))
                cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) "
                            "VALUES ('4111', 'Clienți', 100, 0, '2026-01-31')")
                cur.execute("CREATE TABLE IF NOT EXISTS solduri_parteneri (id SERIAL PRIMARY KEY, cont TEXT NOT NULL, cui TEXT NOT NULL DEFAULT '', "
                            "denumire TEXT NOT NULL DEFAULT '', sold_debitor NUMERIC(15,2) NOT NULL DEFAULT 0, "
                            "sold_creditor NUMERIC(15,2) NOT NULL DEFAULT 0, data_referinta DATE)")
                cur.execute("INSERT INTO solduri_parteneri (cont, cui, denumire, sold_debitor, data_referinta) "
                            "VALUES ('4111', %s, 'DANTE INTERNATIONAL SA', 100, '2026-01-31')", (DANTE,))
                cur.execute("INSERT INTO facturi (numar, serie, data_emitere, directie, tip, tert_nume, tert_cui, total, tva) VALUES "
                            "('1', 'F', '2026-03-10', 'emisa', 'factura', 'DANTE INTERNATIONAL SA', %s, 1210, 210) RETURNING id", (DANTE,))
                f1 = cur.fetchone()[0]
                _nota(cur, "2026-03-10", "validata", [("4111", "707", 1000), ("4111", "4427", 210)], factura_id=f1)
                n_casa = _nota(cur, "2026-03-20", "validata", [("5311", "4111", 500)], descriere="încasare")
                cur.execute("INSERT INTO casa_operatiuni (data, tip, categorie, document, partener, cui, suma, inregistrare_id) VALUES "
                            "('2026-03-20', 'incasare', 'incasare_client', 'CH 1', 'DANTE INTERNATIONAL SA', %s, 500, %s)", (DANTE, n_casa))
                cur.execute("INSERT INTO extras_linii (data, descriere, suma, tip, status, alocari) VALUES "
                            "('2026-04-02', 'OP DANTE F 1', 300, 'incasare', 'nou', %s)", ('{"alocari": [{"factura_id": %d, "suma": "300"}]}' % f1,))
                _nota(cur, "2026-04-05", "ciorna", [("4111", "707", 50)], factura_id=f1)
                cur.execute("INSERT INTO facturi (numar, data_emitere, directie, tip, tert_nume, tert_cui, total, tva) VALUES "
                            "('A-77', '2026-05-02', 'primita', 'factura', 'ALTEX ROMANIA SRL', %s, 242, 42) RETURNING id", (ALTEX,))
                f2 = cur.fetchone()[0]
                _nota(cur, "2026-05-02", "validata", [("601", "401", 200), ("4426", "401", 42)], factura_id=f2)
                # rândul VECHI, scris înaintea triggerului `trg_cui_fara_ro` (forma brută „RO2864518” a rămas în bază)
                cur.execute("ALTER TABLE inregistrari_linii DISABLE TRIGGER USER")
                _nota(cur, "2026-05-15", "validata", [("401", "5121", 42, "RO2864518", "Altex Romania")], numar="77",
                      descriere="plată parțială")
                cur.execute("ALTER TABLE inregistrari_linii ENABLE TRIGGER USER")
                cur.execute("INSERT INTO facturi (numar, data_emitere, directie, tip, tert_nume, total) VALUES "
                            "('B1', '2026-06-01', 'primita', 'borderou', 'POPESCU ION', 300)")
                # o notă manuală validată pe 4111 fără partener (scrisă înainte ca partenerul să fie cerut, 381): în balanță, în niciun partener
                _nota(cur, "2026-06-10", "validata", [("4111", "758", 70)], descriere="fără partener")
            yield c
        finally:
            c.rollback()


def test_rolul_dupa_grupa_contului():
    """OMFP 1802/2014 pct.594: grupa 40 „Furnizori și conturi asimilate”, grupa 41 „Clienți și conturi asimilate”."""
    assert [ca._rol_cont(x) for x in ("401", "4091", "408", "4111", "419", "418.01", "5121", "461", None)] == [
        "furnizor", "furnizor", "furnizor", "client", "client", "client", None, None, None]


def test_461_lista_cuprinde_partenerii_din_toate_documentele(conn):
    lista = ca.parteneri_firmei(conn, _SCH)
    pe_nume = {p["nume"]: p for p in lista}
    assert sorted(pe_nume) == ["ALTEX ROMANIA SRL", "DANTE INTERNATIONAL SA", "POPESCU ION"], lista
    d, a, p = pe_nume["DANTE INTERNATIONAL SA"], pe_nume["ALTEX ROMANIA SRL"], pe_nume["POPESCU ION"]
    # DANTE: fișa de client, factura, casa, banca (nota facturii și a casei nu se numără a doua oară: documentul e factura / casa)
    assert (d["cheie"], d["cui"], d["rol"], d["fisa"], d["documente"]) == ("cui-14399840", DANTE, "client", True, 3), d
    # ALTEX: factura primită + nota manuală cu partenerul pe linie, scris „RO2864518” — același partener, nu doi
    assert (a["cui"], a["rol"], a["fisa"], a["documente"]) == (ALTEX, "furnizor", False, 2), a
    # persoana fizică fără cod: după nume
    assert (p["cheie"], p["cui"], p["rol"], p["documente"]) == ("nume-POPESCU_ION", None, "furnizor", 1), p


def test_461_fisa_partenerului_date_documente_si_soldul_din_contabilitate(conn):
    f = ca.fisa_partenerului(conn, _SCH, "cui-14399840")
    assert (f["nume"], f["cui"], f["rol"]) == ("DANTE INTERNATIONAL SA", DANTE, "client"), f
    assert [(x["fel"], x["oras"], x["judet"]) for x in f["fise"]] == [("clienti", "București", "B")], f["fise"]
    assert [(x["data"], x["fel"], x["document"], x["suma"]) for x in f["documente"]] == [
        ("2026-04-02", "Încasare prin bancă", "OP DANTE F 1", 300.0),
        ("2026-03-20", "Încasare în numerar", "CH 1", 500.0),
        ("2026-03-10", "Factură emisă", "F 1", 1210.0)], f["documente"]
    s = f["sold"]
    # soldul de preluare 100 + factura 1.210 − încasarea 500 = 810 debitor pe 4111; ciorna de 50 nu e evidență (R36), se numără separat
    assert s["conturi"] == [{"cont": "4111", "denumire": "Clienți", "debitor": 810.0, "creditor": 0.0}], s
    assert (s["preluare"], s["nedefalcat"], s["ciorne"], s["note_fara_partener"]) == ("2026-01-31", [], 1, 1), s
    g = ca.fisa_partenerului(conn, _SCH, "cui-2864518")
    assert [x["fel"] for x in g["documente"]] == ["Notă contabilă", "Factură primită"], g["documente"]
    assert g["sold"]["conturi"] == [{"cont": "401", "denumire": "Furnizori", "debitor": 0.0, "creditor": 200.0}], g["sold"]
    assert ca.fisa_partenerului(conn, _SCH, "cui-1") is None


def test_461_preluarea_nedefalcata_pe_parteneri_se_spune(conn):
    """Balanța de deschidere are sold pe 401, dar soldurile pe parteneri nu-l defalcă: partea furnizorului din soldul de preluare nu se
    cunoaște — fișa o spune (nu pornește tacit de la zero)."""
    with conn.cursor() as cur:
        cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) "
                    "VALUES ('401', 'Furnizori', 0, 900, '2026-01-31')")
    assert ca.fisa_partenerului(conn, _SCH, "cui-2864518")["sold"]["nedefalcat"] == ["401"]
