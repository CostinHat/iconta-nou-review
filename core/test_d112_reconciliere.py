# -*- coding: utf-8 -*-
"""
core/test_d112_reconciliere.py — gardul A DOUA CALE D112 (05.08.2026, campanie pas 3/6).

D112 e cel mai expus la tautologie. Apara:
  - NON-TAUTOLOGIA pe lantul de import TRANZITIV: calea 2 nu ajunge la calcul_salariu /
    salarizare / d112 / salariu_istoric nici indirect.
  - reconcilierea PICA pe bug de contributie in CAZUL SIMPLU (MUTATIE: cas / cass gresit).
  - pe date corecte NU alarma falsa (proba functionala pe schema efemera).
  - CAZUL NESIMPLU (angajat la salariul minim = facilitate) e SARIT, nu comparat -> nicio
    alarma falsa chiar daca valoarea lui difera.
"""
import io
import os
import ast
import pytest

from core import d112 as _d112
from core import d112_reconciliere as _rec
from core.d112_reconciliere import reconciliaza, verifica_reconciliere, ReconciliereD112
from core import perioada as _per


# ============================================================
#  1. NON-TAUTOLOGIE pe lantul de import TRANZITIV.
# ============================================================
def _core_imports_din_fisier(path):
    mods = set()
    tree = ast.parse(io.open(path, encoding="utf-8").read())
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module and n.module.startswith("core"):
            mods.add(n.module)
            if n.module == "core":
                for a in n.names:
                    mods.add("core." + a.name)
        elif isinstance(n, ast.Import):
            for a in n.names:
                if a.name.startswith("core"):
                    mods.add(a.name)
    return mods


def test_non_tautologie_lant_tranzitiv_nu_atinge_salarizarea():
    """Inchiderea TRANZITIVA a importurilor core.* pornind din d112_reconciliere NU trebuie sa
    contina calcul_salariu / salarizare / d112 / salariu_istoric (altfel calea 2 ar imparti,
    fie si indirect, agregarea generatorului = tautologie)."""
    rad = os.path.dirname(os.path.dirname(_rec.__file__))   # radacina repo (parinte de core/)
    vazut, coada = set(), [_rec.__file__]
    inchidere = set()
    while coada:
        f = coada.pop()
        if f in vazut:
            continue
        vazut.add(f)
        for mod in _core_imports_din_fisier(f):
            inchidere.add(mod)
            cale = os.path.join(rad, mod.replace(".", os.sep) + ".py")
            if os.path.exists(cale):
                coada.append(cale)
    for interzis in ("core.salarizare", "core.d112", "core.salariu_istoric"):
        assert interzis not in inchidere, (
            "NON-TAUTOLOGIE (tranzitiv) incalcata: calea 2 ajunge la %s. Inchidere: %s"
            % (interzis, sorted(inchidere)))
    # si pe nume folosite direct:
    folosite = {n.id for n in ast.walk(ast.parse(io.open(_rec.__file__, encoding="utf-8").read()))
                if isinstance(n, ast.Name)}
    for interzis in ("calcul_salariu", "deducere_personala", "taxe_cm"):
        assert interzis not in folosite, "calea 2 foloseste '%s'" % interzis


# ============================================================
#  Fixtura DB: firma + 2 salariati SIMPLI (brut > salariu minim, luna intreaga, fara CM/tichete/
#  part-time) + 1 salariat la MINIM (facilitate -> caz nesimplu, sarit).
# ============================================================
from core import db as _db, tenant_provisioning as _tp
_SCHEMA = "test_d112_recon"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn_recon():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,platitor_tva,tip_decont) "
                            "VALUES (1,'PROBA SRL','14399840','Str 1','Buc','B','6202',true,'L')")
                # 2 salariati SIMPLI (brut 6000 si 8000, peste minimul 2026 de 4050, luna intreaga)
                cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time) "
                            "OVERRIDING SYSTEM VALUE VALUES (1,'SIMPLU','A','1900101410011','2025-01-01',6000,8,false)")
                cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time) "
                            "OVERRIDING SYSTEM VALUE VALUES (2,'SIMPLU','B','1900101410028','2025-01-01',8000,8,false)")
                # 1 salariat la MINIM (4050) -> facilitate -> CAZ NESIMPLU
                cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time) "
                            "OVERRIDING SYSTEM VALUE VALUES (3,'MINIM','C','1900101410036','2025-01-01',4050,8,false)")
                cur.execute("INSERT INTO salariu_istoric (salariat_id,valabil_din,salariu_brut) "
                            "VALUES (1,'2025-01-01',6000),(2,'2025-01-01',8000),(3,'2025-01-01',4050)")
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_reconciliere_curata_si_genereaza_trece(conn_recon):
    """PROBA FUNCTIONALA: genereaza() (cu POARTA wired) trece; reconciliaza NU raporteaza divergente;
    cei 2 simpli sunt reconciliati, cel la minim e sarit."""
    xml, _av = _d112.genereaza(conn_recon, _SCHEMA, 2026, 6)   # daca gardul da fals-pozitiv -> AICI crapa
    _prof, sal = _d112.pull(conn_recon, _SCHEMA, 2026, 6)
    # calea 1 (generator): CAS 25% / CASS 10% pe brut (caz simplu)
    g = {s["id"]: s for s in sal}
    assert (int(g[1]["cas"]), int(g[1]["cass"])) == (1500, 600)   # 6000 x 25% / 10%
    assert (int(g[2]["cas"]), int(g[2]["cass"])) == (2000, 800)   # 8000 x 25% / 10%
    rap = reconciliaza(conn_recon, _SCHEMA, 2026, 6, sal)
    assert rap["divergente"] == [], "alarma falsa: %s" % rap["divergente"]
    # sub-caz 1a: salariatul 3 (la minim 4050, toata luna, full-time) e acum RECONCILIAT cu facilitate, nu sarit
    assert set(rap["reconciliati"]) == {1, 2, 3}, rap["reconciliati"]
    # generatorul tine cas la 2 zecimale (937.50); D112 il EMITE ca 938 (_d112int, half-up); calea 2 confrunta
    # valoarea EMISA (rotunjita). baza=4050-300=3750, cas=3750x25%=937.50->938, cass=375
    assert (float(g[3]["cas"]), float(g[3]["cass"])) == (937.5, 375.0), (g[3]["cas"], g[3]["cass"])
    assert "<angajator" in xml


# ---- MUTATIE: bug de contributie in cazul simplu -> reconcilierea PICA ----

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_mutatie_cas_gresit_pica(conn_recon):
    _prof, sal = _d112.pull(conn_recon, _SCHEMA, 2026, 6)
    for s in sal:
        if s["id"] == 1:
            s["cas"] = 9999   # <- mutatie: CAS gresit pe un salariat simplu
    with pytest.raises(ReconciliereD112) as ei:
        verifica_reconciliere(conn_recon, _SCHEMA, 2026, 6, sal)
    msg = str(ei.value)
    assert "salariat 1 cas" in msg and "generator=9999" in msg and "cale2=1500" in msg, msg


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_mutatie_cass_gresit_pica(conn_recon):
    _prof, sal = _d112.pull(conn_recon, _SCHEMA, 2026, 6)
    for s in sal:
        if s["id"] == 2:
            s["cass"] = 1   # <- mutatie: CASS gresit
    with pytest.raises(ReconciliereD112) as ei:
        verifica_reconciliere(conn_recon, _SCHEMA, 2026, 6, sal)
    msg = str(ei.value)
    assert "salariat 2 cass" in msg and "generator=1" in msg and "cale2=800" in msg, msg


# ============================================================
#  ACOPERIRE: cazul NESIMPLU (facilitate la minim) e SARIT, nu comparat -> fara alarma falsa.
# ============================================================
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_facilitate_la_minim_reconciliata_si_mutatie_pica(conn_recon):
    """SUB-CAZ 1a: salariatul 3 (la minim 4050, toata luna, full-time) e RECONCILIAT cu facilitate
    (baza = sm - fac). Un cas gresit pe el PICA acum (inainte era sarit)."""
    _prof, sal = _d112.pull(conn_recon, _SCHEMA, 2026, 6)
    g = {s["id"]: s for s in sal}
    assert (float(g[3]["cas"]), float(g[3]["cass"])) == (937.5, 375.0)   # generator 2 zec; emis 938 (half-up)
    rap = reconciliaza(conn_recon, _SCHEMA, 2026, 6, sal)
    assert 3 in rap["reconciliati"] and rap["divergente"] == []
    for s in sal:
        if s["id"] == 3:
            s["cas"] = 999   # <- mutatie: cas gresit pe facilitate
    with pytest.raises(ReconciliereD112) as ei:
        verifica_reconciliere(conn_recon, _SCHEMA, 2026, 6, sal)
    assert "salariat 3 cas: generator=999 vs cale2=938" in str(ei.value), str(ei.value)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_facilitate_proratata_ramane_sarita(conn_recon):
    """Facilitatea PRORATATA (schimbare de salariu IN luna) ramane NEACOPERITA (sub-caz ulterior) -
    salariatul cade in sarite, nu se confrunta cu formula full-facilitate."""
    with conn_recon.cursor() as cur:
        cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time) "
                    "OVERRIDING SYSTEM VALUE VALUES (6,'PRORATA','F','1900101410016','2025-01-01',4050,8,false)")
        # schimbare de salariu IN luna 6 (valabil_din 2026-06-16) -> facilitate proratata
        cur.execute("INSERT INTO salariu_istoric (salariat_id,valabil_din,salariu_brut) VALUES (6,'2025-01-01',4050),(6,'2026-06-16',4050)")
    _prof, sal = _d112.pull(conn_recon, _SCHEMA, 2026, 6)
    rap = reconciliaza(conn_recon, _SCHEMA, 2026, 6, sal)
    assert 6 in rap["sarite"] and 6 not in rap["reconciliati"], rap


# ============================================================
#  SKIP-SUSPECT (date corupte) vs SKIP-LEGITIM (complexitate): gardul VORBESTE pe date stricate.
# ============================================================
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_skip_suspect_brut_lipsa_e_semnalat_nu_tacut(conn_recon):
    """Angajat EMIS dar cu brut LIPSA (fara istoric, salariu_brut NULL) -> generatorul emite pe 0.
    NU trebuie sarit tacut: e skip-SUSPECT, semnalat (null base = eroare pana la proba contrarie)."""
    with conn_recon.cursor() as cur:
        cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time) "
                    "OVERRIDING SYSTEM VALUE VALUES (4,'FARABRUT','D','1900101410014','2025-01-01',NULL,8,false)")
    sal = [{"id": 4, "cas": 0, "cass": 0}]   # generatorul l-a emis pe 0
    rap = reconciliaza(conn_recon, _SCHEMA, 2026, 6, sal)
    assert any(s["salariat"] == 4 for s in rap["suspecte"]), rap
    assert 4 not in rap["sarite"] and 4 not in rap["reconciliati"]
    with pytest.raises(ReconciliereD112) as ei:
        verifica_reconciliere(conn_recon, _SCHEMA, 2026, 6, sal)
    assert "salariul brut lipsește" in str(ei.value) and "SUSPECTE" in str(ei.value)  # diacritice cap.6 (mesaj afisat)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_skip_suspect_brut_sub_minim_e_semnalat(conn_recon):
    """Angajat full-time luna intreaga cu brut SUB minimul legal -> date probabil corupte -> semnalat."""
    with conn_recon.cursor() as cur:
        cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time) "
                    "OVERRIDING SYSTEM VALUE VALUES (5,'SUBMINIM','E','1900101410015','2025-01-01',3000,8,false)")
        cur.execute("INSERT INTO salariu_istoric (salariat_id,valabil_din,salariu_brut) VALUES (5,'2025-01-01',3000)")
    sal = [{"id": 5, "cas": 750, "cass": 300}]   # 3000 x 25/10 - dar brutul e sub minim
    rap = reconciliaza(conn_recon, _SCHEMA, 2026, 6, sal)
    assert any(s["salariat"] == 5 for s in rap["suspecte"]), rap
    assert 5 not in rap["reconciliati"] and 5 not in rap["sarite"]
    with pytest.raises(ReconciliereD112) as ei:
        verifica_reconciliere(conn_recon, _SCHEMA, 2026, 6, sal)
    assert "SUB salariul minim" in str(ei.value)


# ============================================================
#  SUB-CAZ 1b (05.08.2026): TICHETE DE MASA peste minim -> CAS reconciliat, CASS numit-afara.
# ============================================================
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_tichete_masa_cas_reconciliat_cass_ramane_afara(conn_recon):
    """Angajat PESTE minim cu tichete de masa: pull EMITE cass = brut x cota_cass + cass_tichete
    (d112.py:239). Calea 2 reconciliaza DOAR CAS (tichetele nu ating baza CAS); CASS ramane numit-afara.
    PROBA: (a) pe date corecte CAS reconciliat, fara alarma falsa; (b) MUTATIE pe cas PICA; (c) MUTATIE
    pe cass NU pica (limita CASS-afara e reala, nu o omisiune tacuta)."""
    with conn_recon.cursor() as cur:
        cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time,tichet_masa_valoare) "
                    "OVERRIDING SYSTEM VALUE VALUES (7,'TICHETE','G','1900101410017','2025-01-01',6000,8,false,40)")
        cur.execute("INSERT INTO salariu_istoric (salariat_id,valabil_din,salariu_brut) VALUES (7,'2025-01-01',6000)")
    # tichetele de masa cer pontaj CONFIRMAT (d112.py:472, HG 1045/2018 art.10(3)) - altfel pull ridica PerioadaNeconfirmata
    _per.confirma(conn_recon, _SCHEMA, 2026, 6, "pontaj", 1)
    _prof, sal = _d112.pull(conn_recon, _SCHEMA, 2026, 6)
    g = {s["id"]: s for s in sal}
    assert int(g[7]["cas"]) == 1500, g[7]["cas"]                         # 6000 x 25% - neatins de tichete (EMIS = reconciliabil)
    # s["cass"] pastreaza DOAR CASS salarial (600); cass_tichete e camp SEPARAT. CASS-ul EMIS la ANAF = cass + cass_tichete
    # (d112.py:239 face cass += cass_tichete la build). Reconcilierea lasa CASS afara: nu poate recalcula cass_tichete
    # fara motorul de tichete (nominal x zile-pontaj x cota_cass) = tautologie + dependenta de pontaj.
    assert float(g[7]["cass"]) == 600.0, g[7]["cass"]                    # CASS salarial = 6000 x 10% (component, NU emisul; nu se confrunta)
    assert float(g[7]["cass_tichete"]) > 0, ("cass_tichete=0 -> limita CASS-afara ar fi vacua: %s" % g[7]["cass_tichete"])
    # (a) date corecte: 7 e reconciliat pe CAS DOAR, fara divergenta; nu e in reconciliati (complet) nici sarit
    rap = reconciliaza(conn_recon, _SCHEMA, 2026, 6, sal)
    assert rap["divergente"] == [], "alarma falsa: %s" % rap["divergente"]
    assert 7 in rap["reconciliati_cas_doar"], rap
    assert 7 not in rap["reconciliati"] and 7 not in rap["sarite"], rap
    # (b) MUTATIE pe cas -> hard-block care numeste salariatul si ambele valori
    for s in sal:
        if s["id"] == 7:
            s["cas"] = 9999
    with pytest.raises(ReconciliereD112) as ei:
        verifica_reconciliere(conn_recon, _SCHEMA, 2026, 6, sal)
    assert "salariat 7 cas" in str(ei.value) and "generator=9999" in str(ei.value) and "cale2=1500" in str(ei.value), str(ei.value)
    # (c) MUTATIE pe cass -> NU pica (CASS numit-afara pentru tichete): limita declarata, nu omisiune tacuta
    _prof, sal2 = _d112.pull(conn_recon, _SCHEMA, 2026, 6)
    for s in sal2:
        if s["id"] == 7:
            s["cass"] = 1   # valoare absurda pe CASS
    rap2 = reconciliaza(conn_recon, _SCHEMA, 2026, 6, sal2)
    assert all(d["salariat"] != 7 for d in rap2["divergente"]), (
        "CASS pe tichete NU trebuie confruntata (limita 1b) - dar a produs divergenta: %s" % rap2["divergente"])
    verifica_reconciliere(conn_recon, _SCHEMA, 2026, 6, sal2)   # nu ridica


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_tichete_masa_la_minim_ramane_sarit(conn_recon):
    """Combo facilitate(la minim)+tichete = sub-caz ulterior: angajatul la minim CU tichete de masa
    ramane SARIT (nu se confrunta nici pe CAS), pana la un sub-caz care il acopera explicit."""
    with conn_recon.cursor() as cur:
        cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time,tichet_masa_valoare) "
                    "OVERRIDING SYSTEM VALUE VALUES (8,'MINTICH','H','1900101410018','2025-01-01',4050,8,false,40)")
        cur.execute("INSERT INTO salariu_istoric (salariat_id,valabil_din,salariu_brut) VALUES (8,'2025-01-01',4050)")
    _per.confirma(conn_recon, _SCHEMA, 2026, 6, "pontaj", 1)
    _prof, sal = _d112.pull(conn_recon, _SCHEMA, 2026, 6)
    rap = reconciliaza(conn_recon, _SCHEMA, 2026, 6, sal)
    assert 8 in rap["sarite"], rap
    assert 8 not in rap["reconciliati"] and 8 not in rap["reconciliati_cas_doar"], rap


# ============================================================
#  SUB-CAZ 1c-PT (05.08.2026): PART-TIME suprataxare art.146(5^6) -> CAS+CASS pe baza ridicata la min.
# ============================================================
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_part_time_sub_prag_reconciliat_pe_baza_ridicata(conn_recon):
    """Part-time cu brut SUB nivelul minim (sm-facilitate): D112 emite CAS/CASS pe baza RIDICATA la prag
    (cas_min_pt/cass_min_pt; diferenta fata de retinut = pe angajator, B4_8D/B4_6D). calea 2 reconciliaza
    EMISUL vs max(brut, salariul minim INTEGRAL) x cota - floor-ul part-time = salariul minim, NU sm-facilitate
    (facilitatea e doar norma intreaga, art.LXVI; fix 06.08.2026). MUTATIE pe cas_min_pt PICA."""
    with conn_recon.cursor() as cur:
        cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time) "
                    "OVERRIDING SYSTEM VALUE VALUES (10,'PTSUB','I','1900101410020','2025-01-01',2025,4,true)")
        cur.execute("INSERT INTO salariu_istoric (salariat_id,valabil_din,salariu_brut) VALUES (10,'2025-01-01',2025)")
    _prof, sal = _d112.pull(conn_recon, _SCHEMA, 2026, 6)
    g = {s["id"]: s for s in sal}
    assert g[10]["pt_aplica"] is True, g[10]
    assert (int(g[10]["cas_min_pt"]), int(g[10]["cass_min_pt"])) == (1013, 405), g[10]  # 4050 x 25% / 10% (half-up): floor = salariul minim INTEGRAL (art.146(5^6)), NU sm-facilitate
    rap = reconciliaza(conn_recon, _SCHEMA, 2026, 6, sal)
    assert rap["divergente"] == [], "alarma falsa: %s" % rap["divergente"]
    assert 10 in rap["reconciliati"] and 10 not in rap["sarite"], rap
    for s in sal:
        if s["id"] == 10:
            s["cas_min_pt"] = 9999   # <- mutatie: baza minima part-time gresita pe CAS
    with pytest.raises(ReconciliereD112) as ei:
        verifica_reconciliere(conn_recon, _SCHEMA, 2026, 6, sal)
    assert "salariat 10 cas" in str(ei.value) and "generator=9999" in str(ei.value) and "cale2=1013" in str(ei.value), str(ei.value)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_part_time_peste_prag_reconciliat_pe_brut(conn_recon):
    """Part-time cu brut PESTE nivelul minim: fara suprataxare (pt_aplica False), CAS/CASS pe brut (part-time
    n-are facilitate). max(brut, prag)=brut -> reconciliat pe brut x cota. MUTATIE pe cas PICA."""
    with conn_recon.cursor() as cur:
        cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time) "
                    "OVERRIDING SYSTEM VALUE VALUES (11,'PTPESTE','J','1900101410021','2025-01-01',8000,4,true)")
        cur.execute("INSERT INTO salariu_istoric (salariat_id,valabil_din,salariu_brut) VALUES (11,'2025-01-01',8000)")
    _prof, sal = _d112.pull(conn_recon, _SCHEMA, 2026, 6)
    g = {s["id"]: s for s in sal}
    assert g[11]["pt_aplica"] is False, g[11]
    assert (int(g[11]["cas"]), int(g[11]["cass"])) == (2000, 800), g[11]   # 8000 x 25% / 10%
    rap = reconciliaza(conn_recon, _SCHEMA, 2026, 6, sal)
    assert rap["divergente"] == [], "alarma falsa: %s" % rap["divergente"]
    assert 11 in rap["reconciliati"] and 11 not in rap["sarite"], rap
    for s in sal:
        if s["id"] == 11:
            s["cas"] = 9999
    with pytest.raises(ReconciliereD112) as ei:
        verifica_reconciliere(conn_recon, _SCHEMA, 2026, 6, sal)
    assert "salariat 11 cas" in str(ei.value) and "cale2=2000" in str(ei.value), str(ei.value)
