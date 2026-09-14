# -*- coding: utf-8 -*-
"""E6 — `core/` nu mai depinde de stratul HTTP. `CORE_IMPORTA_MAIN = 0`.

CE ERA, și de ce nu era teoretic. `core/firma_rezumat.py` — lucrătorul modelului de citire — făcea
`import main` în două locuri și cerea de acolo trei nume: `_construieste_contabil`, `pastila_firma`,
`_termene_una_firma`. Stratul de sub HTTP depindea de stratul HTTP.

**Prețul a fost deja plătit o dată.** În valul use-case, o curățenie automată de importuri a scos din
`main.py` re-exportul `pastila_firma` — nefolosit *acolo* —, iar lucrătorul a început să dea
`AttributeError`: **șase firme** au ajuns cu `control_fiscal` în stare de eroare. A prins-o
`core/test_paritate_p2.py`, care refuză să compare un verdict cu o absență. Reparația de atunci a
fost să se pună importul la loc, cu `# noqa` — adică să se păstreze inversarea. E6 o scoate.

CE PĂZEȘTE GARDA ASTA, și de ce citește AST-ul, nu textul: după mutare, în `core/firma_rezumat.py`
a rămas un COMENTARIU care spune «îl cerea prin `import main`». Un `grep` l-ar număra drept import
și ar raporta 1 acolo unde codul are 0 — iar o gardă care se înșală în direcția asta se dezactivează
singură prin zgomot. Se citesc nodurile `Import`/`ImportFrom`, deci proza nu poate nici să aprindă,
nici să stingă cifra.

DOMENIUL, scris ca să nu fie citit mai larg decât e: **`core/`, fără probe**. `scripts/` NU intră —
acolo trăiesc unelte care pornesc aplicația ca s-o măsoare (`proba_*.py`, `masoara_*.py`), iar un
instrument care importă aplicația nu e o inversare de strat, e un instrument.
"""
from __future__ import annotations

import ast
import io
import os

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _surse_core():
    cdir = os.path.join(RADACINA, "core")
    for f in sorted(os.listdir(cdir)):
        if f.endswith(".py") and not f.startswith("test_"):
            cale = os.path.join(cdir, f)
            yield cale, io.open(cale, encoding="utf-8", errors="ignore").read()


def importurile_de_main(surse=None):
    """[(fișier, linia, cum)] — importuri REALE ale stratului HTTP din `core/`."""
    out = []
    for cale, text in (surse if surse is not None else _surse_core()):
        try:
            arb = ast.parse(text)
        except SyntaxError:
            continue
        rel = os.path.relpath(cale, RADACINA) if os.path.isabs(cale) else cale
        for n in ast.walk(arb):
            if isinstance(n, ast.Import):
                for a in n.names:
                    if a.name == "main" or a.name.startswith("main."):
                        out.append((rel, n.lineno, "import %s" % a.name))
            elif isinstance(n, ast.ImportFrom):
                if (n.module or "") == "main" and n.level == 0:
                    out.append((rel, n.lineno, "from main import %s"
                                % ", ".join(a.name for a in n.names)))
    return out


def test_CORE_IMPORTA_MAIN_e_zero():
    """Criteriul de ieșire al lui E6, scris ca cifră."""
    gasite = importurile_de_main()
    assert not gasite, (
        "module din `core/` care importă stratul HTTP (%d) — stratul de sub HTTP nu are voie să "
        "depindă de el:\n  %s"
        % (len(gasite), "\n  ".join("%s:%d  %s" % g for g in gasite)))


def test_CALIBRARE_detectorul_vede_amandoua_formele_si_NU_proza():
    """Pe univers FABRICAT, în ambele direcții — inclusiv direcția care contează aici.

    A treia probă e cea care justifică AST-ul: un comentariu care POMENEȘTE importul nu-l aprinde.
    Fix cazul din `core/firma_rezumat.py` după mutare."""
    rau = [("zt_rau.py", "import main as _m\nfrom main import pastila_firma\n\n"
                         "def f():\n    return _m.x\n")]
    gasite = importurile_de_main(rau)
    assert len(gasite) == 2, "detectorul a găsit %d din 2 forme: %s" % (len(gasite), gasite)

    bun = [("zt_bun.py", "from core import uc_comun as _uc\n\n"
                         "def f():\n    return _uc.y\n")]
    assert not importurile_de_main(bun), "forma CORECTĂ e raportată ca defect"

    proza = [("zt_proza.py", "# lucrătorul îl cerea prin `import main` — inversare de strat\n"
                             '"""Docstring care spune: from main import x."""\n'
                             "def f():\n    return 1\n")]
    assert not importurile_de_main(proza), (
        "un comentariu care POMENEȘTE importul e numărat ca import — garda ar raporta despre proză")


def test_cele_trei_nume_se_cer_de_unde_SUNT():
    """Anti-vacuum pe reparație: nu doar că importul a dispărut, ci că numele vin de la sursă.

    Fără proba asta, `CORE_IMPORTA_MAIN = 0` s-ar putea obține și ștergând apelurile — adică
    stingând funcționalitatea, nu inversarea."""
    from core import common as _common
    from core import firma_rezumat as _fr
    from core import uc_comun as _uc_comun

    assert callable(getattr(_common, "pastila_firma", None)), (
        "`pastila_firma` nu mai e în `core/common.py` — lucrătorul o cere de acolo")
    assert callable(getattr(_uc_comun, "_construieste_contabil", None)), (
        "`_construieste_contabil` nu mai e în `core/uc_comun.py`")
    assert callable(getattr(_fr, "_termene_una_firma", None)), (
        "`_termene_una_firma` n-a ajuns în `core/firma_rezumat.py`, lângă singurul ei apelant")

    import main
    assert not hasattr(main, "_termene_una_firma"), (
        "`_termene_una_firma` a rămas ȘI în `main.py` — două definiții ale aceleiași cifre")


def test_functia_mutata_e_CHEMATA_de_recalculeaza_greu():
    """Mutarea n-a rupt legătura: apelul e acolo, pe numele local, nu pe un modul.

    Se citește AST-ul lui `recalculeaza_greu`, nu textul fișierului."""
    from core import firma_rezumat as _fr
    arb = ast.parse(io.open(_fr.__file__, encoding="utf-8").read())
    fn = next((n for n in arb.body
               if isinstance(n, ast.FunctionDef) and n.name == "recalculeaza_greu"), None)
    assert fn is not None, "`recalculeaza_greu` a dispărut"
    apeluri = {getattr(x.func, "id", None) or getattr(x.func, "attr", None)
               for x in ast.walk(fn) if isinstance(x, ast.Call)}
    # Diferență de mulțimi, nu trei `"nume" in apeluri`: numește dintr-o dată tot ce lipsește și nu
    # ancorează pe niciun șir — clichetul 50 numără forma aia, și are dreptate s-o numere.
    lipsa = {"_termene_una_firma", "_construieste_contabil", "pastila_firma"} - apeluri
    assert not lipsa, (
        "`recalculeaza_greu` nu mai cheamă %s — mutarea a rupt legătura, iar CORE_IMPORTA_MAIN=0 "
        "s-ar fi obținut stingând funcționalitatea" % ", ".join(sorted(lipsa)))
