# -*- coding: utf-8 -*-
"""GARD — planul de conturi al firmelor e planul general din OMFP 1802/2014 pct.594, întreg și cu denumirile ordinului (deficiența 387,
comanda Costin 9.1, 19.10.2026: „Plan de conturi: lipsește 609 (Reduceri comerciale primite). Planul are 184 de conturi — compară-l integral
cu OMFP 1802/2014.”).

`core/plan_conturi_omfp.py` și blocul „[p97_plan_seed]” din `tenant_template.sql` sunt GENERATE de `scripts/plan_conturi_omfp.py` din
`anaf_surse/omfp_1802_2014_reglementari_consolidat.html`. Garda cere: (1) ambele = regenerarea; (2) o a doua sursă, independentă de
extragere — nomenclatorul de conturi al validatorului D406 (`anaf_surse/d406_nomenclatoare_anaf.properties`, `plan_conturi_bal_soc_com`) —
diferă de plan numai prin abaterile numite (conturile eliminate după el / introduse după el); (3) `core.plan_omfp` nu mai e o a doua copie;
(4) migrarea adaugă numai ce lipsește; (5) D406 nu numește pe fiecare declarație un cont din plan pe care validatorul nu-l are, dacă nu e folosit.
"""
import os
import re
import subprocess
import sys

import pytest

from core.plan_conturi_omfp import PLAN

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
import plan_conturi_omfp as gen  # noqa: E402


def test_modulul_si_sablonul_sunt_regenerarea_din_ordin():
    """MUTAȚIA: o denumire din `core/plan_conturi_omfp.py` sau un rând din `tenant_template.sql` editat de mână -> ROȘU."""
    r = subprocess.run([sys.executable, os.path.join(RAD, "scripts", "plan_conturi_omfp.py"), "--verifica"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_conturile_citate_din_ordin():
    # OMFP 1802/2014 pct.594, grupa 60: „609. Reduceri comerciale primite” (contul cerut de 387)
    assert PLAN["609"] == ("Reduceri comerciale primite", "")
    # pct.594, grupa 21: „2111. Terenuri”, „2112. Amenajări de terenuri” (importul mijloacelor fixe le folosește, lista veche nu le avea)
    assert PLAN["2111"][0] == "Terenuri" and PLAN["2112"][0] == "Amenajări de terenuri"
    # denumire modificată de OMFP 2531/2018 art.8 pct.1 (MO 623/18.07.2018): „441. Impozitul pe profit și alte impozite”
    assert PLAN["441"] == ("Impozitul pe profit și alte impozite", "")
    # funcțiunea tipărită se păstrează: „4111. Clienți (A)”, „401. Furnizori (P)”, „4423. TVA de plată (P)”, „121. Profit sau pierdere (A/P)”
    assert PLAN["4111"][1] == "A" and PLAN["401"][1] == "P" and PLAN["4423"][1] == "P" and PLAN["121"][1] == "A/P"
    # rândul pierdut la consolidare, din MO 963/2014: „6651. Diferențe nefavorabile de curs valutar legate de elementele monetare
    # exprimate în valută”; 665 rămâne „Cheltuieli din diferențe de curs valutar”
    assert PLAN["6651"][0] == "Diferențe nefavorabile de curs valutar legate de elementele monetare exprimate în valută"
    assert PLAN["665"][0] == "Cheltuieli din diferențe de curs valutar"
    # eliminate de OMFP 58/2021 art.13 pct.1 (MO 66/21.01.2021): 5126, 5127
    assert "5126" not in PLAN and "5127" not in PLAN
    # anti-vacuu: 577 de conturi de gradul I și II (257 + 320); nicio notă a portalului rămasă în denumiri
    assert len(PLAN) == 577
    assert not [s for s, (d, _f) in PLAN.items() if re.search(r"\(la \d|-{5}|\*\d|\^\d|Eliminat|MONITORUL", d)]


#: abaterile dintre planul ordinului și nomenclatorul validatorului D406 (Nomen_v3, identic cu `anaf_surse/d406_nomenclatoare_anaf.properties`):
#: validatorul are încă 5126 / 5127 (eliminate de OMFP 58/2021) și nu are 6121–6123 (OMFP 2649/2023) și 6351 (OMFP 981/2024)
NUMAI_LA_VALIDATOR = {"5126", "5127"}
NUMAI_IN_ORDIN = {"6121", "6122", "6123", "6351"}


def test_a_doua_sursa_nomenclatorul_validatorului_d406():
    from core import d406
    anaf = {c for c in d406.plan_oficial("A") if len(c) in (3, 4)}
    assert len(anaf) > 500, "anti-vacuu: %d conturi în nomenclatorul D406" % len(anaf)
    assert anaf - set(PLAN) == NUMAI_LA_VALIDATOR, sorted(anaf - set(PLAN))
    assert set(PLAN) - anaf == NUMAI_IN_ORDIN, sorted(set(PLAN) - anaf)


def _sablon():
    s = open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read()
    a = s.index("INSERT INTO TENANT_PLACEHOLDER.plan_conturi")
    z = s.index(";\n", a)
    return {m.group(1): m.group(2).replace("''", "'") for m in re.finditer(r"\('([^']+)', '((?:[^']|'')*)', 'Bifunctional'\)", s[a:z])}


def test_sablonul_are_tot_planul_cu_denumirile_ordinului():
    s = _sablon()
    assert {c: d for c, (d, _f) in PLAN.items()} == {c: d for c, d in s.items() if c in PLAN}
    assert set(s) - set(PLAN) == {c for c, _d in gen.ANALITICE_APLICATIE}, sorted(set(s) - set(PLAN))


def test_plan_omfp_citeste_planul_generat():
    """`core.plan_omfp.PLAN_OMFP` (denumirea de rezervă din balanță, conturile de venit din Date firmă) era o copie scrisă de mână."""
    from core import firma_profil_api, plan_omfp
    assert all(plan_omfp.PLAN_OMFP[c] == d for c, (d, _f) in PLAN.items())
    assert set(plan_omfp.PLAN_OMFP) - set(PLAN) == {"731", "732", "733", "734", "736", "738"}   # OMFP 3103/2017, grupa 73
    # 709 „Reduceri comerciale acordate” e în grupa 70, dar nu e un cont pe care se facturează o vânzare
    assert "709" in PLAN and "709" not in firma_profil_api.CONTURI_VENIT and "707" in firma_profil_api.CONTURI_VENIT


def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


def _schema_din_sablon(cur, schema):
    from core import tenant_provisioning as tp
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % schema)
    cur.execute(tp.parametrizeaza_template(open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), schema))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_migrarea_adauga_numai_ce_lipseste():
    from core import db, migrare_plan_conturi_omfp as mig
    schema = "ztest_plan_omfp_mig"
    with db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                _schema_din_sablon(cur, schema)
                cur.execute("DELETE FROM %s.plan_conturi WHERE simbol IN ('609', '6651', '2112')" % schema)
                cur.execute("UPDATE %s.plan_conturi SET denumire = 'Furnizori (din SAGA)', sold_creditor = 50 WHERE simbol = '401'" % schema)
                cur.execute("INSERT INTO %s.plan_conturi (simbol, denumire) VALUES ('401.05', 'Furnizor X')" % schema)
            assert mig.aplica(conn, schema) == 3
            with conn.cursor() as cur:
                cur.execute("SELECT simbol, denumire, sold_creditor FROM %s.plan_conturi WHERE simbol IN ('609', '401', '401.05') "
                            "ORDER BY simbol" % schema)
                assert cur.fetchall() == [("401", "Furnizori (din SAGA)", 50), ("401.05", "Furnizor X", 0), ("609", "Reduceri comerciale primite", 0)]
            assert mig.aplica(conn, schema) == 0    # idempotentă
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d406_numeste_contul_exclus_numai_cand_e_folosit():
    """6122 e în ordin (OMFP 2649/2023), nu și în nomenclatorul validatorului D406: se exclude din MasterFiles. Neatins (fără sold, fără
    linii), nu se mai numește pe fiecare D406; cu sold, se numește — „ca să nu dispară un cont cu sold fără ca contabilul să știe”."""
    from core import d406, db
    schema = "ztest_plan_omfp_d406"
    with db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                _schema_din_sablon(cur, schema)
                cur.execute("SET search_path TO %s, public" % schema)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, banca, iban, telefon, declarant_nume, declarant_prenume, "
                            "declarant_functie, platitor_tva, tip_decont, regim_fiscal) VALUES (1, 'TEST SRL', '14399840', 'Str. Testul 1', "
                            "'Bucuresti', 'B', '6920', 'BCR', 'RO49BCRA0000000000000000', '0212223344', 'POPESCU', 'GHEORGHE', 'EXPERT CONTABIL', true, 'L', 'real')")
            _xml, res = d406.genereaza(conn, schema, 2026, 6)
            assert not [x for x in res.avertismente if " din planul firmei " in x and " exclus din D406" in x], res.avertismente
            with conn.cursor() as cur:
                cur.execute("UPDATE plan_conturi SET sold_debitor = 100 WHERE simbol = '6122'")
            _xml, res = d406.genereaza(conn, schema, 2026, 6)
            # numai 6122 (cu sold, străin de norma declarată) e exclus și numit; 6121 nu
            # [390, lotul 12] textul în limba contabilului (fără „cont(uri) exclus(e)”)
            assert [x for x in res.avertismente if " din planul firmei " in x and " exclus din D406" in x] == [
                "Atenție (D406): 1 cont din planul firmei e exclus din D406 — nu e în planul de conturi al bazei contabile declarate (A), iar "
                "ANAF l-ar respinge: 6122. Verifică planul de conturi sau baza contabilă din Date firmă."], res.avertismente
        finally:
            conn.rollback()
