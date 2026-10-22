# -*- coding: utf-8 -*-
"""[lotul 11, C75 — decizia Costin, comanda 11.1 pct.2, verbatim] „C75: DA. Migrează borderourile vechi pe toate firmele, inclusiv pe
cabinetul pilot.” Migrarea `core/migrare_borderou_tip_vechi.py`: borderourile scrise înainte de lotul 9 cu tipul implicit („factura”)
trec pe `tip = 'borderou'`; coliziunile de număr se rezolvă determinist (cel mai vechi păstrează, următorii primesc BA-<următorul>);
o factură primită reală nu se atinge.

Datele de PORNIRE: borderoul vechi se scrie pe drumul de dinainte de lotul 9 (`creeaza_factura` cu tipul implicit + `nota_facturi_cu_factura`,
exact apelurile din `uc_tenants.achizitie_neinregistrat` la `27f4fab3`), iar `creat_la` se pune înainte de restartul lotului 9 — singurul
lucru pe care aplicația de azi nu-l mai poate produce (azi scrie `tip = 'borderou'`). Schemă efemeră, tranzacție anulată, date în 2099."""
import io
import os

import pytest

from core import db as _db, tenant_provisioning as _tp

SCH = "tenant_test_lot11_s_c75"
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, metoda_stoc) VALUES (1, 'C75 SRL', '14399840', 'cantitativ_valoric') "
                            "ON CONFLICT (id) DO UPDATE SET metoda_stoc = 'cantitativ_valoric'")
            yield c
        finally:
            c.rollback()


def _borderou_vechi(conn, numar, data, vanzator, valoare=100, creat_la="2026-10-19 13:39", descriere=None):
    """Borderoul, cum îl scria `achizitie_neinregistrat` înainte de lotul 9 (tipul implicit)."""
    from core import facturi_api as _fa, repo_contabilitate as rc
    descr = (descriere or "Achizitie de la neinregistrat") + " - " + vanzator
    fid = _fa.creeaza_factura(conn, numar=numar, data_emitere=data, directie="primita",
                              linii=[{"descriere": descr[:200], "cantitate": 1, "pret_unitar": str(valoare), "cota_tva": 0}],
                              tert_nume=vanzator, tert_cui="", status="importata", tert_platitor_tva=False, tert_pf=True)["factura_id"]
    with conn.cursor() as cur:
        iid = rc.nota_facturi_cu_factura(cur, SCH, data, fid, descr[:200])[0]
        rc.adauga_linie_furnizor(cur, SCH, iid, "371", valoare)
        cur.execute("UPDATE facturi SET creat_la = %s WHERE id = %s", (creat_la, fid))
    return fid


def _borderou_nou(conn, numar, data, vanzator, valoare=200):
    """Borderoul de azi (`tip = 'borderou'`), cu intrarea lui în stoc (documentul „Borderou de achiziție <nr> din …”)."""
    from core import facturi_api as _fa, jurnal_api as _j, stocuri_cv_api as cva
    fid = _fa.creeaza_factura(conn, numar=numar, data_emitere=data, directie="primita",
                              linii=[{"descriere": "grau - " + vanzator, "cantitate": 1, "pret_unitar": str(valoare), "cota_tva": 0}],
                              tert_nume=vanzator, tert_cui="", status="importata", tert_platitor_tva=False, tert_pf=True, tip="borderou")["factura_id"]
    r = cva.intrare(conn, SCH, {"denumire": "grau", "um": "kg", "data": data, "cantitate": 200, "pret_unitar": "1",
                                "document": _j.eticheta_factura("borderou", None, numar, data)}, factura_id=fid)
    assert "eroare" not in r, r
    return fid


def _tip_numar(conn, fid):
    with conn.cursor() as cur:
        cur.execute("SELECT tip, numar FROM facturi WHERE id = %s", (fid,))
        return cur.fetchone()


def test_def_c75_borderoul_vechi_trece_pe_tipul_lui_iar_numarul_dublat_primeste_urmatorul(conn):
    """Cazul F1 (434): borderoul vechi BA-1 (Ion Popescu, 19.10) + borderoul nou BA-1 (Maria Ionescu, 20.10) -> vechiul păstrează BA-1 și
    devine borderou, noul primește BA-2 (și fișa de magazie îl spune). OMFP 2634/2015 anexa 1 pct.58 lit.o: programul nu permite
    „editarea a două sau a mai multor documente de același tip, cu același număr și conținut diferit de informații în cadrul aceluiași
    exercițiu financiar”."""
    from core import migrare_borderou_tip_vechi as m
    vechi = _borderou_vechi(conn, "BA-1", "2099-10-19", "Ion Popescu")
    nou = _borderou_nou(conn, "BA-1", "2099-10-20", "Maria Ionescu")
    r = m.aplica(conn, SCH)
    assert [c["id"] for c in r["convertite"]] == [vechi] and r["renumerotate"] == [(nou, "BA-1", "BA-2")], r
    assert _tip_numar(conn, vechi) == ("borderou", "BA-1") and _tip_numar(conn, nou) == ("borderou", "BA-2")
    assert [(v, n) for _i, v, n in r["miscari"]] == [("Borderou de achiziție BA-1 din 20.10.2099", "Borderou de achiziție BA-2 din 20.10.2099")]
    # numerotarea aplicației vede acum borderoul vechi: următorul e BA-3
    from core import documente_interne as di
    with conn.cursor() as cur:
        assert di.cel_mai_mare(cur, SCH, "borderou_achizitie", 2099) == 2
    # idempotentă: a doua rulare nu mai găsește nimic
    r2 = m.aplica(conn, SCH)
    assert not r2["convertite"] and not r2["renumerotate"] and not r2["miscari"] and m.verifica(conn, SCH), r2


def test_c75_doua_borderouri_vechi_cu_numarul_implicit_al_aceleiasi_zile(conn):
    """Numărul implicit de dinainte („BORDEROU-<data>”) se repetă pe aceeași zi: primul îl păstrează, al doilea primește BA-1."""
    from core import migrare_borderou_tip_vechi as m
    a = _borderou_vechi(conn, "BORDEROU-2099-10-05", "2099-10-05", "Ana A")
    b = _borderou_vechi(conn, "BORDEROU-2099-10-05", "2099-10-05", "Bogdan B")
    r = m.aplica(conn, SCH)
    assert sorted(c["id"] for c in r["convertite"]) == [a, b] and r["renumerotate"] == [(b, "BORDEROU-2099-10-05", "BA-1")], r


def test_c75_fara_fals_pozitiv_pe_facturi_primite_reale(conn):
    """O factură primită reală nu se atinge: cu codul furnizorului; din SPV (XML); cu două rânduri; scrisă după lotul 9; fără nota borderoului."""
    from core import facturi_api as _fa, migrare_borderou_tip_vechi as m
    reala = _fa.creeaza_factura(conn, numar="FURN-7", data_emitere="2099-10-07", directie="primita",
                                linii=[{"descriere": "Marfă - Furnizor", "cantitate": 1, "pret_unitar": "100", "cota_tva": 0}],
                                tert_nume="Furnizor", tert_cui="14399840", status="importata", tert_platitor_tva=False)["factura_id"]
    spv = _borderou_vechi(conn, "SPV-1", "2099-10-08", "Persoana X")
    doua = _borderou_vechi(conn, "BA-9", "2099-10-09", "Persoana Y")
    dupa = _borderou_vechi(conn, "BA-10", "2099-10-10", "Persoana Z", creat_la="2026-10-20 06:00")
    fara_nota = _borderou_vechi(conn, "BA-11", "2099-10-11", "Persoana W")
    with conn.cursor() as cur:
        cur.execute("UPDATE facturi SET xml = '<Invoice/>' WHERE id = %s", (spv,))
        cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva) VALUES (%s, 'transport', 1, 5, 0)", (doua,))
        cur.execute("UPDATE inregistrari SET descriere = 'alta' WHERE factura_id = %s", (fara_nota,))
    r = m.aplica(conn, SCH)
    assert r["convertite"] == [] and r["renumerotate"] == [], r
    motive = {c["id"]: mot for c, mot in r["neconvertite"]}
    assert set(motive) == {doua, dupa, fara_nota}, motive   # cu cod / din SPV: nici nu sunt candidați
    # motivul fiecărui candidat neconvertit, întreg (core/test_garzi_pe_text.py: valoarea câmpului, nu „fragmentul apare”)
    assert motive == {doua: "nu are exact un rând cu cantitatea 1 și cota 0",
                      dupa: "scrisă după lotul 9 (de atunci borderoul are tipul lui): nu e forma veche",
                      fara_nota: "nu are nota de contare cu aceeași descriere (forma borderoului vechi)"}, motive
    assert all(_tip_numar(conn, f)[0] == "factura" for f in (reala, spv, doua, dupa, fara_nota))


def test_c75_luna_inchisa_nu_se_atinge_si_se_raporteaza(conn):
    from core import migrare_borderou_tip_vechi as m
    f = _borderou_vechi(conn, "BA-1", "2099-09-10", "Ion Popescu")
    with conn.cursor() as cur:
        cur.execute("INSERT INTO perioade_blocate (an, luna, blocat_de) VALUES (2099, 9, 1)")
    r = m.aplica(conn, SCH)
    motiv_inchisa = "luna 09/2099 e închisă: borderoul vechi rămâne cu tipul „factura” până la redeschiderea ei"
    assert r["convertite"] == [] and [(c["numar"], mot) for c, mot in r["neconvertite"]] == [("BA-1", motiv_inchisa)], r
    assert _tip_numar(conn, f)[0] == "factura"
    assert m.text_raport(SCH, r).split("\n") == [
        "%s: 0 borderouri convertite, 0 numere schimbate, 0 mișcări aliniate, 1 candidat neconvertit" % SCH,
        "  neconvertit: BA-1 din 10.09.2099 (Ion Popescu) — " + motiv_inchisa], m.text_raport(SCH, r)
