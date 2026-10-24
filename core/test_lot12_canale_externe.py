# -*- coding: utf-8 -*-
"""GARD — clasa 598 (lotul 12): textul unei excepții tehnice nu ajunge pe ecranul contabilului.

598: „La eșecul WhatsApp, mesajul îi cere contabilului să-și verifice numărul și arată termeni tehnici; trebuie spus că WhatsApp nu e
disponibil și notificările vin pe email.” Clasa: orice eșec al unui canal extern (WhatsApp, email, SPV, REGES, VIES) spus omului cu
textul excepției (`f"REGES: {e}"`, `str(e)`), în loc de ce s-a întâmplat și ce face (CLAUDE.md §9: „fără termeni de programator”).
Detaliul tehnic merge în jurnal (`observare.esec_secundar`).

Ce prinde: în `core/*.py` (fără teste), un `raise _erori.<Clasă>(…)` din interiorul unui `except … as <v>` al cărui argument folosește
variabila excepției direct (`v`, `str(v)`, `f"…{v}"`, `"%s" % v`). Nu prinde o excepție trecută printr-o funcție care o traduce
(`anaf_api.mesaj_indisponibil(e)`): acolo traducerea e explicită, într-un singur loc.
LIMITĂ: `ValueError` / `DateInvalide` cu textul unei validări a NOASTRE (scris pentru om) e legitim — de aceea garda privește numai
erorile de serviciu extern (`ServiciuStrainCazut`), clasa 598.
"""
import ast
import glob
import os

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLASE_EXTERNE = {"ServiciuStrainCazut"}


def _foloseste_direct(nod, var):
    """Variabila excepției apare în argument altfel decât ca argument al unui apel de funcție care o traduce."""
    for n in ast.walk(nod):
        if isinstance(n, ast.Call) and not (isinstance(n.func, ast.Name) and n.func.id == "str"):
            # un apel (alt decât str) primește excepția: traducerea e a lui — nu se coboară în argumentele lui
            if any(isinstance(a, ast.Name) and a.id == var for a in n.args):
                return False
    return any(isinstance(n, ast.Name) and n.id == var for n in ast.walk(nod))


def scurgeri(src, cale="<src>"):
    """PURĂ. [(cale, linie)] — `raise _erori.<extern>(…v…)` în `except … as v`."""
    out = []
    for h in ast.walk(ast.parse(src)):
        if not (isinstance(h, ast.ExceptHandler) and h.name):
            continue
        for n in ast.walk(h):
            if (isinstance(n, ast.Raise) and isinstance(n.exc, ast.Call) and isinstance(n.exc.func, ast.Attribute)
                    and n.exc.func.attr in CLASE_EXTERNE
                    and any(_foloseste_direct(a, h.name) for a in list(n.exc.args) + [k.value for k in n.exc.keywords])):
                out.append((cale, n.lineno))
    return out


def test_def_598_nicio_exceptie_a_unui_serviciu_extern_pe_ecran():
    """MUTAȚIE: `raise _erori.ServiciuStrainCazut(f"REGES: {e}")` pus înapoi în `core/uc_tenants.py` -> pică, numind linia."""
    rele = []
    for f in sorted(glob.glob(os.path.join(_RAD, "core", "*.py"))):
        if os.path.basename(f).startswith("test_"):
            continue
        rele += scurgeri(open(f, encoding="utf-8").read(), os.path.relpath(f, _RAD))
    assert not rele, "textul excepției unui serviciu extern ajunge pe ecran (clasa 598): %s" % rele


def test_garda_scurgerilor_nu_e_vida():
    """Anti-vacuu: prinde formele textului brut și lasă traducerea explicită."""
    rau = ("try:\n    x()\nexcept Exception as e:\n    raise _erori.ServiciuStrainCazut(f'REGES: {e}')\n",
           "try:\n    x()\nexcept Exception as e:\n    raise _erori.ServiciuStrainCazut(str(e))\n",
           "try:\n    x()\nexcept Exception as e:\n    raise _erori.ServiciuStrainCazut('VIES: %s' % e)\n")
    bun = ("try:\n    x()\nexcept Exception as e:\n    raise _erori.ServiciuStrainCazut(anaf_api.mesaj_indisponibil(e))\n",
           "try:\n    x()\nexcept Exception as e:\n    _obs.esec_secundar('x', e)\n    raise _erori.ServiciuStrainCazut('REGES nu a răspuns.')\n")
    assert all(scurgeri(s) for s in rau)
    assert not any(scurgeri(s) for s in bun)
