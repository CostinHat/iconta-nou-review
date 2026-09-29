# -*- coding: utf-8 -*-
"""GARD [3c, CF art.77 alin.(1)]: deducerea personala se acorda NUMAI la functia de baza.

Formula (core/salarizare.calcul_salariu) trateaza deja corect functie_baza=False. Defectul era de
CABLARE: coloana lipsea si apelantii (stat de plata + D112) nu treceau flag-ul (default True ->
deducere pt toti). Gardul asertează pe STRUCTURA (METODA §23), FARA `"sir" in sursa`:
  - AST: ambele trasee cheama calcul_salariu cu argumentul-cheie `functie_baza`;
  - AST: D112 poarta cheia "functie_baza" intr-un dict al salariatului;
  - DB: coloana exista in information_schema (structura reala, nu textul din tenant_template.sql);
  - comportament: pe formula, fara functia de baza deducerea e 0.
Mutatie: scoaterea `functie_baza=` din oricare apelant -> AST rosu; drop coloana -> DB rosu.
"""
import ast
import io
import os
from datetime import date

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _arbore(rel):
    return ast.parse(io.open(os.path.join(RAD, rel), encoding="utf-8").read())


def _cheama_cu_kw(rel, functie, kw):
    """AST: exista un apel `functie(..., kw=...)` in modul?"""
    for n in ast.walk(_arbore(rel)):
        if isinstance(n, ast.Call):
            f = n.func
            nume = f.id if isinstance(f, ast.Name) else getattr(f, "attr", None)
            if nume == functie and any(k.arg == kw for k in n.keywords):
                return True
    return False


def _dict_are_cheie(rel, cheie):
    """AST: exista un literal de dict cu cheia data (nod ast.Dict cu ast.Constant)?"""
    for n in ast.walk(_arbore(rel)):
        if isinstance(n, ast.Dict):
            for k in n.keys:
                if isinstance(k, ast.Constant) and k.value == cheie:
                    return True
    return False


def test_stat_plata_paseaza_functie_baza():
    assert _cheama_cu_kw("core/stat_plata_api.py", "calcul_salariu", "functie_baza"), \
        "stat_plata_api nu mai paseaza functie_baza catre calcul_salariu (CF art.77(1) necablat)"


def test_d112_paseaza_functie_baza():
    assert _cheama_cu_kw("core/d112.py", "calcul_salariu", "functie_baza"), \
        "d112 nu mai paseaza functie_baza catre calcul_salariu (CF art.77(1) necablat)"
    assert _dict_are_cheie("core/d112.py", "functie_baza"), \
        "d112 nu mai include cheia functie_baza in dictul salariatului"


def test_schema_are_coloana_in_db():
    # STRUCTURA REALA: coloana exista in information_schema pentru o schema de tenant.
    from core import db
    from core import migrare_functie_baza as mig
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name LIMIT 1")
            rand = cur.fetchone()
        assert rand, "niciun tenant in DB de test"
        schema = rand[0]
        assert mig.verifica(conn, schema), \
            "coloana functie_baza lipseste din %s.salariati (migrarea neaplicata)" % schema


def test_formula_fara_functie_baza_deducere_zero():
    # PROBA PE PORTOFOLIU (CF art.77(1)): un salariat cu functia de baza la ALT angajator
    # (functie_baza=False) NU primeste deducere personala; cu functie_baza=True o primeste.
    from core import salarizare as sz
    la = date(2026, 3, 1)
    fara = sz.deducere_personala(4050, persoane=0, functie_baza=False, la_data=la)["total"]
    cu = sz.deducere_personala(4050, persoane=0, functie_baza=True, la_data=la)["total"]
    assert fara == 0, "fara functia de baza deducerea trebuie sa fie 0 (CF art.77(1))"
    assert cu > 0, "la functia de baza deducerea trebuie acordata"
