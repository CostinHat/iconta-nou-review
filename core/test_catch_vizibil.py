# -*- coding: utf-8 -*-
"""GARD DEFECT-3 (08.08.2026): (A) frontend - un catch{} GOL care inghite un api.* transforma un 500 intr-o
STARE GOALA mincinoasa (ecranul minte plauzibil - mai grav decat un ecran care crapa). (B) backend -
perioada.e_confirmat primea `schema` dar folosea perioada_confirmata NECALIFICAT -> 500 pe ruta fara
search_path. Vezi E1E12_GASITE DEFECT-3. DS cap.6: eroarea de load = ecran-nota (distinct), NU .stare-goala (gol)."""
import re, glob, os
import pytest

_EMPTY_CATCH = re.compile(r"catch\s*(\([a-z_]*\))?\s*\{\s*\}")
_APICALL = re.compile(r"api\.(get|post|del)\(")
_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cele 16 fetch-uri PERICULOASE reparate (E1E12_GASITE 08.08). woo EXCLUS (backend intoarce mereu 200 -> catch-ul
# frontend nu vede un 500; datorie de backend, raportata separat). Fiecare fragment NU trebuie sa fie inghitit
# de un catch{} gol (= randa o stare goala mincinoasa la 500).
_URL_PERICULOASE = [
    "stat-plata", "casa/registru", "rip/registru", "/jurnal?",              # cele 4 (ieri, flag _eroare)
    "facturi-primite", "facturi?an=", "facturi-recurente", "/solicitari",   # cele 12 (azi, ecran-nota)
    "/retete", "stocuri/nir", "centre-cost", "contracte/sabloane",
    "etransport/trimiteri", "/concedii", "echipa/centralizator", "cabinet/api-chei",
]


def _fisiere_js():
    return (sorted(glob.glob(os.path.join(_RAD, "static/js/ecrane/*.js"))) +
            sorted(glob.glob(os.path.join(_RAD, "static/js/*.js"))))


def _count_catch_gol_langa_api():
    total = 0
    for f in _fisiere_js():
        src = open(f, encoding="utf-8").read()
        for m in _EMPTY_CATCH.finditer(src):
            if _APICALL.search(src[max(0, m.start() - 260):m.start()]):
                total += 1
    return total


def test_ratchet_catch_gol_pe_api_nu_creste():
    """RATCHET: numarul de catch{} goale care inghit un api.* NU trebuie sa creasca. O cale noua = pica.
    Cele 16 periculoase reparate (4 ieri + 12 azi); au ramas doar catch-uri BENIGNE (mark-read, contoare,
    selectoare de formular, migrare wizard) + woo. Baseline coborat 54->41 pe masura ce s-au reparat."""
    BASELINE = 41   # 08.08.2026, dupa repararea celor 12 periculoase ramase
    n = _count_catch_gol_langa_api()
    assert n <= BASELINE, (
        "catch{} gol NOU care inghite un api.* (%d > %d): un 500 devine stare goala mincinoasa. "
        "Randeaza EROARE vizibila (ecran-nota / arataMesaj), nu tacere. Daca ai REPARAT unul, coboara BASELINE." % (n, BASELINE))


def test_niciun_fetch_periculos_nu_e_inghitit_tacut():
    """ZERO PERICULOASE: niciunul dintre cele 16 fetch-uri de continuut primar nu e urmat imediat de un catch{}
    gol. Un 500 pe ele trebuie sa produca eroare vizibila, nu stare goala. woo exclus (backend intoarce 200)."""
    src_all = {os.path.basename(f): open(f, encoding="utf-8").read() for f in _fisiere_js()}
    vinovati = []
    for base, src in src_all.items():
        for m in _APICALL.finditer(src):          # ancora pe apelul api.get/post/del
            seg = src[m.start():m.start() + 300]
            url_part = seg[:120]                   # URL-ul e imediat dupa api.get(
            matched = next((u for u in _URL_PERICULOASE if u in url_part), None)
            if not matched:
                continue
            any_m = re.search(r"catch\s*(\([a-z_]*\))?\s*\{", seg)
            empty_m = _EMPTY_CATCH.search(seg)
            if any_m and empty_m and any_m.start() == empty_m.start():  # PRIMUL catch = gol
                vinovati.append("%s: %s" % (base, matched))
    assert not vinovati, "fetch periculos inghitit de catch{} gol (500 -> stare goala mincinoasa): %s" % vinovati


def test_ecranele_reparate_randeaza_eroare_vizibila():
    """Cele 4 (ieri, flag) + cele 12 (azi, ecran-nota) randeaza EROARE VIZIBILA, nu stare goala."""
    firme = open(os.path.join(_RAD, "static/js/ecrane/firme.js"), encoding="utf-8").read()
    rip = open(os.path.join(_RAD, "static/js/ecrane/rip_ecran.js"), encoding="utf-8").read()
    # cele 4 unificate (08.08) la CANONICUL ecran-nota: mesajul canonic pe fiecare
    for txt in ("statul de plată", "registrul de casă", "jurnalul"):
        assert ("Nu am putut încărca " + txt) in firme, "firme.js: '%s' a regresat" % txt
    assert "Nu am putut încărca registrul" in rip, "RIP a regresat"
    # O SINGURA SURSA de stil (DS): stilul vechi (.stare-goala colorat rosu pt eroare) NU mai exista
    assert 'stare-goala" style="color:var(--rosu)' not in firme and 'stare-goala" style="color:var(--rosu)' not in rip,         "stil de eroare vechi (.stare-goala rosu) - unifica la ecran-nota"
    for base in ("facturi_ecran.js", "etransport_ecran.js", "flux_concediu.js", "setari.js", "cabinet.js", "woo_ecran.js"):
        s2 = open(os.path.join(_RAD, "static/js/ecrane", base), encoding="utf-8").read()
        assert "Nu am putut încărca" in s2, "%s nu mai randeaza eroarea de load" % base


def test_backend_e_confirmat_calificat_pe_conn_fara_search_path():
    """[perioada_confirmata_v2_qualified] e_confirmat califica tabela cu schema (merge pe conn fara search_path)."""
    per = open(os.path.join(_RAD, "core/perioada.py"), encoding="utf-8").read()
    assert "_tbl(schema)" in per, "perioada.py nu mai califica tabela cu schema (regresie DEFECT-3.1)"
    assert "FROM perioada_confirmata" not in per and "INTO perioada_confirmata" not in per, \
        "perioada.py inca are perioada_confirmata NECALIFICAT"


def test_backend_rute_tenant_deschid_get_conn_schema():
    """Rutele payroll/documente deschid db.get_conn(schema) (marcaj search_path_tenant_v1), nu get_conn() gol."""
    main = open(os.path.join(_RAD, "main.py"), encoding="utf-8").read()
    assert main.count("search_path_tenant_v1") >= 5, "regresie DEFECT-3.1 (rute fara search_path pe tenant)"
