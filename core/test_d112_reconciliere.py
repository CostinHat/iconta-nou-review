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
                            "OVERRIDING SYSTEM VALUE VALUES (2,'SIMPLU','B','1900101410012','2025-01-01',8000,8,false)")
                # 1 salariat la MINIM (4050) -> facilitate -> CAZ NESIMPLU
                cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time) "
                            "OVERRIDING SYSTEM VALUE VALUES (3,'MINIM','C','1900101410013','2025-01-01',4050,8,false)")
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
    assert set(rap["reconciliati"]) == {1, 2}, rap["reconciliati"]
    assert 3 in rap["sarite"], "salariatul la minim (facilitate) trebuia SARIT: %s" % rap["sarite"]
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
def test_caz_nesimplu_facilitate_e_sarit_nu_alarma(conn_recon):
    """Salariatul 3 (la minim, cu facilitate) are cas care NU e brut x 25%. Daca ar fi comparat,
    ar da divergenta falsa. Trebuie SARIT (NEACOPERIT), nu confruntat."""
    _prof, sal = _d112.pull(conn_recon, _SCHEMA, 2026, 6)
    # ii dam salariatului 3 un cas aberant: NU trebuie sa alarmeze (e sarit din start)
    for s in sal:
        if s["id"] == 3:
            s["cas"] = 123456
    rap = reconciliaza(conn_recon, _SCHEMA, 2026, 6, sal)
    assert 3 in rap["sarite"] and 3 not in rap["reconciliati"]
    assert all(d["salariat"] != 3 for d in rap["divergente"]), rap["divergente"]
    assert all(s["salariat"] != 3 for s in rap["suspecte"]), rap["suspecte"]  # facilitate = legitim, NU suspect


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
    assert "brut LIPSA" in str(ei.value) and "SUSPECTE" in str(ei.value)


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
