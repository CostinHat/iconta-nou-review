# -*- coding: utf-8 -*-
"""[lotul 11, K — clasa „căutare pe cod fiscal în forma brută”] Decizia Costin 10.3 pct.4, verbatim în DECIZII „Comanda 10.3”: „CUI-ul se
păstrează fără «RO» și fără spații; «RO» apare doar la afișare, după starea de plătitor de TVA.” Triggerul `trg_cui_fara_ro` scrie forma
păstrată („14399840”), dar valorile care vin din afară (XML-ul e-Factura, cererea ecranului) aduc „RO14399840”, iar documentele de dinainte
au rămas cu „RO” (decizia P §6: emisele nu se rescriu). O căutare `tert_cui = %s` cu valoarea brută nu-și mai găsea rândul:

  * `repo_main.select_facturi_3` (importul e-Factura): a doua trimitere a aceleiași facturi nu se găsea -> INSERT -> cheia unică a
    numărului (`facturi_numar_emisa_uniq`) — prins de `core/test_contare_automata.py::test_importul_efactura_duplicat_...` (UniqueViolation);
  * `repo_efactura.contul_invatat_al_emitentului`: contul învățat al furnizorului se pierdea între rândurile vechi și noi;
  * `rapoarte_comerciale_api.lista_parteneri` / `fisa_partener`: același partener ieșea de două ori în selector, iar fișa cerută cu „RO”
    nu găsea facturile noi.

Acum toate compară FORMA PĂSTRATĂ pe ambele părți (`cui_forma.SQL` pe coloană, `cui_forma.stocare` pe parametru). Temei: N/A — forma de
stocare e o decizie de produs (10.3 pct.4); prefixul RO e al codului de TVA (CF art.318 alin.(1)), nu al CUI-ului.
GARDA: niciun SQL din `core/` / `main.py` nu mai compară o coloană de cod fiscal a documentelor cu un parametru brut.
MUTAȚIE: `select_facturi_3` înapoi pe `COALESCE(tert_cui,'')=%s` cu `f["tert_cui"]` -> pică proba și garda."""
import glob
import io
import os
import re

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = "ztest_lot11_k_cui_cautare"


def _db_ok():
    from core import db
    try:
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cautarile_pe_cod_fiscal_gasesc_randul_in_orice_forma():
    from core import db, rapoarte_comerciale_api as rc, repo_efactura, repo_main, tenant_provisioning as _tp
    with db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read(), SCHEMA))
                # o factură VECHE, scrisă înainte de trigger (cu „RO”), și una nouă (forma păstrată, scrisă de trigger)
                cur.execute("ALTER TABLE %s.facturi DISABLE TRIGGER USER" % SCHEMA)
                cur.execute("INSERT INTO %s.facturi (numar, data_emitere, directie, tip, tert_nume, tert_cui, total) VALUES "
                            "('V1', '2099-03-01', 'emisa', 'factura', 'DANTE INTERNATIONAL SA', 'RO14399840', 100)" % SCHEMA)
                cur.execute("ALTER TABLE %s.facturi ENABLE TRIGGER USER" % SCHEMA)
                cur.execute("INSERT INTO %s.facturi (numar, data_emitere, directie, tip, tert_nume, tert_cui, total) VALUES "
                            "('N1', '2099-03-02', 'emisa', 'factura', 'DANTE INTERNATIONAL SA', 'RO14399840', 200) RETURNING id, tert_cui"
                            % SCHEMA)
                nid, pastrat = cur.fetchone()
                assert pastrat == "14399840", pastrat   # triggerul `trg_cui_fara_ro`: forma păstrată
                cur.execute("INSERT INTO %s.efactura_primite (id_mesaj_anaf, xml_sha256, cif_emitent, cif_beneficiar, status, "
                            "cont_cheltuiala) VALUES ('K-2099-1', repeat('0', 64), '14399840', '2864518', 'validata', '628')" % SCHEMA)
                # importul: aceeași factură, adusă de XML cu „RO”, se găsește (nu se dublează)
                gasit = repo_main.select_facturi_3(cur, '"%s"' % SCHEMA, {"numar": "N1", "tert_cui": "RO14399840", "data_emitere": "2099-03-02",
                                                                       "directie": "emisa"})
                assert gasit is not None and gasit[0] == nid, gasit
                # contul învățat al furnizorului, cerut cu „RO”
                assert repo_efactura.contul_invatat_al_emitentului(cur, '"%s"' % SCHEMA, "RO 14399840") == ("628",)
            # selectorul fișei: UN partener, nu două forme ale aceluiași CUI
            lista = rc.lista_parteneri(conn, '"%s"' % SCHEMA)
            assert [p["cui"] for p in lista] == ["14399840"], lista
            # fișa cerută cu „RO” cuprinde ambele facturi (cea veche cu „RO” și cea nouă fără)
            fisa = rc.fisa_partener(conn, '"%s"' % SCHEMA, "RO14399840", "2099-01-01", "2099-12-31")
            assert sorted(f["numar"] for f in fisa["facturi"]) == ["N1", "V1"], fisa
        finally:
            conn.rollback()


#: coloanele de cod fiscal ale DOCUMENTELOR (rândurile vechi pot păstra „RO”; decizia 10.3 pct.4 + P §6: emisele nu se rescriu)
_COMPARATIE_BRUTA = re.compile(r"\b(?:tert_cui|cif_emitent|cif_beneficiar)(?:\s*,\s*'')?\)?\s*=\s*%s")


def test_garda_niciun_sql_nu_compara_codul_fiscal_brut():
    """GARDĂ: o comparație `tert_cui = %s` (sau `COALESCE(tert_cui,'') = %s`, `cif_emitent = %s`) în SQL-ul aplicației -> pică, cu locul.
    Forma cerută: `cui_forma.SQL.format(c=…) = %s` cu `cui_forma.stocare(valoare)`. Liniile de `print` (jurnal) nu sunt SQL."""
    rele = []
    for cale in sorted(glob.glob(os.path.join(_RAD, "core", "*.py"))) + [os.path.join(_RAD, "main.py")]:
        if os.path.basename(cale).startswith(("test_", "scan_")):
            continue
        for i, rand in enumerate(io.open(cale, encoding="utf-8"), 1):
            if _COMPARATIE_BRUTA.search(rand) and "print(" not in rand:
                rele.append("%s:%d  %s" % (os.path.relpath(cale, _RAD), i, rand.strip()[:100]))
    assert rele == [], "comparații pe cod fiscal în forma brută (folosește cui_forma.SQL + cui_forma.stocare):\n  " + "\n  ".join(rele)
