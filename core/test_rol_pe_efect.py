# -*- coding: utf-8 -*-
"""core/test_rol_pe_efect.py — GARD: rolul se cere după CE FACE ruta, nu după cum se numește.

Cerut de Costin, 26.08.2026, cu argumentul care decide: **măsurătoarea manuală s-a înșelat de trei
ori în trei zile**, de fiecare dată pe un PROXY — numele funcției (R33), numele grupului (R55),
calea fără metodă (R56). *„Un clichet pe nume […] e singurul care nu depinde de cine măsoară."*

Sonda trăiește în `core/scan_rol_pe_efect.py`, cu cele **șase moduri de eșec** scrise în antetul
ei, înaintea primei măsurători (interdicția 76). Aici stau doar aserțiunile — pe ce întoarce
instrumentul, nu pe text (clichetul 50).

CE FACE IMPOSIBIL
  1. o rută care scrie o înregistrare `validata` **direct** (produce evidență, sărind peste
     validare) și nu cere rol;
  2. o rută care scrie credențiale ale unui sistem extern și nu cere rol;
  3. schimbarea tăcută a mulțimii — aserțiunea e pe **mulțime**, nu pe cardinal, deci o inversare
     (una pierde rolul, alta îl câștigă) nu trece;
  4. dispariția sondei — anti-vacuu pe fiecare dintre cele două.

CE NU FACE, DECLARAT: nu spune dacă `admin_firma` e rolul POTRIVIT — spune că **există** un rol
acolo unde efectul îl cere. Alegerea rolului e decizia lui Costin (R42, R55, R56).
"""
import ast

import pytest

from core import scan_rol_pe_efect as scan

# Rute care scriu `validata` din PARAMETRU, nu literal (E6) — cu motivul.
PIN_STARE_DIN_PARAMETRU = {
    "/tenants/{tenant_id}/salarii-contare":
        "statusul e parametru de la R33 (25.08.2026), tocmai ca să poată fi asertat pe structură, "
        "nu pe textul SQL-ului. Citit la sursă: scrie ciornă, deci NU intră în mulțime",
}

# Mulțimea AȘTEPTATĂ a rutelor care produc evidență direct. Nu e sursa (aia e codul) — e martorul
# care face schimbarea vizibilă. E1 + E4.
ASTEPTAT_VALIDATA = {
    ("POST", "/tenants/{tenant_id}/amortizare"),
    ("POST", "/tenants/{tenant_id}/bonuri/{bon_id}/aproba"),
    ("POST", "/tenants/{tenant_id}/horeca/raport-z"),
}


@pytest.fixture(scope="module")
def m():
    r = scan.masoara()
    assert len(r["rute"]) >= 300, (
        "sonda vede doar %d rute — s-a rupt, nu s-a curățat codul" % len(r["rute"]))
    return r


def test_orice_ruta_care_scrie_evidenta_direct_cere_rol(m):
    """O rută care scrie `validata` produce EVIDENȚĂ sărind peste validare — deci schimbă ce
    datorează firma (criteriul lui Costin de la R42, extins la R55)."""
    fara = sorted(m["fara_rol_validata"])
    assert not fara, (
        "rute care scriu o înregistrare `validata` DIRECT, fără niciun rol (%d): %s\n"
        "Ori primesc rol, ori scriu ciornă și lasă poarta la validare." % (len(fara), fara))


def test_multimea_celor_care_produc_evidenta_nu_se_schimba_tacut(m):
    """E1 + E4: mulțimea se derivă din cod, dar e și așteptată. Un clichet pe număr ar trece la o
    inversare; aici se compară mulțimile."""
    gasit = {k for k in m["scriu_validata"] if k[1] not in PIN_STARE_DIN_PARAMETRU}
    assert gasit == ASTEPTAT_VALIDATA, (
        "mulțimea rutelor care produc evidență direct s-a schimbat.\n  intrate: %s\n  ieșite : %s\n"
        "Dacă e intenționat, se scrie aici — iar fiecare intrată trebuie să aibă rol."
        % (sorted(gasit - ASTEPTAT_VALIDATA) or "—", sorted(ASTEPTAT_VALIDATA - gasit) or "—"))


def test_orice_ruta_care_atinge_credentiale_cere_rol(m):
    """Costin, 26.08: *„Cheile de acces la sisteme externe nu sunt date de firmă — sunt
    credențiale."* R56: `admin_firma`, nu drept fin."""
    fara = sorted(m["fara_rol_credentiale"])
    assert not fara, ("rute care scriu credențiale ale unui sistem extern, fără rol (%d): %s"
                      % (len(fara), fara))


def test_ambele_sonde_gasesc_ceva(m):
    """Anti-vacuu: zero rute găsite ar face testele de mai sus adevărate despre o lume pe care
    sonda n-o vede."""
    assert len(m["scriu_validata"]) >= 3, "sonda de evidență: %s" % sorted(m["scriu_validata"])
    assert len(m["cu_credentiale"]) >= 3, "sonda de credențiale: %s" % sorted(m["cu_credentiale"])


# ── calibrare pe modurile PROPRII de eșec ────────────────────────────────────
def _f(src):
    return {n.name: n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef)}


def test_CALIBRARE_sonda_deosebeste_evidenta_de_ciorna():
    """Dacă sonda n-ar deosebi cele două stări, primul test ar fi verde pe orice cod. Se dau trei
    cazuri: unul pe care TREBUIE să-l vadă și două pe care NU trebuie."""
    f = _f('def a(x):\n'
           '    cur.execute(f"INSERT INTO {s}.inregistrari (d, status) VALUES (%s, \'validata\')")\n'
           'def b(x):\n'
           '    cur.execute(f"INSERT INTO {s}.inregistrari (d, status) VALUES (%s, \'ciorna\')")\n'
           'def c(x):\n'
           '    cur.execute(f"INSERT INTO {s}.inregistrari_linii (a,b) VALUES (%s, \'validata\')")\n')
    assert scan.scrie_validata(f["a"]) is True
    assert scan.scrie_validata(f["b"]) is False
    assert scan.scrie_validata(f["c"]) is False


def test_CALIBRARE_rolul_se_vede_si_din_CORP_nu_doar_din_decorator():
    """E2: un rol verificat în corp e tot un rol. Fără asta, gardul ar raporta «fără rol» pe rute
    care au unul — fals pozitiv care erodează încrederea în el."""
    f = _f('def a(ctx=Depends(cere_rol("admin_firma"))):\n    pass\n'
           'def b(ctx=None):\n'
           '    if ctx["rol"] != "superadmin":\n        raise HTTPException(403)\n'
           'def c(ctx=None):\n    pass\n')
    assert scan.roluri(f["a"]), "rolul din decorator nu se vede"
    assert scan.roluri(f["b"]) == {scan.ROL_DIN_CORP}, "rolul din corp nu se vede — E2 deschis"
    assert not scan.roluri(f["c"]), "sonda inventează un rol acolo unde nu e"


def test_CALIBRARE_un_rol_calculat_se_NUMESTE_nu_se_inghite():
    """E3: `cere_rol(x)` cu rol dintr-o variabilă nu se poate citi static. Nu se trece drept «fără
    rol» (fals pozitiv) și nici drept rol cunoscut (fals negativ) — se numește."""
    f = _f('def a(ctx=Depends(cere_rol(ROL))):\n    pass\n')
    assert scan.roluri(f["a"]) == {scan.ROL_CALCULAT}


def test_CALIBRARE_sonda_de_credentiale_nu_prinde_o_simpla_CITIRE():
    """Un `SELECT` pe o tabelă de credențiale nu e o scriere. Fără direcția asta, gardul ar cere
    rol pe rute care doar citesc — și ar fi relaxat de cineva, pe drept."""
    f = _f('def a(x):\n    cur.execute("SELECT 1 FROM reges_chei")\n'
           'def b(x):\n    cur.execute("INSERT INTO reges_chei (k) VALUES (%s)")\n')
    assert scan.atinge_credentiale(f["a"]) is False
    assert scan.atinge_credentiale(f["b"]) is True


def test_pinul_starii_din_parametru_e_real_si_motivat(m):
    """E6: cazul cunoscut e pinat, dar pinul nu poate deveni o listă de ignorat."""
    cai = {c for (_metoda, c) in m["rute"]}
    for cale, motiv in PIN_STARE_DIN_PARAMETRU.items():
        assert cale in cai, "%s nu mai e rută — scoate-o din pin" % cale
        assert len(motiv) > 80, "%s e în pin fără motiv scris" % cale
