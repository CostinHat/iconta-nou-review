# -*- coding: utf-8 -*-
"""META-GARD (LANT legislatie TURA 4, 10.08.2026): NICIO reconciliere sursa-vs-declaratie nu moare tacit.

Clasa "D300 mort" (tura 14): cross-check-ul TVA murise fiindca apelul d300.genereaza se rupsese (derivare de
semnatura) iar `except -> gri` inghitea eroarea - "am verificat" fara sa verifice. Gardul de wiring
(test_control_incrucisat_wiring) acopera calea de Control fiscal pentru D300. Acesta il GENERALIZEAZA la stratul
de GENERARE (a-doua-cale): fiecare declaratie cu reconciliere trebuie sa aiba, MECANIC (verificat prin AST, nu
pe text - imun la mentiuni in docstring):
  (a) modulul core/dXXX_reconciliere.py PREZENT;
  (b) verifica_reconciliere IMPORTAT si APELAT in dXXX.genereaza (orice stil de import; un modul necablat e mort);
  (c) NON-TAUTOLOGIE: dXXX_reconciliere NU importa generatorul core.dXXX - altfel ar imparti agregarea cu calea 1
      si un bug de agregare n-ar produce divergenta;
  (d) un test de reconciliere (test_dXXX_reconciliere.py) - proba de FIRE pe divergenta traieste acolo (mutatie
      ROLLBACK sursa-vs-declaratie).

Un modul sters, necablat, tautologizat sau fara test = gardul pica. D710 EXCEPTAT (input manual, fara sursa DB -
reconcilierea lui e aritmetica interna suma_ded in calcul_d710, gardata de test_d710_suma_ded)."""
import ast
import pathlib

_RAD = pathlib.Path(__file__).resolve().parent.parent
_CORE = _RAD / "core"
DECL_CU_RECONCILIERE = ["d100", "d101", "d112", "d205", "d300", "d301", "d390", "d394", "d406"]


def _ast(nume):
    p = _CORE / nume
    if not p.exists():
        return None
    return ast.parse(p.read_text(encoding="utf-8", errors="replace"))


def _importuri_modul(tree, modul_tinta, nume_scurt):
    """(aliasuri_modul, nume_functie_import) - cum e adus modulul dXXX_reconciliere si functia verifica_reconciliere.
    Acopera: `from core.X import verifica_reconciliere [as a]`, `import core.X [as a]`, `from core import X [as a]`."""
    alias_modul, nume_functie = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == modul_tinta:
            for a in node.names:
                if a.name == "verifica_reconciliere":
                    nume_functie.add(a.asname or a.name)
        elif isinstance(node, ast.Import):
            for a in node.names:
                if a.name == modul_tinta:
                    alias_modul.add(a.asname or a.name.split(".")[-1])
        elif isinstance(node, ast.ImportFrom) and node.module == "core":
            for a in node.names:
                if a.name == nume_scurt:
                    alias_modul.add(a.asname or a.name)
    return alias_modul, nume_functie


def test_fiecare_reconciliere_are_modul():
    """(a) core/dXXX_reconciliere.py exista pentru fiecare declaratie cu reconciliere."""
    lipsa = [d for d in DECL_CU_RECONCILIERE if not (_CORE / (d + "_reconciliere.py")).exists()]
    assert not lipsa, "module de reconciliere lipsa (a-doua-cale absenta): %s" % lipsa


def test_fiecare_reconciliere_e_cablata_in_genereaza():
    """(b) dXXX.py aduce verifica_reconciliere din dXXX_reconciliere SI il apeleaza (orice stil). AST, nu text."""
    rele = []
    for d in DECL_CU_RECONCILIERE:
        tree = _ast(d + ".py")
        if tree is None:
            rele.append("%s.py lipseste" % d); continue
        modul = "core.%s_reconciliere" % d
        alias_modul, nume_functie = _importuri_modul(tree, modul, d + "_reconciliere")
        if not (alias_modul or nume_functie):
            rele.append("%s: nu importa %s_reconciliere" % (d, d)); continue
        chemat = False
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            if isinstance(f, ast.Name) and f.id in nume_functie:
                chemat = True; break
            if isinstance(f, ast.Attribute) and f.attr == "verifica_reconciliere" \
                    and isinstance(f.value, ast.Name) and f.value.id in alias_modul:
                chemat = True; break
        if not chemat:
            rele.append("%s: verifica_reconciliere importat dar NEAPELAT in genereaza (mort tacit)" % d)
    assert not rele, "reconcilieri necablate (definite dar nechemat):\n  " + "\n  ".join(rele)


def test_fiecare_reconciliere_e_non_tautologica():
    """(c) dXXX_reconciliere NU importa generatorul core.dXXX (AST - imun la mentiuni in docstring)."""
    rele = []
    for d in DECL_CU_RECONCILIERE:
        tree = _ast(d + "_reconciliere.py")
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == ("core.%s" % d):
                rele.append("%s_reconciliere: from core.%s import (tautologie)" % (d, d))
            elif isinstance(node, ast.Import) and any(a.name == ("core.%s" % d) for a in node.names):
                rele.append("%s_reconciliere: import core.%s (tautologie)" % (d, d))
            elif isinstance(node, ast.ImportFrom) and node.module == "core" and any(a.name == d for a in node.names):
                rele.append("%s_reconciliere: from core import %s (tautologie)" % (d, d))
    assert not rele, "reconcilieri TAUTOLOGICE (importa generatorul - nu-s a-doua-cale independenta):\n  " + "\n  ".join(rele)


def test_fiecare_reconciliere_are_test_care_probeaza_firing():
    """(d) exista test_dXXX_reconciliere.py per declaratie (proba de FIRE pe divergenta traieste acolo)."""
    lipsa = [d for d in DECL_CU_RECONCILIERE if not (_CORE / ("test_%s_reconciliere.py" % d)).exists()]
    assert not lipsa, "declaratii fara test de reconciliere (firing-ul nu e probat): %s" % lipsa


def test_meta_gard_prinde_un_modul_lipsa():
    """MUTATIE pe meta-gard: un modul inexistent (d999) trebuie semnalat de logica (a)."""
    fals = [d for d in DECL_CU_RECONCILIERE + ["d999"] if not (_CORE / (d + "_reconciliere.py")).exists()]
    assert "d999" in fals, "logica gardului (a) e rupta: un modul inexistent nu e semnalat"
