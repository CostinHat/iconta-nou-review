# -*- coding: utf-8 -*-
"""GARD DEFECT-3 (08.08.2026): (A) frontend - un catch{} GOL care inghite un api.* transforma un 500 intr-o
STARE GOALA mincinoasa (ecranul minte plauzibil - mai grav decat un ecran care crapa). (B) backend -
perioada.e_confirmat primea `schema` dar folosea perioada_confirmata NECALIFICAT -> 500 pe ruta fara
search_path. Vezi E1E12_GASITE DEFECT-3."""
import re, glob, os
import pytest

_EMPTY_CATCH = re.compile(r"catch\s*(\([a-z_]*\))?\s*\{\s*\}")
_APICALL = re.compile(r"api\.(get|post|del)\(")
_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _fisiere_js():
    return (sorted(glob.glob(os.path.join(_RAD, "static/js/ecrane/*.js"))) +
            sorted(glob.glob(os.path.join(_RAD, "static/js/*.js"))))


def _count_catch_gol_langa_api():
    total = 0
    for f in _fisiere_js():
        src = open(f, encoding="utf-8").read()
        for m in _EMPTY_CATCH.finditer(src):
            pre = src[max(0, m.start() - 260):m.start()]
            if _APICALL.search(pre):
                total += 1
    return total


def test_ratchet_catch_gol_pe_api_nu_creste():
    """RATCHET: numarul de catch{} goale care inghit un api.* NU trebuie sa creasca. O cale noua = pica.
    Cele 4 cele mai grave (stat-plata/casa/jurnal/rip) reparate cu ramura de EROARE vizibila. Restul din
    harta (E1E12_GASITE) raman de reparat - reparandu-le, COBOARA BASELINE in acelasi commit."""
    BASELINE = 54   # 08.08.2026, dupa repararea celor 4 cele mai grave
    n = _count_catch_gol_langa_api()
    assert n <= BASELINE, (
        "catch{} gol NOU care inghite un api.* (%d > %d): un 500 devine stare goala mincinoasa. "
        "Randeaza o EROARE vizibila (flag in catch + ramura), nu tacere. Daca ai REPARAT unul, coboara BASELINE." % (n, BASELINE))


def test_ecranele_reparate_nu_regreseaza_la_catch_gol():
    """Cele 4 fetch-uri cele mai grave NU trebuie sa revina la catch gol: catch-ul seteaza un flag de
    eroare ([catch_vizibil_v1]) care randeaza un mesaj VIZIBIL, nu o stare goala."""
    firme = open(os.path.join(_RAD, "static/js/ecrane/firme.js"), encoding="utf-8").read()
    rip = open(os.path.join(_RAD, "static/js/ecrane/rip_ecran.js"), encoding="utf-8").read()
    for flag, unde in [("_eroareStat", firme), ("_eroareCasa", firme), ("_eroareJurnal", firme), ("_eroareRip", rip)]:
        assert flag in unde, "%s: fetch reparat a regresat la catch gol (DEFECT-3.2)" % flag
    # mesajul de eroare VIZIBIL e randat (proba ca o eroare de backend ajunge in UI, nu mascata)
    assert firme.count("Nu am putut încărca") >= 3, "ecranele reparate nu mai randeaza eroarea vizibila"
    assert "Nu am putut încărca" in rip, "RIP nu mai randeaza eroarea vizibila"


def test_backend_e_confirmat_calificat_pe_conn_fara_search_path():
    """[perioada_confirmata_v2_qualified] e_confirmat primeste `schema` si TREBUIE sa-l foloseasca
    (tabela calificata), ca sa mearga pe o conexiune fara search_path pe tenant (ruta stat-plata folosea
    db.get_conn() fara schema -> UndefinedTable -> 500). Gard de sursa (nu cere DB)."""
    per = open(os.path.join(_RAD, "core/perioada.py"), encoding="utf-8").read()
    assert "_tbl(schema)" in per, "perioada.py nu mai califica tabela cu schema (regresie DEFECT-3.1)"
    # cele 3 query-uri folosesc tabela calificata, nu literalul necalificat
    assert "FROM perioada_confirmata" not in per and "INTO perioada_confirmata" not in per, \
        "perioada.py inca are perioada_confirmata NECALIFICAT (revine 500 pe ruta fara search_path)"


def test_backend_rute_tenant_nu_apeleaza_helper_pe_conn_fara_search_path():
    """Rutele de payroll/documente care paseaza `schema` unui helper tenant deschid db.get_conn(schema)
    (search_path pe tenant), NU db.get_conn() gol. Ancora: marcajul [search_path_tenant_v1]."""
    main = open(os.path.join(_RAD, "main.py"), encoding="utf-8").read()
    assert main.count("search_path_tenant_v1") >= 5, \
        "rutele stat-plata/fluturas/pain001/balanta nu mai deschid get_conn(schema) (regresie DEFECT-3.1)"
