# -*- coding: utf-8 -*-
"""[lotul 11, comanda Costin 11.1, verbatim în DECIZII „Comanda 11.1”] Importul salariaților peste fișe existente.

- **420** (pct.12): „norma și funcția de bază lipsă din fișier se pun tăcut. Trebuie editabile în previzualizare și marcate «de
  verificat», ca celelalte.” CAUZA, văzută pe producție (F6 Migrare Test SRL, `tenant_055`, numai citire): cei 3 salariați au fost
  importați la 19.10.2026, înainte de reparația 420 — norma și funcția de bază puse tăcut, marcate numai persoanele și scutirea. La
  retestul din 21.10 (cod 22c71846) fișierul a fost încărcat din nou peste ei; salvarea păstra valorile vechi și ținea marcajul numai
  pentru câmpurile marcate DEJA (intersecția `EXCLUDED.de_verificat ∩ salariati.de_verificat`), deci norma și funcția de bază ieșeau
  iar nemarcate. E2E-ul lotului 10 a trecut pentru că lucra pe o firmă NOUĂ, fără fișe.
- **447** (pct.15): „mesajul după import: «0 noi, 3 fișe actualizate», nu «3 importați» plus «3 actualizate».” `importati` cuprindea și
  fișele actualizate; acum `importa` numără la scriere `noi` (rând inserat) și `actualizate`.

TEMEI: N/A — regula de produs a lui Costin (marcajul „de verificat” al câmpurilor lipsă, comanda 14.10 pct.3–4 și 10.1), nicio valoare
fiscală. CNP-urile de probă au cifra de control verificată (algoritmul din CLAUDE.md). Schemă efemeră din template, tranzacție anulată."""
import os

import pytest

from core import db as _db, salariati_import_api as si

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = "ztest_lot11_m_salariati"
CNP1 = "1900101410011"      # cifra de control verificată (test_412_cim_salariat)
CNP2 = "1960101078916"      # cifra de control verificată (test_import_saga.CNP_OK)
FARA_NORMA = ("nume;prenume;cnp;data angajare;brut;judet;persoane in intretinere;scutit contributie minima\n"
              "POPESCU;ANA;%s;2024-01-15;5000;B;0;nu\nIONESCU;RADU;%s;2024-02-01;6000;CJ;1;nu\n" % (CNP1, CNP2)).encode("utf-8")


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    from core import tenant_provisioning as _tp
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % SCHEMA)
            yield c
        finally:
            c.rollback()


def _fisa(c, cnp):
    with c.cursor() as cur:
        cur.execute("SELECT part_time, ore_zi, functie_baza, de_verificat FROM salariati WHERE cnp = %s", (cnp,))
        r = cur.fetchone()
        return (r[0], float(r[1]), r[2], sorted(r[3]))


def _ca_pe_f6(c):
    """Starea fișelor F6 după importul din 19.10.2026 (dinainte de 420): norma și funcția de bază puse fără marcaj, marcate numai
    persoanele și scutirea. DATE DE PORNIRE pe care aplicația de azi nu le mai produce (codul vechi le producea) — scrise direct."""
    si.importa(c, si.extrage(FARA_NORMA, "s.csv"))
    with c.cursor() as cur:
        cur.execute("UPDATE salariati SET de_verificat = '{scutit_contrib_minim,persoane_intretinere}'::text[]")


def test_def_420_reimportul_peste_fisa_marcheaza_norma_si_functia_de_baza_lipsa(conn):
    """ROȘU înainte: după reimportul confirmat, POPESCU avea marcajul [] (intersecția cu marcajul vechi) — norma și funcția de bază
    rămâneau „puse tăcut”. VERDE: valorile din fișă rămân, iar câmpurile lipsă din fișier sunt marcate de verificat.
    MUTAȚIA: marcajul înapoi pe intersecție -> pică."""
    _ca_pe_f6(conn)
    rr = si.din_fise(conn, si.extrage(FARA_NORMA, "s.csv"))
    rez = si.importa(conn, rr, inlocuieste=True)
    assert rez["respinse"] == []
    # norma întreagă și funcția de bază Da rămân (fișa), marcate; persoanele și scutirea vin acum din fișier, deci nu mai sunt marcate
    assert _fisa(conn, CNP1) == (False, 8.0, True, ["functie_baza", "tip_norma"])


def test_def_420_previzualizarea_arata_valoarea_din_fisa_nu_propunerea(conn):
    """Fișa lui IONESCU: normă parțială 4 ore, funcția de bază „Nu”. Fișierul nu le are. Previzualizarea arată ce păstrează salvarea —
    parțială 4 ore, „Nu” —, editabile și marcate, cu textul „rămâne cea din fișa existentă”; POPESCU nou (alt CNP șters) primește
    propunerea. MUTAȚIA: `din_fise` care nu schimbă nimic -> propunerea „întreagă” / „Da” -> pică."""
    from core import salariati_api as sa
    _ca_pe_f6(conn)
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM salariati WHERE cnp = %s", (CNP2,))
        sid = cur.fetchone()[0]
        cur.execute("DELETE FROM salariu_istoric WHERE salariat_id IN (SELECT id FROM salariati WHERE cnp = %s)", (CNP1,))
        cur.execute("DELETE FROM salariati WHERE cnp = %s", (CNP1,))
    sa.actualizeaza_salariat(conn, sid, tip_norma="partiala", ore_zi=4, functie_baza=False)
    rr = si.eticheteaza(si.din_fise(conn, si.extrage(FARA_NORMA, "s.csv")))
    pop, ion = rr
    assert (pop["tip_norma"], pop["functie_baza"], pop.get("din_fisa")) == ("intreaga", True, None)      # salariat nou: propunerea
    assert (ion["tip_norma"], ion["ore_zi"], ion["functie_baza"], ion["din_fisa"]) == ("partiala", 4.0, False, ["tip_norma", "functie_baza"])
    assert {"tip_norma", "functie_baza"} <= set(ion["de_verificat"])
    assert ("IONESCU RADU: norma de lucru lipsește din fișier — rămâne cea din fișa existentă, normă parțială, 4 ore pe zi; schimb-o pe "
            "rând dacă nu e așa (intră marcată de verificat)") in ion["motive"], ion["motive"]
    assert ("IONESCU RADU: funcția de bază lipsește din fișier — rămâne cea din fișa existentă („Nu”); schimb-o pe rând dacă nu e așa "
            "(intră marcată de verificat)") in ion["motive"], ion["motive"]
    # salvarea păstrează exact ce a arătat previzualizarea
    si.importa(conn, rr, inlocuieste=True)
    assert _fisa(conn, CNP2) == (True, 4.0, False, ["functie_baza", "tip_norma"])


def test_def_420_alegerea_de_pe_ecran_scrie_valoarea_si_scoate_marcajul(conn):
    """Contabilul alege pe rând (normă parțială, 6 ore): ecranul scoate câmpul din marcaj, iar salvarea îl scrie peste fișă, nemarcat."""
    _ca_pe_f6(conn)
    rr = si.din_fise(conn, si.extrage(FARA_NORMA, "s.csv"))
    rr[0].update(tip_norma="partiala", ore_zi=6, de_verificat=[x for x in rr[0]["de_verificat"] if x != "tip_norma"])
    si.importa(conn, rr, inlocuieste=True)
    assert _fisa(conn, CNP1) == (True, 6.0, True, ["functie_baza"])


def test_def_447_importul_numara_noi_si_fise_actualizate(conn):
    """ROȘU înainte: `importa` întorcea numai `importati` (3 = noi + actualizate), iar ecranul spunea „3 importați” și „3 actualizate”.
    MUTAȚIA: `noi` numărat pe fiecare rând scris -> al doilea import spune 2 noi -> pică."""
    r1 = si.importa(conn, si.extrage(FARA_NORMA, "s.csv"))
    assert (r1["importati"], r1["noi"], r1["actualizate"]) == (2, 2, 0)
    r2 = si.importa(conn, si.extrage(FARA_NORMA, "s.csv"), inlocuieste=True)
    assert (r2["importati"], r2["noi"], r2["actualizate"]) == (2, 0, 2)


# ── 447: gardul clasei (CICLUL DE NECONFORMITATE pas 4) ─────────────────────────────────────────────────────────────────────────
def test_447_clasa_importul_care_actualizeaza_numara_noi_si_actualizate():
    """Clasa 447: un import care ACTUALIZEAZĂ ce exista (`ON CONFLICT … DO UPDATE` în `importa`) numără la scriere `noi` și `actualizate`,
    ca ecranul să spună fiecare număr o singură dată. Scan AST pe TOATE modulele din `core/` cu `def importa` (un import nou intră singur);
    premisa anti-vacuu: scanul vede `salariati_import_api` (singurul upsert de azi). MUTAȚIA: cheia `noi` scoasă din `importa` -> pică."""
    import ast
    import glob
    gasite, rele = [], []
    for f in sorted(glob.glob(os.path.join(RAD, "core", "*.py"))):
        if os.path.basename(f).startswith("test_"):
            continue
        src = open(f, encoding="utf-8").read()
        if "def importa" not in src:
            continue
        for n in ast.walk(ast.parse(src)):
            if isinstance(n, ast.FunctionDef) and n.name == "importa":
                corp = ast.get_source_segment(src, n) or ""
                if "DO UPDATE" not in corp:
                    continue
                gasite.append(os.path.basename(f))
                chei = {k.value for r in ast.walk(n) if isinstance(r, ast.Return) and isinstance(r.value, ast.Dict)
                        for k in r.value.keys if isinstance(k, ast.Constant)}
                if not {"noi", "actualizate"} <= chei:
                    rele.append("%s: întoarce %s" % (os.path.basename(f), sorted(chei)))
    assert set(gasite) >= {"salariati_import_api.py"}, "anti-vacuu: scanul nu mai vede upsert-ul salariaților: %s" % gasite
    assert not rele, "import care actualizează fără `noi` / `actualizate` (447):\n  " + "\n  ".join(rele)


def test_447_ecranul_spune_noi_si_fise_actualizate_nu_importati():
    """Mesajul de după importul salariaților vine din `_noiActualizate` (noi + actualizate de la server), nu din `rez.importati` (care
    le cuprinde pe amândouă) plus `rez.actualizati`. MUTAȚIA: mesajul vechi cu `rez.importati` -> pică."""
    from core.arbore_js import apeluri, arbore_js, functia, noduri
    arb, cod = arbore_js("migrare.js")
    fn = functia(arb, "previzualizeazaSalariati")
    citite = {cod(m) for m in noduri(fn, "MemberExpression") if cod(m).startswith("rez.") or cod(m).startswith("rez &&")}
    assert not {"rez.importati", "rez.actualizati"} & citite, sorted(citite)
    assert apeluri(fn, cod, "_noiActualizate") == [("rez", '"fișă actualizată"', '"fișe actualizate"')]
    aj = functia(arb, "_noiActualizate")
    assert sorted(cod(m) for m in noduri(aj, "MemberExpression") if cod(m).startswith("rez.")) == ["rez.actualizate", "rez.noi"]
