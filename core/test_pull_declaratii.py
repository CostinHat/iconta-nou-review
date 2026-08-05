# -*- coding: utf-8 -*-
"""Teste pe pull() — granita COD <-> BAZA DE DATE pentru generatoarele de declaratii.

DE CE (27.07.2026): cele ~175 de teste pe generatoare sunt PURE - cheama calcul_dXXX()
si build_xml() cu fixturi in memorie. Niciunul nu cheama pull(). Dar pull() e exact locul
unde au trait TOATE defectele gasite in iulie:
  - d406.pull citea `cont/debit/credit` in loc de `cont_debit/cont_credit/suma`
    -> GeneralLedgerEntries mereu gol, pentru ORICE firma, sub un `except: pass`;
  - d406.pull cerea coloane inexistente pe facturi -> 0 facturi in SourceDocuments,
    desi existau 5 reale;
  - toate mascate, deci XML valid structural si gol. DUK nu poate prinde asta.

Un test pur nu atinge schema. Cand cineva redenumeste o coloana, testele raman verzi si
declaratia iese goala. Aceste teste sunt puntea care lipsea.

CUM: schema TEMPORARA construita din tenant_template.sql intr-o tranzactie cu ROLLBACK -
acelasi tipar ca `core/audit_schema.auditeaza` (referinta temporara, zero mutatie). NU se
ating tenantii reali, NU se scrie nimic definitiv.

DOUA CLASE DE TESTE:
  A. pull() VEDE datele care exista (daca ar citi coloane gresite, n-ar vedea nimic);
  B. pull() CRAPA ZGOMOTOS cand schema nu se potriveste (mutatie: redenumesc o coloana).
Clasa B e cea care ar fi prins bug-urile din iulie.

LIMITA DECLARATA: pe `SELECT *`, garda de coloane (common.cere_coloane) verifica randurile
CITITE - deci pe o tabela GOALA nu are ce verifica si trece. O coloana disparuta pe o firma
fara salariati nu se semnaleaza. Corect ca mecanism (fara randuri nu ai ce controla), dar
inseamna ca acoperirea depinde de existenta datelor. De aceea fiecare test de mutatie isi
SEAMANA datele intai.
"""
import pytest

from core import db, tenant_provisioning as tp
import inspect
from core.common import Perioada

SCHEMA_T = "ztest_pull"


def _db_ok():
    try:
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture
def schema():
    """Schema temporara din template, populata minimal. ROLLBACK garantat la final."""
    db.init_pool()
    with db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_T)
                cur.execute(tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), SCHEMA_T))
                cur.execute("SET search_path TO %s, public" % SCHEMA_T)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, "
                    "platitor_tva, tip_decont) VALUES "
                    "(1, 'PROBA SRL', '14399840', 'Str. Test 1', 'Bucuresti', 'B', '6202', true, 'L') "
                    "ON CONFLICT (id) DO UPDATE SET nume=EXCLUDED.nume, cui=EXCLUDED.cui")
            yield conn
        finally:
            conn.rollback()


def _factura(conn, **kw):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO facturi (numar, data_emitere, directie, tert_cui, tert_nume, "
            "total, tva, taxare_inversa) VALUES (%s,%s,%s,%s,%s,%s,%s,false) RETURNING id",
            (kw.get("numar", "1"), kw.get("data", "2026-06-15"), kw.get("directie", "emisa"),
             kw.get("cui", "RO14399840"), kw.get("nume", "CLIENT SRL"),
             kw.get("total", 1210), kw.get("tva", 210)))
        fid = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO factura_linii (factura_id, descriere, um, cantitate, pret_unitar, cota_tva) "
            "VALUES (%s,'Serviciu','buc',1,%s,%s)",
            (fid, kw.get("total", 1210) - kw.get("tva", 210), kw.get("cota", 21)))
    return fid


# ============================================================
#  A. pull() VEDE ce exista
# ============================================================
def test_d300_pull_vede_factura_emisa(schema):
    from core import d300
    _factura(schema, total=1210, tva=210)
    prof, facturi = d300.pull(schema, SCHEMA_T, Perioada(2026, luna=6))
    assert prof and prof.get("cui") == "14399840", "profilul firmei nu e citit"
    assert len(facturi) == 1, "factura reala nu ajunge in pull (coloane gresite?)"
    assert float(facturi[0]["tva"]) == 210.0


def test_d300_pull_nu_ia_facturi_din_alta_luna(schema):
    from core import d300
    _factura(schema, data="2026-05-15")
    _, facturi = d300.pull(schema, SCHEMA_T, Perioada(2026, luna=6))
    assert facturi == [], "fereastra de luna nu filtreaza"


def test_d394_pull_vede_factura(schema):
    from core import d394
    _factura(schema)
    rez = d394.pull(schema, SCHEMA_T, Perioada(2026, luna=6))
    assert rez is not None
    text = repr(rez)
    assert "14399840" in text or "CLIENT SRL" in text, "d394.pull nu vede factura reala"


def test_d112_pull_vede_salariatul(schema):
    from core import d112
    with schema.cursor() as cur:
        cur.execute(
            "INSERT INTO salariati (nume, prenume, cnp, data_angajare, salariu_brut, "
            "ore_zi, part_time) VALUES "
            "('POPESCU','ION','1900101410011','2026-01-01',5000,8,false)")
    prof, sal = d112.pull(schema, SCHEMA_T, 2026, 6)
    assert prof.get("cui") == "14399840"
    assert len(sal) == 1, "salariatul activ nu ajunge in pull"
    assert sal[0]["nume"] == "POPESCU"


def test_d112_pull_ignora_salariatul_plecat(schema):
    # Contract incetat INAINTE de luna calculata (data_incetare 2026-05-31 < iunie) -> exclus din D112.
    # Sub Optiunea A, "a plecat" = data_incetare, nu boolean activ (PASUL 1).
    from core import d112
    with schema.cursor() as cur:
        cur.execute(
            "INSERT INTO salariati (nume, prenume, cnp, data_angajare, data_incetare, salariu_brut, "
            "ore_zi, part_time) VALUES "
            "('DEMISIONAT','X','1900101410011','2026-01-01','2026-05-31',5000,8,false)")
    _, sal = d112.pull(schema, SCHEMA_T, 2026, 6)
    assert sal == [], "salariatii cu contract incetat inainte de luna nu intra in D112"


def test_d301_pull_vede_operatiunea(schema):
    from core import d301
    with schema.cursor() as cur:
        cur.execute(
            "INSERT INTO d301_operatiuni (an, luna, tip, nr_doc, data_doc, val_valuta, "
            "tip_valuta, curs, tva) VALUES (2026,6,5,'F1','2026-06-10',100,'EUR',4.97,105)")
    prof, ops = d301.pull(schema, SCHEMA_T, Perioada(2026, luna=6))
    assert prof.get("cui") == "14399840"
    assert len(ops) == 1, "operatiunea D301 nu ajunge in pull"


# ============================================================
#  B. pull() CRAPA ZGOMOTOS pe schema nepotrivita (clasa iulie 2026)
# ============================================================
def _seamana_salariat(conn):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO salariati (nume, prenume, cnp, data_angajare, salariu_brut, "
            "ore_zi, part_time) VALUES "
            "('POPESCU','ION','1900101410011','2026-01-01',5000,8,false)")


def _seamana_d301(conn):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO d301_operatiuni (an, luna, tip, nr_doc, data_doc, val_valuta, "
            "tip_valuta, curs, tva) VALUES (2026,6,5,'F1','2026-06-10',100,'EUR',4.97,105)")


@pytest.mark.parametrize("modul,tabela,coloana,seamana", [
    ("d300", "facturi", "tva", _factura),
    ("d300", "firma_profil", "tip_decont", None),
    ("d112", "salariati", "salariu_brut", _seamana_salariat),
    ("d301", "d301_operatiuni", "curs", _seamana_d301),
])
def test_pull_crapa_zgomotos_cand_coloana_lipseste(schema, modul, tabela, coloana, seamana):
    """Mutatie: redenumesc o coloana pe care pull() o cere. Trebuie EROARE, nu lista goala.

    Asta e testul care ar fi prins bug-urile din iulie: acolo query-ul crapa, masca il
    inghitea, iar generatorul primea zero randuri si scotea o declaratie valida si goala.

    DATELE SE SEAMANA INTAI, si asta conteaza: garda `common.cere_coloane` verifica randurile
    CITITE, deci pe o tabela GOALA nu are ce verifica si trece. Limita reala a gardei, nu doar
    a testului - prima versiune a acestui test picase exact asa (tabela salariati era goala).
    """
    import importlib
    m = importlib.import_module("core.%s" % modul)
    if seamana:
        seamana(schema)
    with schema.cursor() as cur:
        cur.execute("ALTER TABLE %s.%s RENAME COLUMN %s TO %s_x"
                    % (SCHEMA_T, tabela, coloana, coloana))
    with pytest.raises(Exception) as e:
        if "perioada" in inspect.signature(m.pull).parameters:
            m.pull(schema, SCHEMA_T, Perioada(2026, luna=6))
        else:
            m.pull(schema, SCHEMA_T, 2026, 6)
    mesaj = str(e.value).lower()
    assert coloana in mesaj or "does not exist" in mesaj or "exista" in mesaj, \
        "eroarea nu spune ce lipseste: %s" % str(e.value)[:150]


def test_pull_nu_inghite_tabela_lipsa(schema):
    """Aceeasi clasa, la nivel de tabela."""
    from core import d300
    with schema.cursor() as cur:
        cur.execute("ALTER TABLE %s.facturi RENAME TO facturi_x" % SCHEMA_T)
    with pytest.raises(Exception):
        d300.pull(schema, SCHEMA_T, Perioada(2026, luna=6))


def test_schema_temporara_chiar_dispare():
    """Garda pe test: schema de proba NU trebuie sa ramana in baza dupa rulare."""
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM information_schema.schemata WHERE schema_name=%s",
                        (SCHEMA_T,))
            assert cur.fetchone() is None, \
                "schema %s a ramas in baza - ROLLBACK-ul n-a functionat" % SCHEMA_T
        conn.rollback()


def test_d112_pull_prorateaza_facilitatea_la_incetare(schema):
    # REGRESIE (PASUL 1): incetare la mijloc de luna -> facilitatea se prorateaza (OUG 156/2024 art.LXVI
    # alin.4 lit.d). Bug prins de proba functionala: pull() reconstruia dict-ul salariatului FARA
    # data_incetare -> calcul primea None -> facilitate INTREAGA (300) in loc de proratata.
    from core import d112
    with schema.cursor() as cur:
        cur.execute(
            "INSERT INTO salariati (nume, prenume, cnp, data_angajare, data_incetare, salariu_brut, "
            "ore_zi, part_time) VALUES "
            "('MIN','A','1900101410011','2026-01-01','2026-06-20',4050,8,false)")
    _, sal = d112.pull(schema, SCHEMA_T, 2026, 6)
    assert len(sal) == 1
    assert float(sal[0]["facilitate"]) == 200.0, sal[0].get("facilitate")   # 300 x 14/21 (incetare 20 iun 2026), nu 300 intreg


def test_d112_facilitate_prorata_la_mentinere_partiala(schema):
    # GARD PERMANENT (mutat din test_datorie dupa modelarea salariu_istoric, PASUL 2a): facilitatea se
    # prorateaza pe zilele in care salariul e MENTINUT la minim (OUG 156/2024 art.LXVI alin.4 lit.a).
    # Salariat la minim (4050) pana pe 15 iun, marit la 5000 din 16 -> facilitate pe zilele 1-15 (10/21).
    from core import d112
    with schema.cursor() as cur:
        cur.execute("INSERT INTO salariati (id, nume, prenume, cnp, data_angajare, salariu_brut, ore_zi, "
                    "part_time) OVERRIDING SYSTEM VALUE VALUES "
                    "(1,'MARIRE','A','1900101410011','2026-01-01',5000,8,false)")
        cur.execute("INSERT INTO salariu_istoric (salariat_id, valabil_din, salariu_brut) "
                    "VALUES (1,'2026-01-01',4050),(1,'2026-06-16',5000)")
    _, sal = d112.pull(schema, SCHEMA_T, 2026, 6)
    assert len(sal) == 1
    assert round(float(sal[0]["facilitate"]), 2) == round(300 * 10 / 21, 2), sal[0].get("facilitate")  # 142.86 = 300 x 10/21 (zile la minim 1-15 iun)


def test_cm_arbori_paraleli_acelasi_rezultat(schema):
    # [UNIFICARE CM] Cele DOUA lanturi trebuie sa dea ACELASI tratament pe indemnizatia de CM:
    #   - lantul FLUTURAS: salarizare.taxe_cm(indemnizatie, cod) - CAS 25% uniform, CASS doar 01/07/10;
    #   - lantul DECLARATIE: d112 (care acum APELEAZA taxe_cm) - baza CAS (B4_7) include indemnizatia,
    #     baza CASS (B4_5) o include DOAR daca taxe_cm zice ca se datoreaza CASS.
    # Proba pe cod 08 (maternitate, CASS-scutit): taxe_cm cass=0 <=> d112 exclude indemnizatia din B4_5.
    # Inainte de unificare d112 aplica CASS uniform -> testul pica (divergenta reala).
    from core import d112
    from core.salarizare import taxe_cm
    import re
    from datetime import date
    CM_ANG, CM_FNUASS = 1000, 3000        # indemnizatie 4000 (cm_base)
    cm_base = CM_ANG + CM_FNUASS
    with schema.cursor() as cur:
        cur.execute("INSERT INTO salariati (id, nume, prenume, cnp, data_angajare, salariu_brut, ore_zi, "
                    "part_time) OVERRIDING SYSTEM VALUE VALUES "
                    "(1,'CM','B','1900101410011','2026-01-01',6000,8,false)")
        cur.execute("INSERT INTO concedii_medicale (salariat_id, an, luna, cod, zile, indemnizatie, baza, "
                    "media_zilnica, procent, diminuare, zile_platite, zile_ang, zile_fnuass, brut_ang, "
                    "brut_fnuass, cass, impozit, cas, net) VALUES "
                    "(1,2026,6,'08',10,%s,0,0,85,false,10,5,5,%s,%s,0,0,0,0)",
                    (cm_base, CM_ANG, CM_FNUASS))
    xml, _av = d112.genereaza(schema, SCHEMA_T, 2026, 6)
    m = re.search(r'<asiguratB4[^>]*B4_5="(\d+)"[^>]*B4_7="(\d+)"', xml)
    assert m, "randul B4 nu s-a gasit in XML"
    b4_5 = int(m.group(1))   # baza CASS
    b4_7 = int(m.group(2))   # baza CAS
    # lantul fluturas: cod 08 e scutit de CASS
    flut = taxe_cm(cm_base, "08", la_data=date(2026, 6, 1))
    assert flut["cass"] == 0, "fluturas: cod 08 trebuie scutit de CASS"
    # lantul declaratie trebuie sa fie DE ACORD: indemnizatia (cod 08) e in baza CAS dar NU in baza CASS
    assert b4_7 - b4_5 == cm_base, (
        "d112 nu exclude indemnizatia cod-08 din baza CASS: B4_7=%d B4_5=%d, diferenta trebuie cm_base=%d "
        "(divergenta fluturas/declaratie)" % (b4_7, b4_5, cm_base))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def _seed_cod09(schema, cnp_ingrijit):
    with schema.cursor() as cur:
        cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time) "
                    "OVERRIDING SYSTEM VALUE VALUES (1,'ING','A','2900101410011','2025-01-01',9000,8,false)")
        cur.execute("INSERT INTO salariu_istoric (salariat_id,valabil_din,salariu_brut) VALUES (1,'2025-01-01',9000)")
        cur.execute("INSERT INTO concedii_medicale (id,salariat_id,an,luna,cod,zile,zile_ang,zile_fnuass,brut_ang,"
                    "brut_fnuass,baza,media_zilnica,serie,numar,data_acordare,data_inceput,data_sfarsit,loc_prescriere,"
                    "cnp_ingrijit) OVERRIDING SYSTEM VALUE VALUES (1,1,2026,6,'09',5,0,5,0,3000,9000,600,'AB','1',"
                    "'2026-06-01','2026-06-01','2026-06-05',1,%s)", (cnp_ingrijit,))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d112_cod09_fara_cnp_copil_blocheaza_emisia(schema):
    """[D_8, regula DUK S97 + regula bazei nule] cod 09/91/92 cer CNP-ul copilului (D_8). Un certificat FARA CNP
    (sau cu CNP invalid) BLOCHEAZA generarea cu mesaj explicit - NU se emite D112 invalid la ANAF."""
    from core import d112
    _seed_cod09(schema, None)
    with pytest.raises(ValueError) as ei:
        d112.genereaza(schema, SCHEMA_T, 2026, 6)
    assert "D_8" in str(ei.value) and "cod 09" in str(ei.value), str(ei.value)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d112_cod09_cu_cnp_copil_emite_d8_si_e_duk_valid(schema):
    """[D_8] cod 09 cu CNP copil VALID -> emite D_8="<cnp>" + declaratia e DUK VALIDA. Acesta e lantul care
    inainte NU era probat DUK (cod 09 pica pe S97 lipsa D_8 -> se folosea cod 08 ca inlocuitor). CNP 5200515400016
    e valid (cifra de control). Gard anti-regresie pe lantul de ingrijire copil."""
    from core import d112, duk as _duk
    import re
    _seed_cod09(schema, "5200515400016")
    xml, _av = d112.genereaza(schema, SCHEMA_T, 2026, 6)
    d = re.search(r'<asiguratD[^>]*D_9="09"[^>]*/>', xml)
    assert d, "randul asiguratD cod 09 lipseste"
    assert 'D_8="5200515400016"' in d.group(0), "D_8 (CNP copil) neemis: " + d.group(0)
    if _duk.poate_valida("d112"):
        r = _duk.valideaza(xml, "d112", an=2026, luna=6)
        assert r["stare"] == "valid", "cod 09 cu D_8 trebuie DUK-valid: " + (r.get("erori") or "")[:200]


def test_d112_impozit_multi_certificat_partitie_per_cert(schema):
    """[impozit CM multi-cert] Luna cu MAI MULTE certificate mixte: cod 01 (impozabil) + cod 09 (neimpozabil) +
    zile lucrate. Scazamintele cm_cas_imp/cm_cass_imp se acumuleaza PER-CERTIFICAT in bucla (d112.py: for _x in cms:
    if _cod not in _sz._CM_COD_NEIMPOZABIL: cm_cas_imp += _xcas) -> partitia impozabil/neimpozabil SUPRAVIETUIESTE
    insumarii (nu se calculeaza pe total). brut 12600, 4 zile cod 01 (brut_ang 2000) + 3 zile cod 09 (brut_fnuass 1500)
    -> brut_lucrat 8400, ded 0.
    CORECT: impozit 676 (baza = 8400 salariu + 2000 cod01; se scad salariu+cod01 CAS/CASS; cod 09 EXCLUS complet).
    RED (mutatie built-in: golirea setului -> cod 09 impozitat): 789. Diferenta 113 = 10%*(1500-375) = fix partea cod09.
    NOTA: cod 09/91 e DUK-invalid separat (lipseste D_8 CNP copil, gap preexistent - vezi GARZI 05.08); proba DUK pe
    multi-cert = cod 01+08 (identic 676, DUK valid, /tmp/probe_m08).
    """
    import re
    from core import d112, salarizare as _sz
    def _seed(cur):
        cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time) "
                    "OVERRIDING SYSTEM VALUE VALUES (1,'M','A','2900101410011','2025-01-01',12600,8,false)")
        cur.execute("INSERT INTO salariu_istoric (salariat_id,valabil_din,salariu_brut) VALUES (1,'2025-01-01',12600)")
        cur.execute("INSERT INTO concedii_medicale (id,salariat_id,an,luna,cod,zile,zile_ang,zile_fnuass,brut_ang,"
                    "brut_fnuass,baza,media_zilnica,serie,numar,data_acordare,data_inceput,data_sfarsit,loc_prescriere)"
                    " OVERRIDING SYSTEM VALUE VALUES (1,1,2026,6,'01',4,4,0,2000,0,12600,600,'A','1','2026-06-01',"
                    "'2026-06-01','2026-06-04',1)")
        cur.execute("INSERT INTO concedii_medicale (id,salariat_id,an,luna,cod,zile,zile_ang,zile_fnuass,brut_ang,"
                    "brut_fnuass,baza,media_zilnica,serie,numar,data_acordare,data_inceput,data_sfarsit,loc_prescriere,cnp_ingrijit)"
                    " OVERRIDING SYSTEM VALUE VALUES (2,1,2026,6,'09',3,0,3,0,1500,12600,500,'A','2','2026-06-10',"
                    "'2026-06-10','2026-06-12',1,'5200515400016')")   # cod 09 cere CNP copil (D_8) - vezi test_d112_cod09_*
    with schema.cursor() as cur:
        _seed(cur)
    def _imp():
        xml, _av = d112.genereaza(schema, SCHEMA_T, 2026, 6)
        return int(re.search(r'E1_6="(\d+)"', re.search(r"<asiguratE1[^>]*/>", xml).group(0)).group(1))
    assert _imp() == 676, "impozit multi-cert (cod01 impozabil + cod09 neimpozabil) trebuie 676"
    # RED built-in: golirea setului neimpozabil -> cod 09 devine impozabil -> 789 (dovada partitie PER-CERT, nu pe total)
    _orig = _sz._CM_COD_NEIMPOZABIL
    _sz._CM_COD_NEIMPOZABIL = ()
    try:
        assert _imp() == 789, "mutatie (nimic exclus): cod 09 impozitat -> 789 (dovada ca 09 e exclus per-certificat)"
    finally:
        _sz._CM_COD_NEIMPOZABIL = _orig


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cm_coduri_14_18_raman_impozabile_decizie_05_08():
    """[DECIZIE 05.08.2026, vezi DECIZII.md] Codurile 14 (neoplazii/SIDA ale ASIGURATULUI - boala proprie, NU
    'ingrijirea pacientului oncologic' din art.62 lit.c care e cod 17=ingrijitorul) si 18 (carantina/izolare copil,
    NU 'copil bolnav') sunt IMPOZABILE - nu intra in CF art.62 lit.c. Setul neimpozabil e PINUIT: daca cineva muta 14
    sau 18 (sau schimba setul) fara sa modifice DECIZII.md, testul pica -> forteaza re-decizia."""
    from core.salarizare import _CM_COD_NEIMPOZABIL
    assert "14" not in _CM_COD_NEIMPOZABIL, "cod 14 (neoplazii/SIDA proprii) mutat in neimpozabil - re-decizie in DECIZII.md"
    assert "18" not in _CM_COD_NEIMPOZABIL, "cod 18 (carantina/izolare copil) mutat in neimpozabil - re-decizie in DECIZII.md"
    assert set(_CM_COD_NEIMPOZABIL) == {"08", "09", "15", "17", "91", "92"}, (
        "setul _CM_COD_NEIMPOZABIL s-a schimbat fata de decizia 05.08 (art.62 lit.c) - actualizeaza DECIZII.md + acest gard")


def test_d112_impozit_exclude_indemnizatia_cm_neimpozabila_luna_mixta(schema):
    """[impozit CM, CF art.62 lit.c] Indemnizatiile de maternitate(08)/ingrijire copil(09/91/92)/risc maternal(15)/
    oncologic(17) sunt NEIMPOZABILE. Baza impozitului le exclude, SI exclude CAS/CASS aferent lor (SIMETRIE - altfel
    CAS 25% pe indemnizatia neimpozabila ar cobori bimp = sub-declarare impozit). CAS/CASS EMISE raman pe toate codurile.
    CAZ MIXT (nu luna intreaga de CM, care s-ar clampa la 0 si ar ascunde bug-ul de simetrie): brut 12600, iunie 2026
    (nzl=21), 6 zile cod 08 maternitate -> brut_lucrat=9000 (>plafon deducere -> ded=0). Indemnizatie 4000.
    CORECT (simetric): bimp = 9000 - _d112int(9000*25%)=2250 - _d112int(9000*10%)=900 - 0 = 5850 -> impozit 585.
    Distinct de: BUGGY (impoziteaza si maternitatea) = 885; NAIV (scoate baza CM dar lasa CAS pe ea) = 485.
    Probat RED pe cod vechi: impozit emis 885 (vs 585). MUTATIE: readu cm_base neimpozabil in baza -> pica.
    """
    import re
    from core import d112
    from core.salarizare import taxe_cm
    from datetime import date
    with schema.cursor() as cur:
        cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time) "
                    "OVERRIDING SYSTEM VALUE VALUES (1,'MIXT','A','2900101410011','2025-01-01',12600,8,false)")
        cur.execute("INSERT INTO salariu_istoric (salariat_id,valabil_din,salariu_brut) VALUES (1,'2025-01-01',12600)")
        cur.execute("INSERT INTO concedii_medicale (id,salariat_id,an,luna,cod,zile,zile_ang,zile_fnuass,brut_ang,"
                    "brut_fnuass,baza,media_zilnica,serie,numar,data_acordare,data_inceput,data_sfarsit,loc_prescriere) "
                    "OVERRIDING SYSTEM VALUE VALUES (1,1,2026,6,'08',6,0,6,0,4000,12600,600,'AB','1','2026-06-01',"
                    "'2026-06-01','2026-06-06',1)")
    xml, _av = d112.genereaza(schema, SCHEMA_T, 2026, 6)
    b4 = re.search(r"<asiguratB4[^>]*/>", xml).group(0)
    e1 = re.search(r"<asiguratE1[^>]*/>", xml).group(0)
    def g(seg, a): return int(re.search(a + r'="(\d+)"', seg).group(1))
    # CAS/CASS EMISE = pe TOATE codurile (neschimbate de fix): CAS 25% pe salariu(9000)+indemnizatie(4000)
    assert g(b4, "B4_8") == 3250, "B4_8 CAS emis (pe toate codurile) = 3250: " + b4
    assert g(b4, "B4_6") == 900, "B4_6 CASS emis (cod 08 exclus CASS) = 900: " + b4
    assert g(b4, "B4_7") == 13000, "B4_7 baza CAS (include indemnizatia) = 13000: " + b4
    # IMPOZIT = pe baza IMPOZABILA (exclude maternitatea SI CAS/CASS aferent) = 585, NU 885 (buggy) sau 485 (naiv)
    assert g(e1, "E1_6") == 585, "impozit trebuie 585 (simetric), nu 885 (buggy)/485 (naiv): " + e1
    # lantul FLUTURAS (taxe_cm) trebuie CONSISTENT: impozit 0 pe maternitate; CAS ramane (art.139(1)(o))
    flut = taxe_cm(4000, "08", la_data=date(2026, 6, 1))
    assert int(flut["impozit"]) == 0, "taxe_cm cod 08 (maternitate) impozit trebuie 0 (CF art.62 lit.c): %s" % flut
    assert int(flut["cas"]) == 1000, "taxe_cm cod 08 CAS ramane 25%% (art.139(1)(o)): %s" % flut
    # cod 01 (boala) RAMANE impozabil - fix-ul nu afecteaza codurile taxabile
    flut01 = taxe_cm(4000, "01", la_data=date(2026, 6, 1))
    assert int(flut01["impozit"]) > 0, "taxe_cm cod 01 (boala) trebuie sa ramana impozabil: %s" % flut01


def test_d112_poarta_reconciliaza_valorile_emise_nu_pre_emisia(schema):
    """[B, 05.08.2026] Poarta cale2 primeste valorile EMISE (post _d112_genereaza), nu pre-emisia din pull.
    Blind-spot inainte: verifica_reconciliere rula pe salariati DIN pull (contributii intermediare), iar layerul
    de EMISIE recalcula - un bug de emisie nu ajungea la poarta desi ajungea la ANAF. Acum _d112_genereaza scrie
    contributiile EMISE (B4_8/B4_6) inapoi in salariat, iar poarta ruleaza DUPA emisie.
    PROBA: (1) dupa emisie salariatul poarta valorile EMISE (== B4_8/B4_6 din XML); (2) un emis GRESIT (mutatie pe
    valoarea EMISA, nu pe pull) e prins de poarta - dovada ca poarta acopera acum layerul de emisie."""
    import re, pytest
    from core import d112
    from core.d112_reconciliere import verifica_reconciliere, ReconciliereD112
    with schema.cursor() as cur:
        cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time) "
                    "OVERRIDING SYSTEM VALUE VALUES (1,'S','A','1900101410011','2025-01-01',6000,8,false)")
        cur.execute("INSERT INTO salariu_istoric (salariat_id,valabil_din,salariu_brut) VALUES (1,'2025-01-01',6000)")
    prof, sal = d112.pull(schema, SCHEMA_T, 2026, 6)
    rez = d112._d112_genereaza(prof, sal, 2026, 6)   # scrie contributiile EMISE inapoi in sal
    xml = rez[0] if isinstance(rez, tuple) else rez
    b4 = re.search(r"<asiguratB4[^>]*/>", xml).group(0)
    b4_8 = int(re.search(r'B4_8="(\d+)"', b4).group(1))
    b4_6 = int(re.search(r'B4_6="(\d+)"', b4).group(1))
    # (1) write-back: salariatul poarta ACUM valorile EMISE (6000*25%=1500 / 10%=600)
    assert int(sal[0]["cas"]) == b4_8 == 1500, (sal[0].get("cas"), b4_8)
    assert int(sal[0]["cass"]) == b4_6 == 600, (sal[0].get("cass"), b4_6)
    # (2) un emis GRESIT (bug de layer emisie, simulat pe valoarea EMISA) e prins de poarta
    sal[0]["cas"] = b4_8 + 500
    with pytest.raises(ReconciliereD112):
        verifica_reconciliere(schema, SCHEMA_T, 2026, 6, sal)


def test_d112_cm_baza_salariala_realizata_nu_brut_intreg(schema):
    """[d112_cm_baza_realizata_v1] NECONFORMITATE FISCALA reparata 05.08.2026: in luna cu concediu medical,
    baza CAS/CASS/CAM (B2_5/B4_7/B4_5/B4_14) = castigul brut REALIZAT pe zile LUCRATE (CF art.139(1) "castigul
    brut REALIZAT din salarii"; structura D112 B4_7=B2_5+B3_7 aditiv - baza salariala realizata + baza
    indemnizatiei CM), NU brutul contractual. Brutul contractual ramane doar in B1_sal1/B4_3 (informativ).
    Inainte de fix, emisia pe brut INTREG supra-declara CAS/CASS/CAM la ANAF si diverga de fluturas (calcul_salariu
    pe brut_lucrat). MUTATIE (probata): reasignarea bazac in ramura CM readusa la brutul intreg -> B4_8=3100 -> pica.
    Fixtura: brut 8400, iunie 2026 (nzl=21 zile lucratoare), 5 zile CM cod 01 (brut_ang=4000, cm_base=4000).
    brut_lucrat=8400*16/21=6400 EXACT (fara granita de rotunjire). Astepta: baza realizata 6400, nu 8400.
    """
    import re
    from core import d112
    with schema.cursor() as cur:
        cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time) "
                    "OVERRIDING SYSTEM VALUE VALUES (1,'CM','R','1900101410011','2025-01-01',8400,8,false)")
        cur.execute("INSERT INTO salariu_istoric (salariat_id,valabil_din,salariu_brut) VALUES (1,'2025-01-01',8400)")
        cur.execute("INSERT INTO concedii_medicale (id,salariat_id,an,luna,cod,zile_ang,zile_fnuass,brut_ang,brut_fnuass) "
                    "OVERRIDING SYSTEM VALUE VALUES (1,1,2026,6,'01',5,0,4000,0)")
    xml, _av = d112.genereaza(schema, SCHEMA_T, 2026, 6)
    b1 = re.search(r"<asiguratB1[^>]*/>", xml).group(0)
    b2 = re.search(r"<asiguratB2[^>]*/>", xml).group(0)
    b4 = re.search(r"<asiguratB4[^>]*/>", xml).group(0)
    def g(seg, attr):
        return int(re.search(attr + r'="(\d+)"', seg).group(1))
    # baza salariala CAS = REALIZAT (brut_lucrat 6400), nu contractual 8400
    assert g(b2, "B2_5") == 6400, "B2_5 (baza CAS salariala) trebuie 6400 realizat, nu 8400 contractual: " + b2
    # B4_7 (baza CAS) = B2_5 realizat 6400 + B3_7 (cm_base 4000) = 10400 (nu 12400)
    assert g(b4, "B4_7") == 10400, "B4_7 = baza realizata 6400 + cm 4000 = 10400: " + b4
    # B4_8 (CAS) = round(10400*25%) = 2600 (nu 3100 pe brut intreg)
    assert g(b4, "B4_8") == 2600, "B4_8 CAS pe baza realizata = 2600, nu 3100 (over-declarare): " + b4
    # CASS: B4_5 = 6400+4000 = 10400 ; B4_6 = round(10400*10%) = 1040 (nu 1240)
    assert g(b4, "B4_5") == 10400, "B4_5 baza CASS realizata = 10400: " + b4
    assert g(b4, "B4_6") == 1040, "B4_6 CASS pe baza realizata = 1040, nu 1240: " + b4
    # brutul CONTRACTUAL ramane in B1_sal1 (8400) - NU se prorateaza
    assert g(b1, "B1_sal1") == 8400, "B1_sal1 = salariul contractual 8400 (informativ, neproratat): " + b1


def test_d112_maternitate_cod08_c2_rd3(schema):
    # [D112 D-field] CM cod 08 (maternitate) -> agregatele C2 pe Rd.3 (C2_31/32/34/36), NU pe Rd.1;
    # maternitatea e 100% FNUASS (D_20=0). Inainte d112 punea 08 in Rd.1 -> DUK respingea (C2_32 lipsa).
    from core import d112
    with schema.cursor() as cur:
        cur.execute("INSERT INTO salariati (id, nume, prenume, cnp, data_angajare, salariu_brut, ore_zi, "
                    "part_time) OVERRIDING SYSTEM VALUE VALUES "
                    "(1,'MAT','A','2900101410011','2026-01-01',6000,8,false)")
        cur.execute("INSERT INTO concedii_medicale (salariat_id, an, luna, cod, zile, indemnizatie, baza, "
                    "media_zilnica, procent, diminuare, zile_platite, zile_ang, zile_fnuass, brut_ang, "
                    "brut_fnuass, cass, impozit, cas, net) VALUES "
                    "(1,2026,6,'08',10,4000,6000,400,85,false,10,0,10,0,4000,0,300,1000,2700)")
    xml, _av = d112.genereaza(schema, SCHEMA_T, 2026, 6)
    import re
    m = re.search(r'<angajatorC2[^>]*/>', xml)
    assert m, "angajatorC2 negasit"
    c2 = m.group(0)
    assert 'C2_31="1"' in c2 and 'C2_32="10"' in c2 and 'C2_36="4000"' in c2, "maternitatea nu e pe Rd.3: " + c2
    assert 'C2_11="0"' in c2 and 'C2_16="0"' in c2, "maternitatea nu e exclusa din Rd.1: " + c2


def test_d112_urgenta_cod06_emite_d11(schema):
    # [D112 D-field] CM cod 06 (urgenta medico-chirurgicala) cere D_11 (cod urgenta, HG 423/2020, C(3),
    # obligatoriu daca D_9=06). Inainte D_11 nu se emitea -> DUK: "Nu s-a completat codul de urgenta".
    from core import d112
    with schema.cursor() as cur:
        cur.execute("INSERT INTO salariati (id, nume, prenume, cnp, data_angajare, salariu_brut, ore_zi, "
                    "part_time) OVERRIDING SYSTEM VALUE VALUES "
                    "(1,'URG','C','1900101410011','2026-01-01',6000,8,false)")
        cur.execute("INSERT INTO concedii_medicale (salariat_id, an, luna, cod, zile, indemnizatie, baza, "
                    "media_zilnica, procent, diminuare, zile_platite, zile_ang, zile_fnuass, brut_ang, "
                    "brut_fnuass, cass, impozit, cas, net, cod_urgenta) VALUES "
                    "(1,2026,6,'06',10,4000,6000,400,100,false,10,5,5,2000,2000,0,300,1000,2700,123)")
    xml, _av = d112.genereaza(schema, SCHEMA_T, 2026, 6)
    import re
    m = re.search(r'<asiguratD[^>]*D_9="06"[^>]*/>', xml)
    assert m, "asiguratD cod 06 negasit in XML"
    d = m.group(0)
    assert 'D_11="123"' in d, "D_11 (cod urgenta) nu e emis la cod 06: " + d



def test_d390_pull_incadreaza_pe_data_emitere_exigibilitate(schema):
    """D390 incadreaza o operatiune IC in luna dupa DATA EMITERII facturii = exigibilitatea
    intracomunitara (CF art.283 livrari / art.284 achizitii: exigibilitatea intervine la data
    emiterii facturii; CF art.325 alin.(1)/(4): declaratia se face pentru luna in care ia nastere
    exigibilitatea). pull() filtreaza data_emitere in [luna-01, (luna+1)-01). Gard temporal (golul
    de acoperire semnalat la clusterul exigibilitate/prag): testele calcul ocoleau pull, deci
    incadrarea pe luna nu era testata. Mutant: o fereastra gresita sau alt camp de data ar aduce
    si factura din mai/iulie -> testul cade."""
    from core import d390
    _factura(schema, numar="E1", data="2026-06-30", directie="emisa",
             cui="IT00905811006", nume="IT PARTNER", total=5000, tva=0)   # in fereastra iunie
    _factura(schema, numar="E2", data="2026-07-01", directie="emisa",
             cui="IT00905811006", nume="IT PARTNER", total=9999, tva=0)   # iulie -> exclus
    _factura(schema, numar="E3", data="2026-05-31", directie="emisa",
             cui="IT00905811006", nume="IT PARTNER", total=8888, tva=0)   # mai -> exclus
    _, facturi = d390.pull(schema, SCHEMA_T, 2026, 6)
    totaluri = sorted(f["total"] for f in facturi)
    assert totaluri == [5000], (
        "D390 iunie trebuie sa contina DOAR factura cu data_emitere in iunie "
        "(exigibilitate art.283/284), nu mai/iulie: %r" % (totaluri,))



def test_d101_rezerva_legala_din_conturi_reale(schema):
    """PROBA pe date reale (A1): d101.pull sursa capital (1012), rezerva existenta (1061) si cheltuiala
    cu impozitul (691) din inregistrari_linii; calcul_d101 computa P13 = rezerva legala deductibila
    (CF art.26 alin.(1) lit.a). Fara sursare/calcul, deducerea nu se aplica si firma SUPRA-DECLARA
    impozitul pe profit. Aici: capital subscris/varsat 200000, profit brut 350000 (300000 + 50000
    cheltuiala impozit adaugata inapoi), fara rezerva anterioara -> P13 = min(5%*350000=17500;
    20%*200000-0=40000) = 17500. Gard SOURCING (pull citeste conturile reale)."""
    from core import d101
    from core.common import Perioada
    with schema.cursor() as cur:
        cur.execute("INSERT INTO inregistrari (data, status) VALUES ('2026-06-30','validata') RETURNING id")
        iid = cur.fetchone()[0]
        for cd, cc, suma in [("5121", "1012", 200000),   # capital subscris varsat
                             ("4111", "707", 1000000),    # venituri din exploatare
                             ("607", "401", 650000),      # cheltuieli de exploatare
                             ("691", "4411", 50000)]:      # cheltuiala cu impozitul pe profit
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                        "VALUES (%s,%s,%s,%s)", (iid, cd, cc, suma))
    xml, res = d101.genereaza(schema, SCHEMA_T, Perioada(2026))
    assert res.P.get("P13") == 17500, ("P13 asteptat 17500, primit %r" % res.P.get("P13"))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d112_brut_si_baza_pe_salariul_lunii_nu_contractual_curent(schema):
    """[fix salariu-la-data 06.08.2026] CLASA (nu doar cazul E1): brutul si baza DECLARATE in D112 =
    salariul LUNII (date-aware, din salariu_istoric), NU salariati.salariu_brut (contractual CURENT).
    Un salariat cu majorare in cursul anului (minim 4050 -> 5000 la 01.07) trebuie sa emita, pentru o luna
    DE DINAINTE de majorare, brutul MIC, cu baza CONSISTENTA cu contributia (regula DUK S74d:
    B4_8 = ROUND(B4_7 * 0.25)). Bug-ul (migrare 29.07 pe jumatate): d112.pull lasa s['brut'] pe
    salariati.salariu_brut (stale) pentru brut/baza, iar contributiile foloseau salariul date-aware ->
    B4_7 pe 5000 dar B4_8 pe 4050 -> divergenta interna -> respins de DUK. Prinde clasa la nivel de
    INVARIANT (baza <-> contributie), nu pe cifrele unei instante. MUTATIE: revino la s['brut']=stale in
    d112.pull -> ambele asserturi pica."""
    import re
    from core import d112
    with schema.cursor() as cur:
        cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time) "
                    "OVERRIDING SYSTEM VALUE VALUES (1,'MAJ','A','1900101410011','2026-01-01',5000,8,false)")
        cur.execute("INSERT INTO salariu_istoric (salariat_id,valabil_din,salariu_brut) "
                    "VALUES (1,'2026-01-01',4050),(1,'2026-07-01',5000)")
    xml, _av = d112.genereaza(schema, SCHEMA_T, 2026, 2)   # FEBRUARIE, inainte de majorarea de la 01.07
    m = re.search(r'<asiguratB4\b([^>]*)/>', xml)
    assert m, "randul asiguratB4 nu s-a gasit in XML"
    at = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
    b3, b7, b8 = int(at["B4_3"]), int(at["B4_7"]), int(at["B4_8"])
    # 1) brutul DECLARAT = salariul LUNII (4050), NU contractualul curent (5000)
    assert b3 == 4050, (
        "B4_3=%d: brutul declarat trebuie sa fie salariul LUNII (4050), nu contractualul curent (5000) - "
        "consumator de salariu care citeste valoarea curenta acolo unde regula e 'la data lunii'" % b3)
    # 2) INVARIANT DE CLASA: baza CAS (B4_7) consistenta cu contributia CAS (B4_8 = ROUND(B4_7*25%%), DUK S74d)
    assert abs(b8 - round(b7 * 0.25)) <= 1, (
        "B4_7=%d dar B4_8=%d: baza si contributia CAS pe salarii sunt pe snapshot-uri DIFERITE de salariu "
        "(brut/baza stale vs contributie date-aware) - regula DUK S74d incalcata" % (b7, b8))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d112_part_time_baza_minima_salariul_minim_integral(schema):
    """[fix part-time-floor 06.08.2026] baza minima part-time (CAS art.146 alin.(5^6) / CASS art.157) = salariul
    de baza minim brut INTEGRAL in vigoare in luna, NU sm-facilitate. Facilitatea de 300/200 lei se aplica DOAR
    salariatilor cu NORMA INTREAGA (OUG 156/2024 art.LXVI), deci nu diminueaza floor-ul part-time. Salariat
    part-time sub prag, luna intreaga, iunie 2026 (salariu minim 4050): baza minima emisa (B4_5P) = 4050, NU 3750
    (=4050-300). MUTATIE: prag_pt = sm - fac in d112.pull -> B4_5P=3750 -> pica. NOTA: DUK da atentionare pe
    4050 (validatorul scade facilitatea = 3750) - divergenta lege<->validator, urmarim legea (decizie Costin)."""
    import re
    from core import d112
    with schema.cursor() as cur:
        cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time) "
                    "OVERRIDING SYSTEM VALUE VALUES (1,'PT','A','1900101410011','2026-01-01',2000,4,true)")
    xml, _av = d112.genereaza(schema, SCHEMA_T, 2026, 6)
    m = re.search(r'<asiguratB4\b([^>]*)/>', xml)
    at = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
    b5p = int(at.get("B4_5P", 0))
    assert b5p == 4050, (
        "B4_5P=%d: baza minima part-time trebuie sa fie salariul minim INTEGRAL (4050), nu sm-facilitate (3750) - "
        "facilitatea e doar norma intreaga (art.LXVI)" % b5p)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d112_exclude_salariat_neangajat_inca_in_luna(schema):
    """[fix data-angajare 06.08.2026] CLASA: selectia salariatilor activi PE PERIOADA trebuie sa filtreze si
    data_angajare, nu doar data_incetare. D112 pe o luna ANTERIOARA angajarii NU trebuie sa includa salariatul
    (altfel DUK S7: dataAng > data raportare). MUTATIE: scoaterea gardului data_angajare din pull -> salariatul
    apare in ianuarie -> pica."""
    from core import d112
    with schema.cursor() as cur:
        cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time) "
                    "OVERRIDING SYSTEM VALUE VALUES (1,'NOU','A','1900101410011','2026-03-15',5000,8,false)")
    _p, sal_ian = d112.pull(schema, SCHEMA_T, 2026, 1)   # inainte de angajare (15.03)
    assert len(sal_ian) == 0, "salariat angajat 15.03 NU trebuie inclus in D112 pe ianuarie (era %d)" % len(sal_ian)
    _p, sal_mar = d112.pull(schema, SCHEMA_T, 2026, 3)   # luna angajarii
    assert len(sal_mar) == 1, "salariat angajat 15.03 trebuie inclus in D112 pe martie (era %d)" % len(sal_mar)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d112_cod15_D23_RM(schema):
    """[cod15 risc maternal] asiguratD D_23 trebuie "RM" pt cod 15 (OUG 96/2003 + OUG 158/2005; regula DUK:
    daca D_9=15 atunci D_23=RM). MUTATIE: D_23=diagnostic -> pica."""
    import re
    from core import d112
    with schema.cursor() as cur:
        cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time) "
                    "OVERRIDING SYSTEM VALUE VALUES (1,'RM','A','1900101410011','2025-01-01',6000,8,false)")
        cur.execute("INSERT INTO salariu_istoric (salariat_id,valabil_din,salariu_brut) VALUES (1,'2025-01-01',6000)")
        cur.execute("INSERT INTO concedii_medicale (salariat_id,an,luna,cod,zile,zile_ang,zile_fnuass,brut_ang,"
                    "brut_fnuass,baza,media_zilnica,serie,numar,data_acordare,data_inceput,data_sfarsit,loc_prescriere) "
                    "VALUES (1,2026,6,'15',10,0,10,0,3000,6000,300,'AB','1','2026-06-01','2026-06-01','2026-06-10',1)")
    xml, _ = d112.genereaza(schema, SCHEMA_T, 2026, 6)
    m = re.search(r'<asiguratD[^>]*D_9="15"[^>]*/>', xml)
    assert m and 'D_23="RM"' in m.group(0), "cod 15 trebuie D_23=RM: %s" % (m.group(0) if m else "randul lipseste")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d112_cod07_carantina_in_C2_prevenire(schema):
    """[cod07 carantina] apartine categoriei "prevenirea imbolnavirilor" (OUG 158/2005 art.20(3)): intra in
    agregatul Rd.2 (C2_24/C2_26) SI in sub-randul propriu C2_211-216. MUTATIE: scoaterea lui 07 din _r2 ->
    C2_2x nu contin carantina -> pica (era complet absenta din angajatorC2)."""
    import re
    from core import d112
    with schema.cursor() as cur:
        cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time) "
                    "OVERRIDING SYSTEM VALUE VALUES (1,'CAR','A','1900101410011','2025-01-01',5000,8,false)")
        cur.execute("INSERT INTO salariu_istoric (salariat_id,valabil_din,salariu_brut) VALUES (1,'2025-01-01',5000)")
        cur.execute("INSERT INTO concedii_medicale (salariat_id,an,luna,cod,zile,zile_ang,zile_fnuass,brut_ang,"
                    "brut_fnuass,baza,media_zilnica,serie,numar,data_acordare,data_inceput,data_sfarsit,loc_prescriere) "
                    "VALUES (1,2026,6,'07',8,0,8,0,1600,5000,200,'AB','1','2026-06-01','2026-06-01','2026-06-08',1)")
    xml, _ = d112.genereaza(schema, SCHEMA_T, 2026, 6)
    m = re.search(r'<angajatorC2[^>]*/>', xml)
    assert m, "angajatorC2 lipseste"
    c2 = dict(re.findall(r'(\w+)="([^"]*)"', m.group(0)))
    assert int(c2.get("C2_24", 0)) == 8 and int(c2.get("C2_26", 0)) == 1600, "carantina lipseste din agregatul Rd.2: %s" % m.group(0)[:200]
    assert "C2_211" in c2, "sub-randul carantina C2_211-216 lipseste"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d112_cod10_D13_aviz(schema):
    """[cod10 reducere 1/4 program] asiguratD cere D_13 = nr aviz medic expert (OUG 158/2005 art.19; regula
    DUK S102: daca D_9=10 atunci D_13 completat). MUTATIE: fara emisia D_13 pt cod 10 -> pica."""
    import re
    from core import d112
    with schema.cursor() as cur:
        cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time) "
                    "OVERRIDING SYSTEM VALUE VALUES (1,'RED','A','1900101410011','2025-01-01',5500,8,false)")
        cur.execute("INSERT INTO salariu_istoric (salariat_id,valabil_din,salariu_brut) VALUES (1,'2025-01-01',5500)")
        cur.execute("INSERT INTO concedii_medicale (salariat_id,an,luna,cod,zile,zile_ang,zile_fnuass,brut_ang,"
                    "brut_fnuass,baza,media_zilnica,serie,numar,data_acordare,data_inceput,data_sfarsit,loc_prescriere,cod_urgenta) "
                    "VALUES (1,2026,6,'10',20,0,20,0,3600,5500,262,'AB','1','2026-06-01','2026-06-01','2026-06-20',1,55501)")
    xml, _ = d112.genereaza(schema, SCHEMA_T, 2026, 6)
    m = re.search(r'<asiguratD[^>]*D_9="10"[^>]*/>', xml)
    assert m and 'D_13="55501"' in m.group(0), "cod 10 trebuie D_13 (nr aviz): %s" % (m.group(0) if m else "randul lipseste")
