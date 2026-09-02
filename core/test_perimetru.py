# -*- coding: utf-8 -*-
"""GARD [02.09.2026]: perimetrul portii SCURTE se DERIVA, si stie cand nu poate.

**Regula pazita** (`PLAN_LUCRU.md`, regula 4 de conducere a lucrului, Costin 02.09.2026):
*„se ruleaza constructia atinsa si tot ce depinde de ea, derivat din dependentele reale din cod,
nu ales de la caz la caz. … Daca derivarea nu poate stabili cu certitudine perimetrul, se ruleaza
tot si se spune de ce."*

**CELE DOUA DIRECTII, fiindca una singura n-ar dovedi nimic** (METODA §22):
  1. pe un modul cu dependenti CUNOSCUTI, perimetrul ii CONTINE — altfel instrumentul ar putea
     intoarce mereu lista vida si ar parea ca „a scurtat" perfect;
  2. pe clasele pe care graful de import NU le vede (registru `.md`, `main.py`, `conftest.py`),
     instrumentul REFUZA sa scurteze si spune de ce — altfel ar da verde despre ce n-a rulat.

**Ce NU pazeste, declarat:** ca perimetrul e MINIM. Un perimetru prea larg costa minute; unul prea
ingust costa o regresie nevazuta. Gardul apara doar directia care doare.
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from scripts import perimetru as P  # noqa: E402


def test_perimetrul_contine_dependentii_REALI_ai_modulului_atins():
    """`core/d100.py` e importat de `core/declaratii_api.py` si de `core/d100_reconciliere.py`;
    amandoua au teste proprii. Un perimetru care nu le contine ar fi o poarta care sare peste
    exact ce s-a atins."""
    teste, incerte = P.perimetru(["core/d100.py"])
    assert not incerte, "derivarea a raportat incertitudini pe un modul curat: %s" % incerte
    # Operatorul de MULTIME, nu `in`: `>=` **crapa** daca `teste` devine vreodata un sir, in loc
    # sa treaca ca sub-sir. Forma recomandata in chiar antetul lui `core/scan_garzi_pe_text.py`.
    ceruti = {"core/test_d100.py", "core/test_d100_reconciliere.py",
              "core/test_declaratii_componente.py", "core/test_supervizor.py"}
    assert set(teste) >= ceruti, (
        "depind tranzitiv de core/d100.py si NU sunt in perimetru: %s — o schimbare de camp ar "
        "trece poarta scurta fara sa fie probata acolo unde se citeste" % sorted(ceruti - set(teste)))


def test_un_modul_fara_niciun_dependent_nu_umfla_perimetrul():
    """Directia opusa: daca perimetrul ar fi mereu «tot», regula n-ar scurta nimic si gardul de
    sus ar trece degeaba."""
    teste_d100, _ = P.perimetru(["core/d100.py"])
    toate = [f for f in P._fisiere_py() if os.path.basename(f).startswith("test_")]
    assert len(teste_d100) < len(toate), (
        "perimetrul lui core/d100.py (%d) nu e mai mic decat suita intreaga (%d) — atunci "
        "instrumentul nu deriva nimic, doar returneaza tot" % (len(teste_d100), len(toate)))


def test_ce_graful_de_import_NU_vede_cere_poarta_COMPLETA():
    """Un registru `.md` e citit de garzi care NU-l importa; `main.py` e citit de scanere de rute.
    Pe clasele astea derivarea trebuie sa REFUZE, nu sa intoarca un perimetru mic si linistitor."""
    for atins in ("PLAN_LUCRU.md", "main.py", "conftest.py"):
        _teste, incerte = P.perimetru([atins])
        assert incerte, (
            "%s a produs un perimetru DERIVAT, fara nicio incertitudine — dar graful de import "
            "nu vede cine il citeste, deci verdele ar fi despre ce n-a rulat" % atins)
        assert any(atins in m for m in incerte), (
            "incertitudinea nu numeste fisierul care a produs-o: %s" % incerte)


def test_motivul_incertitudinii_e_SCRIS_nu_doar_semnalat():
    """«se ruleaza tot SI SE SPUNE DE CE». Un refuz fara motiv scris devine, la a treia oara, o
    superstitie: se ruleaza tot fiindca «asa face instrumentul»."""
    _teste, incerte = P.perimetru(["CONFORMITATE.md"])
    assert incerte and all(" — " in m and len(m.split(" — ")[1].strip()) > 20 for m in incerte), (
        "incertitudinile n-au motiv scris: %s" % incerte)


def test_importurile_se_citesc_cu_AST_nu_din_text():
    """Clichetul 50 / METODA §23, aplicat instrumentului insusi: un `import` scris intr-un
    comentariu sau intr-un sir NU e o dependenta. Un scaner pe text nu deosebeste codul de proza —
    lectia 3 din predarea de pe 02.09, intoarsa aici ca gard."""
    import ast
    sursa = open(os.path.join(_RAD, "scripts", "perimetru.py"), encoding="utf-8").read()
    arbore = ast.parse(sursa)
    fn = next(n for n in ast.walk(arbore)
              if isinstance(n, ast.FunctionDef) and n.name == "importurile")
    apeluri = {n.func.attr for n in ast.walk(fn)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert apeluri >= {"parse", "walk"}, (
        "`importurile` nu mai foloseste `ast` — daca a trecut pe expresii regulate, un import "
        "citat intr-un comentariu devine o dependenta, iar perimetrul creste pe proza")
