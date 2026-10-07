# -*- coding: utf-8 -*-
"""GARD — jurnalul schimbărilor regimului de TVA (PIVOT DECIZII 04.10.2026, răspunsurile lui Costin la confirmări).

Costin: „Regimul de TVA la «Poate pregăti»: confirmat, cu jurnalizarea fiecărei schimbări (utilizator, dată, vechi → nou), ca
la bifa C&D.” Câmpurile: `platitor_tva`, `tip_decont`, `inreg_art317` (`repo_firma_profil.CAMPURI_REGIM_TVA`).

CE FACE IMPOSIBIL:
- o scriere NOUĂ a acestor câmpuri care ocolește jurnalul (gardul structural: orice funcție din `core/` care scrie
  `firma_profil` și numește unul din câmpuri cheamă `jurnalizeaza_regim_tva`, sau e pe lista închisă de mai jos, cu motiv);
- un rând de jurnal pentru o salvare care nu schimbă nimic; un rând fără utilizator; vechiul greșit;
- seed-ul vechi „T”/„L” luat drept schimbare la prima salvare.
CE NU VEDE: o scriere cu numele câmpurilor venit dintr-o listă de la nivelul modulului (SQL compus dinamic). Singurul scriitor
dinamic al `firma_profil` cunoscut (`firma_profil_api.salveaza_date`) e pinat: listele lui nu conțin câmpurile de regim.
"""
import ast
import glob
import io
import os
import re

import pytest

from core import repo_firma_profil as R

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Lista ÎNCHISĂ a scriitorilor care nu jurnalizează, fiecare cu motivul.
_FARA_JURNAL = {
    ("tenant_provisioning", "precompleteaza_din_anaf"):
        "precompletarea din ANAF la CREAREA firmei (register, adăugare, import) — valoarea inițială, nu o schimbare: nu "
        "există „vechi” (DECIZII 04.10.2026, PIVOT pe drepturi, consecința 1)",
    ("migrare_fapte_date_firma", "aplica"):
        "normalizarea schemei (lotul 07.10 B, comanda Costin A.3): un `false` care era implicitul coloanei, nedistinct de o "
        "alegere, devine NULL (neales) — nu e o schimbare făcută de un utilizator; rândurile cu intrare în jurnal (alese) rămân",
}
_SCRIERE = re.compile(r"\b(?:INSERT\s+INTO|UPDATE)\s+[\w\"%{}.']*firma_profil\b(?!_)")
_CAMP = re.compile(r"\b(?:%s)\b" % "|".join(R.CAMPURI_REGIM_TVA))


def _scriitori():
    """{(modul, funcție): jurnalizează?} pentru funcțiile care scriu `firma_profil` și numesc un câmp de regim TVA."""
    out = {}
    for f in sorted(glob.glob(os.path.join(RAD, "core", "*.py"))):
        mod = os.path.basename(f)[:-3]
        if mod.startswith("test_") or mod.startswith("scan_"):
            continue
        src = io.open(f, encoding="utf-8").read()
        for n in ast.walk(ast.parse(src)):
            if not isinstance(n, ast.FunctionDef):
                continue
            seg = ast.get_source_segment(src, n) or ""
            if _SCRIERE.search(seg) and _CAMP.search(seg):
                out[(mod, n.name)] = bool(re.search(r"\bjurnalizeaza_regim_tva\(", seg))
    return out


def test_orice_scriere_a_regimului_de_tva_trece_prin_jurnal():
    s = _scriitori()
    ocolesc = sorted(k for k, j in s.items() if not j and k not in _FARA_JURNAL)
    assert not ocolesc, ("funcții care scriu regimul de TVA fără `jurnalizeaza_regim_tva` (decizia Costin: „jurnalizarea "
                         "fiecărei schimbări”): %s" % ocolesc)
    # anti-vacuu + lista închisă reală: cele două căi cunoscute se văd, iar excepțiile există încă
    assert {("repo_firma_profil", "seteaza_platitor_tva"), ("vector_fiscal_api", "salveaza")} <= set(s), sorted(s)
    assert set(_FARA_JURNAL) <= set(s), "excepție care nu mai scrie regimul — scoate-o: %s" % (set(_FARA_JURNAL) - set(s))


def test_scriitorul_dinamic_al_profilului_nu_primeste_campurile_de_regim():
    from core import firma_profil_api as fpa
    liste = set(fpa.CAMPURI_FISCALE) | set(fpa.CAMPURI_CAPITAL) | set(fpa.CAMPURI_AMEF)
    assert not (liste & set(R.CAMPURI_REGIM_TVA)), liste & set(R.CAMPURI_REGIM_TVA)


def test_CALIBRARE_gardul_vede_o_scriere_fara_jurnal():
    src = ('def a(cur):\n    cur.execute("UPDATE firma_profil SET tip_decont = %s", (1,))\n'
           'def b(cur):\n    cur.execute("UPDATE firma_profil SET logo = %s", (1,))\n'
           'def c(cur):\n    cur.execute("UPDATE firma_profil_jurnal SET platitor_tva = 1")\n')
    gasit = {n.name for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef)
             and _SCRIERE.search(ast.get_source_segment(src, n)) and _CAMP.search(ast.get_source_segment(src, n))}
    assert gasit == {"a"}, gasit


# ── pe bază: schemă efemeră din template, în ROLLBACK ─────────────────────────────────────────────────────────────────
def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


SCH = "ztest_jurnal_regim_tva"


@pytest.fixture
def cur():
    from core import db, tenant_provisioning as _tp
    db.init_pool()
    with db.get_conn() as conn:
        try:
            with conn.cursor() as c:
                c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                c.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"),
                                                              encoding="utf-8").read(), SCH))
                c.execute("SET LOCAL search_path TO %s, public" % SCH)
                yield c
        finally:
            conn.rollback()


def _jurnal(c):
    c.execute("SELECT camp, valoare_veche, valoare_noua, user_id FROM firma_profil_jurnal ORDER BY id")
    return c.fetchall()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_template_are_jurnalul_cu_utilizator_obligatoriu(cur):
    from core import migrare_firma_profil_jurnal as mig
    cur.execute("SELECT column_name, is_nullable FROM information_schema.columns WHERE table_schema=%s "
                "AND table_name='firma_profil_jurnal' ORDER BY ordinal_position", (SCH,))
    assert cur.fetchall() == [("id", "NO"), ("camp", "NO"), ("valoare_veche", "YES"), ("valoare_noua", "YES"),
                              ("user_id", "NO"), ("la", "NO")]
    mig.aplica(cur.connection, SCH)   # idempotentă peste template


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_regimul_tva_doar_schimbarile_reale_in_ordine_cu_utilizatorul(cur):
    """MUTAȚIE: INSERT-ul jurnalului scos -> [] -> pică; condiția `v != n` scoasă -> rânduri în plus -> pică."""
    R.seteaza_platitor_tva(cur, True, 7)                 # firmă fără profil: nimic de schimbat, nimic de jurnalizat
    assert _jurnal(cur) == []
    cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, tip_decont) VALUES (1,'ZT','14399840',false,'T')")
    R.seteaza_platitor_tva(cur, False, 7)                # aceeași valoare: nu e o schimbare
    R.seteaza_platitor_tva(cur, True, 7)
    R.seteaza_platitor_tva(cur, False, 9)
    assert _jurnal(cur) == [("platitor_tva", "false", "true", 7), ("platitor_tva", "true", "false", 9)]
    with pytest.raises(ValueError):
        R.seteaza_platitor_tva(cur, True, None)          # fără autor nu se jurnalizează -> nu se schimbă


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_vectorul_jurnalizeaza_toate_cele_trei_si_prima_salvare_cu_vechiul_gol(cur):
    from core import vector_fiscal_api as v
    r = v.salveaza(cur.connection, "micro", True, "trimestrial", False, nume="ZT", cui="14399840", user_id=5)
    assert r["ok"], r
    # [lotul 07.10 B] art.317 neales (None) nu mai devine „false”: prima salvare fără el nu jurnalizează nimic pentru el
    assert _jurnal(cur) == [("platitor_tva", None, "true", 5), ("tip_decont", None, "trimestrial", 5)]
    cur.execute("UPDATE firma_profil SET tip_decont = 'T'")   # seed-ul vechi: aceeași periodicitate
    cur.execute("DELETE FROM firma_profil_jurnal")
    assert v.salveaza(cur.connection, "micro", True, "trimestrial", False, user_id=5)["ok"]
    assert _jurnal(cur) == [], "„T” -> „trimestrial” jurnalizat ca schimbare"
    assert v.salveaza(cur.connection, "micro", True, "lunar", False, inreg_art317=True, user_id=6)["ok"]
    assert v.salveaza(cur.connection, "micro", False, None, False, user_id=6)["ok"]
    assert _jurnal(cur) == [("tip_decont", "trimestrial", "lunar", 6), ("inreg_art317", None, "true", 6),
                            ("platitor_tva", "true", "false", 6), ("tip_decont", "lunar", None, 6),
                            ("inreg_art317", "true", None, 6)]   # omis = neales (None), consemnat ca atare
