# -*- coding: utf-8 -*-
"""frontend_test/e2e/e2e_baza_test.py — baza de test repetabilă (comanda 16.0, pct.2h). Nu folosește browser și NU rulează sub `scripts/e2e_poarta.py`
(restaurarea ar rupe testele vecine): se rulează direct, `python -m pytest frontend_test/e2e/e2e_baza_test.py`, pe iconta_test.
1. se creează o chitanță pe iconta_test (rând în baza firmei F1 + PDF-ul pe disc), se restaurează, a doua rulare nu o găsește nici în bază, nici pe disc;
2. amprenta (hash pe date fără tabelele „recalculate”, secvențe, inventarul fișierelor generate) luată după restaurarea 1 și după restaurarea 2, fără nicio
   rulare între ele — identice; ieșirea se salvează în docs/dovezi/16_0/."""
import os
import subprocess

import psycopg2

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BAZA_SH = os.path.join(RAD, "scripts", "baza_test.sh")
TEMP = os.environ.get("E2E_TEMP", "/tmp/e2e_poarta")
PDF = os.path.join(TEMP, "fisiere", "chitanta_proba_baza_test.pdf")
DOVEZI = os.path.join(RAD, "docs", "dovezi", "16_0")


def _env():
    env = dict(os.environ)
    for ln in open(os.path.expanduser("~/.iconta/test.env"), encoding="utf-8"):
        ln = ln.strip()
        if "=" in ln and not ln.startswith("#"):
            k, v = ln.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def _sh(*a):
    r = subprocess.run(["sh", BAZA_SH, *a], cwd=RAD, env=_env(), capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    if a and a[0] == "restaureaza":     # restaurarea termină conexiunile pool-ului fixturilor: pool nou, ca teardown-ul conftest să nu pice
        from core import db
        db._pool = None
        db.init_pool()
    return r.stdout


def _chitante_proba():
    with psycopg2.connect(_env()["DATABASE_URL"]) as c, c.cursor() as cur:
        cur.execute("SELECT count(*) FROM tenant_9049.chitante WHERE serie = 'PROBA16'")
        return cur.fetchone()[0]


def test_chitanta_creata_dispare_dupa_restaurare_in_baza_si_pe_disc():
    _sh("restaureaza", "--fara-lucrator")
    with psycopg2.connect(_env()["DATABASE_URL"]) as c, c.cursor() as cur:
        cur.execute("INSERT INTO tenant_9049.chitante (serie, numar, data, client_nume, suma) VALUES ('PROBA16', 1, '2026-11-03', 'Client Test SRL', 500)")
    os.makedirs(os.path.dirname(PDF), exist_ok=True)
    open(PDF, "wb").write(b"%PDF-1.4 chitanta de proba\n")
    assert _chitante_proba() == 1 and os.path.exists(PDF)
    _sh("restaureaza", "--fara-lucrator")
    assert _chitante_proba() == 0, "chitanța a rămas în bază după restaurare"
    assert not os.path.exists(PDF), "PDF-ul chitanței a rămas pe disc după restaurare"


def test_amprenta_identica_dupa_doua_restaurari_consecutive():
    _sh("restaureaza", "--fara-lucrator")
    a = _sh("stare")
    _sh("restaureaza", "--fara-lucrator")
    b = _sh("stare")
    os.makedirs(DOVEZI, exist_ok=True)
    open(os.path.join(DOVEZI, "amprenta_restaurarea_1.txt"), "w", encoding="utf-8").write(a)
    open(os.path.join(DOVEZI, "amprenta_restaurarea_2.txt"), "w", encoding="utf-8").write(b)
    assert a == b, "amprentele diferă între restaurarea 1 și 2 (vezi docs/dovezi/16_0/)"


def test_preconditiile_f017_dupa_testul_10_al_lantului_se_inregistreaza():
    """Rulat în aceeași sesiune cu testele 00–10 ale lanțului pilot (`--doar=e2e_pilot_luna.py::test_pilot_00…` … `::test_pilot_10…` apoi acest test): scrie în
    <E2E_CAPTURI>/verifica_dupa_testul_10.txt (apoi copiat în docs/dovezi/16_0/) rezultatul lui `baza_test.sh verifica` (țin / nu țin la poziția 11). Nu decide nimic: decizia e a lui 16.2."""
    r = subprocess.run(["sh", BAZA_SH, "verifica"], cwd=RAD, env=_env(), capture_output=True, text=True)
    iesire = os.environ.get("E2E_CAPTURI", DOVEZI)      # sub e2e_poarta.py RAD e copia exportată: rezultatul se scrie în directorul capturilor
    os.makedirs(iesire, exist_ok=True)
    open(os.path.join(iesire, "verifica_dupa_testul_10.txt"), "w", encoding="utf-8").write(r.stdout + "\nieșire verifica: %d (0 = țin, 1 = nu țin)\n" % r.returncode)
