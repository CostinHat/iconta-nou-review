# -*- coding: utf-8 -*-
"""[lotul 11, F] GARDĂ — citarea unui `Temei` ajunge la contabil în forma din CLAUDE.md §3.1, nu compusă greșit din câmpuri.

Defectul (găsit de G3, 22.10.2026): `NUMEROTARE_SECVENTIALA = Temei("OMFP", 2634, 2015, art="anexa 1", lit="pct. 24")` — `_citare_temei`
pune „art.” în fața lui `art` și „lit.” în fața lui `lit`, deci contabilul citea în refuzul numerotării „OMFP 2634/2015 art.anexa 1
lit.pct. 24”. Forma corectă: „OMFP 2634/2015 anexa 1 pct.24” (normele OMFP se citează pe PUNCTE, §3.1; anexa ca în restul codului,
ex. „OMFP 2634/2015 anexa 2 cod 14-6-30/a”).

CLASA: un `Temei(...)` al cărui text compus are după „art.” altceva decât un număr de articol (arab / roman), după „lit.” altceva decât o
literă, după „alin.(” altceva decât un număr, sau „pct. ” cu spațiu. Se caută pe AST, în toate modulele (`core/`, `scripts/`, `main.py`,
fără teste), pe textul pe care îl produce chiar `common._citare_temei` (sau `text=`, când e dat).

LIMITĂ DECLARATĂ: vede numai `Temei(...)` cu argumente literale (anti-vacuu: cel puțin 100 găsite); unul construit din variabile nu se
vede de aici.
"""
import ast
import glob
import os
import re

from core.common import _citare_temei

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CAMPURI = ("tip", "nr", "an", "art", "alin", "lit")
#: compunerea greșită: „art.” fără număr de articol, „lit.” fără literă, „alin.(” fără număr, „pct. ” cu spațiu
RAU = re.compile(r"\bart\.(?![0-9]|[IVXLCDM]+\b)|\blit\.(?![a-z]{1,2}\b)|\balin\.\((?!\d)|\bpct\.\s")

#: [lotul 11, F] instanțele aceleiași clase din fișiere pe care F nu le deține — patch-ul exact e cerut sesiunii principale (raportul F,
#: secțiunea 10). Lista se STRÂNGE: o instanță reparată iese și de aici (egalitatea de mai jos pică până atunci), una nouă nu intră.
IN_ASTEPTARE = {}   # [22.10.2026, sesiunea principală] cele 16 instanțe (categorie_marime ×9, d100_pozitia_116, registre_art321 ×3,
#: registru_evidenta_fiscala, registru_inventar ×2) reparate la sursă, în `common._citare_temei` (prefixul numai pe număr / literă)


def citari(fisiere=None):
    """[(fișier, linia, textul citării)] pentru fiecare `Temei(...)` cu argumente literale."""
    if fisiere is None:
        fisiere = sorted(glob.glob(os.path.join(_RAD, "core", "*.py")) + glob.glob(os.path.join(_RAD, "scripts", "*.py"))
                         + [os.path.join(_RAD, "main.py")])
    out = []
    for f in fisiere:
        if os.path.basename(f).startswith("test_"):
            continue
        arb = ast.parse(open(f, encoding="utf-8").read())
        rel = os.path.relpath(f, _RAD)
        for n in ast.walk(arb):
            if not (isinstance(n, ast.Call) and getattr(n.func, "id", getattr(n.func, "attr", None)) == "Temei"):
                continue
            try:
                p = dict(zip(_CAMPURI, (ast.literal_eval(a) for a in n.args)))
                p.update({k.arg: ast.literal_eval(k.value) for k in n.keywords if k.arg in _CAMPURI + ("text",)})
            except ValueError:
                continue
            out.append((rel, n.lineno, p["text"] if p.get("text") is not None else _citare_temei(*(p.get(k) for k in _CAMPURI))))
    return out


def test_citarea_temeiurilor_are_forma_din_3_1():
    toate = citari()
    assert len(toate) >= 100, "anti-vacuu: doar %d temeiuri găsite — scanul s-a rupt" % len(toate)
    rele = [(f, ln, t) for f, ln, t in toate if RAU.search(t)]
    pe_fisier = {}
    for f, _ln, _t in rele:
        pe_fisier[f] = pe_fisier.get(f, 0) + 1
    assert pe_fisier == IN_ASTEPTARE, (
        "citări compuse greșit (CLAUDE.md §3.1: „OMFP 2634/2015 anexa 1 pct.24”, nu „art.anexa 1 lit.pct. 24”) — scrie citarea întreagă "
        "în `text=` sau pune numărul articolului în `art`; o instanță reparată iese din IN_ASTEPTARE:\n%s"
        % "\n".join("  %s:%d  %s" % r for r in rele))


def test_numerotarea_secventiala_se_citeaza_pe_punctul_anexei():
    """Textul pe care îl citește contabilul în refuzul numerotării (`facturi_api.seteaza_numerotare`, `uc_comun`): OMFP 2634/2015 anexa 1
    pct.24 — „fiecare document va avea un număr de ordine sau o serie, după caz, număr sau serie ce trebuie să fie secvențial(ă)”."""
    from core.common import NUMEROTARE_SECVENTIALA as T
    assert (str(T), T.tip, T.nr, T.an) == ("OMFP 2634/2015 anexa 1 pct.24", "OMFP", 2634, 2015)


def test_calibrare_garda_prinde_compunerea_greșita_si_lasa_forma_corecta():
    """Ambele direcții (METODA §22): forma veche a lui NUMEROTARE_SECVENTIALA e prinsă, formele canonice §3.1 nu."""
    for rau in ("OMFP 2634/2015 art.anexa 1 lit.pct. 24", "OMFP 1802/2014 art.pct.22 alin.(1)",   # compunerea de dinainte de lotul 11
                "OPANAF 602/2026 art.I alin.(pct. 1)", "HG 1/2016 art.norme art.321 lit.e"):
        assert RAU.search(rau), rau
    for bun in ("OMFP 2634/2015 anexa 1 pct.24", "OUG 89/2025 art.III alin.(4) lit.b", "CF art.146 alin.(5^6)", "OMFP 1802/2014 pct.111-116",
                "OPANAF 592/2016", "CF art.LXVI", "HG 1/2016 titlul VII pct.101 alin.(1) lit.e", "OMFP 2634/2015 anexa 2 cod 14-1-2"):
        assert not RAU.search(bun), bun


def test_compunerea_pune_prefixul_numai_pe_numar_si_litera():
    """CLAUDE.md §3.1: `OMFP 1802/2014 pct.22 alin.(1)` (normele pe puncte), `OPANAF 602/2026 art.I pct.1`, `OMFP 2634/2015 anexa 2 cod
    14-1-2`; articolul arab / roman și litera păstrează prefixul. MUTAȚIE: „art.” pus din nou necondiționat -> pică."""
    assert _citare_temei("OMFP", 1802, 2014, "pct.22", "1", None) == "OMFP 1802/2014 pct.22 alin.(1)"
    assert _citare_temei("OPANAF", 602, 2026, "I", "pct. 1", None) == "OPANAF 602/2026 art.I pct.1"
    assert _citare_temei("OMFP", 2634, 2015, "anexa 2", None, "cod 14-1-2") == "OMFP 2634/2015 anexa 2 cod 14-1-2"
    assert _citare_temei("HG", 1, 2016, "norme art.321", None, "e") == "HG 1/2016 norme art.321 lit.e"
    assert _citare_temei("CF", None, None, "146", "5^6", None) == "CF art.146 alin.(5^6)"
    assert _citare_temei("OUG", 89, 2025, "III", "4", "b") == "OUG 89/2025 art.III alin.(4) lit.b"
