# -*- coding: utf-8 -*-
"""GARD [R75 (b), 27.08.2026]: procesul care servește ecranele e supravegheat, și se știe cum.

Costin: *„(b) e în aceeași formă cu ce merge deja: `cron.RITMURI` supraveghează 11 joburi; al
12-lea e procesul care le servește pe toate."* Iar cerința, textual: **„procesul e viu ȘI
răspunde"** — nu doar `active` la systemd.

CE FACE IMPOSIBIL:
  1. sonda scoasă din `cron.RITMURI` — atunci lipsa ei n-ar fi lipsă pentru nimeni;
  2. sonda care nu mai trece prin `cron.ruleaza` — n-ar alerta la eșec și n-ar bate la reușită;
  3. sonda care se mulțumește să întrebe systemd dacă unitatea e `active`: trebuie să **ceară
     pagina** și să compare **ora de pornire**. Amândouă, structural;
  4. constanta legată ca argument implicit — forma care a făcut calea de eșec neprobabilă la
     prima scriere (prinsă de propria calibrare, în aceeași tură).

CE NU FACE, declarat, și e afirmația mai slabă pe care Costin a cerut-o scrisă ca atare:
**sonda prinde REPORNIREA, nu durata căderii.** Între două rulări la 15 minute, o cădere de trei
secunde și una de paisprezece minute arată identic. Ce se poate spune e *„a repornit între X și
Y"*, nu *„a fost jos N secunde"*. Iar dacă mașina cade cu totul, nu rulează nici sonda — limita
declarată deja în `cron.verifica_batai`, pe care doar un deadman EXTERN ar acoperi-o.
"""
import ast
import io
import os

from core import cron, sonda_web

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _arbore():
    return ast.parse(io.open(os.path.join(_RAD, "core", "sonda_web.py"), encoding="utf-8").read())


def test_sonda_e_in_deadman():
    assert set(cron.RITMURI) >= {"sonda_web"}, (
        "`sonda_web` nu e în `cron.RITMURI` — lipsa ei n-ar fi lipsă pentru nimeni")
    assert cron.RITMURI["sonda_web"] >= 1, "prag prea strâns pentru un job la 15 minute"


def test_sonda_trece_prin_ambalajul_care_alerteaza_si_bate():
    """Structural: apelul, nu un comentariu."""
    arb = _arbore()
    gasit = any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "ruleaza"
        and isinstance(n.func.value, ast.Name) and n.func.value.id == "cron"
        and n.args and isinstance(n.args[0], ast.Name) and n.args[0].id == "NUME"
        for n in ast.walk(arb))
    assert gasit, "`sonda_web` nu trece prin `cron.ruleaza(NUME, …)`"


def test_sonda_CERE_pagina_si_compara_ora_de_pornire():
    """Cele două lucruri pe care le-a cerut Costin: viu **și** răspunde, plus repornirea vizibilă."""
    fn = next(n for n in ast.walk(_arbore())
              if isinstance(n, ast.FunctionDef) and n.name == "verifica")
    chemate = {n.func.id for n in ast.walk(fn)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert chemate >= {"raspunde", "ora_pornirii"}, (
        "`verifica` nu mai cere pagina sau nu mai citește ora de pornire: %s" % sorted(chemate))


def test_constantele_NU_sunt_argumente_implicite():
    """Forma care a făcut calea de eșec neprobabilă: `def f(baza=BAZA)` fixează valoarea la
    definirea funcției. Prinsă de propria calibrare, 27.08.2026."""
    rele = []
    for n in ast.walk(_arbore()):
        if not isinstance(n, ast.FunctionDef):
            continue
        for d in n.args.defaults:
            if isinstance(d, ast.Name) and d.id.isupper():
                rele.append("%s(...=%s)" % (n.name, d.id))
    assert not rele, (
        "constante legate ca argument implicit: %s — se citesc în corpul funcției, altfel calea "
        "de eșec nu se poate proba" % rele)


def test_pe_viu_procesul_raspunde():
    """Nu o simulare: se cere chiar pagina publică de la procesul care rulează acum."""
    cod, octeti = sonda_web.raspunde()
    assert cod == 200, "pagina publică răspunde %s" % cod
    assert octeti > 200, "pagina publică are doar %d octeți — e goală sau ruptă" % octeti


def test_ora_pornirii_se_poate_citi():
    """Fără ea, sonda ar putea spune doar «răspunde acum», nu «a repornit între timp»."""
    v = sonda_web.ora_pornirii()
    assert v and len(v) > 10, (
        "ora de pornire a unității nu se poate citi (%r) — jumătatea de detectare a repornirii "
        "e oarbă, iar sonda ar trebui s-o spună, nu s-o presupună" % v)


def test_deploy_ul_NU_alerteaza_iar_caderea_DA():
    """`post-commit` repornește serviciul la FIECARE commit. Fără distincția asta, sonda ar fi
    alertat de zece ori pe zi despre reporniri pe care le-am cerut noi — iar *„un semnal care se
    aprinde mereu nu mai e semnal"* e chiar doctrina din `core/cron.py`.

    Cele patru direcții, pe funcția PURĂ:"""
    f = sonda_web.fel_repornirii
    assert f("A", "A", "c1", "c1") is None, "n-a repornit, dar se raportează ceva"
    assert f("A", "B", "c1", "c2") == "deploy", "repornire cu ALT commit = deploy, nu cădere"
    assert f("A", "B", "c1", "c1") == "cadere", "repornire cu ACELAȘI commit = cădere"
    assert f("A", "B", None, "c1") == "necunoscut", (
        "fără unul din commituri, sonda trebuie să SPUNĂ că nu poate deosebi, nu să tacă")
    assert f(None, "B", None, "c1") is None, "prima rulare n-are cu ce compara"


def test_sonda_NU_citeste_commitul_din_memoria_altui_proces():
    """`versiune.stare()['running']` e ștampilat în memoria procesului WEB. Un proces CLI îl
    citește `None`, deci sonda ar raporta veșnic «necunoscut» — și ar alerta la fiecare deploy,
    exact ce distincția voia să evite. Prins la prima rulare reală, nu la scriere."""
    arb = _arbore()
    fn = next(n for n in ast.walk(arb)
              if isinstance(n, ast.FunctionDef) and n.name == "commitul_de_pe_disc")
    chemate = {n.func.attr for n in ast.walk(fn)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert chemate >= {"git_head"}, (
        "sursa commitului nu mai e `HEAD` de pe disc: %s" % sorted(chemate))
    assert chemate.isdisjoint({"stare"}), (
        "sonda citește iar din memoria procesului web — acolo va găsi mereu None")


def test_pe_viu_commitul_se_poate_citi():
    c = sonda_web.commitul_de_pe_disc()
    assert c and len(c) >= 7, (
        "commitul de pe disc nu se poate citi (%r) — sonda ar raporta orice repornire ca "
        "«necunoscut», deci ar alerta și la deploy" % c)


def test_CALIBRARE_o_unitate_inexistenta_NU_inventeaza_o_ora():
    """Direcția «pretinde că știe»: sonda are voie să nu știe, nu are voie să fabrice."""
    assert sonda_web.ora_pornirii("unitate-care-nu-exista-r75.service") in (None, ""), (
        "a întors o valoare pentru o unitate inexistentă")
