# -*- coding: utf-8 -*-
"""GARD (lotul 11, E2F) — profilul „complet” al firmelor de probă din plasa e2e ține pasul cu câmpurile obligatorii din Date firmă.

DE CE: la decizia Costin 10.3 pct.4 (verbatim în DECIZII „Comanda 10.3”: „Întocmitorul bilanțului: calitatea întocmitorului în profilul
cabinetului, interesul public în Date firmă; ambele blochează dacă lipsesc.”) „Entitate de interes public” a intrat în
`firma_profil_api.OBLIGATORII`. Profilul pe care plasa îl numește complet (`e2e_bloc_a._profil`, `e2e_bloc_b._firma_gata`) n-a primit
câmpul, deci după salvare Date firmă spunea „Salvat. Lipsește Entitate de interes public — blochează Bilanț.” în loc de „Datele firmei au
fost salvate.”, iar patru teste e2e (10, 19, 37, 61) au așteptat 20 s un mesaj care nu mai venea — eșecul s-a văzut abia după plasa
întreagă (o oră), ca timeout, nu ca lipsă numită. Același lucru se întâmplase la C69 (lotul 10: „mare contribuabil”, „forma de
proprietate”). Clasa: un câmp obligatoriu nou, fără profilul complet al plasei actualizat.

CE FACE: citește (AST, fără bază și fără browser) dicționarele pe care cele două ajutătoare le trimit pe rutele Date firmă și cere ca
`firma_profil_api.lipsuri` să nu găsească nimic în ele (plus denumirea și CUI-ul, pe care firma de probă le are de la creare). Un câmp
obligatoriu nou fără valoare în aceste profiluri face garda ROȘIE, cu numele câmpului.

LIMITĂ DECLARATĂ: valorile care nu sunt constante în sursă (variabile, expresii) se socotesc completate; garda vede numai cheile și
constantele. Profilurile lăsate intenționat incomplete (`e2e_bloc_c.firma_gv`, `e2e_lot11_p.firma_p` — testele lor completează lipsurile pe
ecran) nu intră aici."""
import ast
import os

from core import firma_profil_api as fp

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_E2E = os.path.join(_RAD, "frontend_test", "e2e")
_NECONSTANT = "valoare-din-cod"


def _dict(nod):
    """Dicționarul literal din sursă: constantele așa cum sunt, restul -> o valoare nevidă."""
    out = {}
    for k, v in zip(nod.keys, nod.values):
        if isinstance(k, ast.Constant) and isinstance(k.value, str):
            out[k.value] = v.value if isinstance(v, ast.Constant) else _NECONSTANT
    return out


def _functie(fisier, nume):
    arbore = ast.parse(open(os.path.join(_E2E, fisier), encoding="utf-8").read())
    return next(n for n in ast.walk(arbore) if isinstance(n, ast.FunctionDef) and n.name == nume)


def profil_bloc_a():
    """`e2e_bloc_a._profil(forma=True)`: `p = {…}` + `p.update({…})` din ramura `if forma`."""
    f = _functie("e2e_bloc_a.py", "_profil")
    p = {}
    for n in ast.walk(f):
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "p" for t in n.targets) and isinstance(n.value, ast.Dict):
            p.update(_dict(n.value))
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "update"
                and isinstance(n.func.value, ast.Name) and n.func.value.id == "p" and n.args and isinstance(n.args[0], ast.Dict)):
            p.update(_dict(n.args[0]))
    return p


def profil_bloc_b():
    """`e2e_bloc_b._firma_gata`: dicționarul trimis lui `_profil(firma, {…})` (`salveaza_date`)."""
    f = _functie("e2e_bloc_b.py", "_firma_gata")
    for n in ast.walk(f):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "_profil" and len(n.args) > 1 \
                and isinstance(n.args[1], ast.Dict):
            return _dict(n.args[1])
    raise AssertionError("e2e_bloc_b._firma_gata nu mai salvează profilul prin `_profil(firma, {…})` — garda trebuie refăcută")


def _lipsuri(p):
    # firma de probă are denumirea și CUI-ul de la creare (`provision_tenant`) și e societate (SRL)
    return [x["camp"] for x in fp.lipsuri(dict({"nume": "E2E Probă SRL", "cui": "14399840", "tip_firma": "srl"}, **p))]


def test_profilul_complet_din_bloc_a_n_are_lipsuri():
    p = profil_bloc_a()
    assert "reg_com" in p and "forma_juridica" in p, p   # garda chiar a citit dicționarele
    # decizia Costin 10.3 pct.4: „interesul public în Date firmă; ambele blochează dacă lipsesc” (`firma_profil_api.OBLIGATORII`)
    assert _lipsuri(p) == [], "profilul complet al plasei (e2e_bloc_a._profil) nu are: %s" % _lipsuri(p)


def test_profilul_complet_din_bloc_b_n_are_lipsuri():
    p = profil_bloc_b()
    assert "reg_com" in p and "forma_juridica" in p, p
    assert _lipsuri(p) == [], "profilul complet al plasei (e2e_bloc_b._firma_gata) nu are: %s" % _lipsuri(p)


def test_garda_vede_un_camp_obligatoriu_lipsa():
    """Non-tautologie: același profil, fără „Entitate de interes public”, are lipsa numită."""
    p = profil_bloc_a()
    p.pop("interes_public", None)
    assert _lipsuri(p) == ["interes_public"], _lipsuri(p)
