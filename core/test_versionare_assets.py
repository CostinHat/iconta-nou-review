# -*- coding: utf-8 -*-
"""core/test_versionare_assets.py -- GARD pentru disciplina ?v= (versionare asseturi front-end).

CE PAZESTE (cererea lui Costin): "orice modul JS sau CSS atins poate fi statut pentru un
utilizator care revine. Vreau garda, nu doar incrementare acum." Staleness-ul devine ROSU
in suita, nu o incrementare manuala pe care o uiti.

CUM: sursa unica de logica este versioneaza_assets.py (generatorul). Aici doar RECALCULAM
hash(asset) pentru fiecare referinta si asertam ca tokenul ?v= scris == hashul curent al tintei.
  - o referinta STATUTA (cod schimbat, ?v= nu) -> ROSU cu fisier:linie, ce token e, ce ar trebui;
  - acelasi asset referit din locuri diferite -> ACELASI ?v= (consistenta);
  - nicio referinta catre un asset inexistent.

DESIGN anti-cascada: token(X) = sha1(continut_X cu ?v=... normalizate)[:10]. Deci hashul lui X
NU depinde de versiunile importatorilor sai -> stampilarea unei referinte nu schimba hashul
fisierului care o contine -> punct-fix intr-o singura trecere.
"""
import os
import sys
import collections

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

import versioneaza_assets as va  # noqa: E402  (sursa unica: generatorul din radacina)


def _rel(p):
    return os.path.relpath(p, _RAD)


def test_generator_prezent():
    """Fara generator, gardul n-are ce recalcula (santinela: importul + functiile cheie)."""
    assert hasattr(va, "descopera") and hasattr(va, "hash_asset")
    assert callable(va.descopera) and callable(va.hash_asset)


def test_hash_stabil_fata_de_versiuni():
    """DINTI pe anti-cascada: hashul NORMALIZEAZA ?v=..., deci nu depinde de versiunile din corp.
    Doua continuturi identice pana la tokenele ?v= au ACELASI hash; schimbarea CODULUI il schimba."""
    import tempfile
    def _h(txt):
        fd, p = tempfile.mkstemp(suffix=".js")
        os.close(fd)
        try:
            open(p, "w", encoding="utf-8", newline="").write(txt)
            return va.hash_asset(p)
        finally:
            os.remove(p)
    a = 'import x from "./a.js?v=111";\nconst k = 1;\n'
    b = 'import x from "./a.js?v=999zzz";\nconst k = 1;\n'   # doar ?v= difera
    c = 'import x from "./a.js?v=111";\nconst k = 2;\n'      # cod diferit
    assert _h(a) == _h(b), "hashul trebuie sa fie STABIL fata de ?v= (anti-cascada)"
    assert _h(a) != _h(c), "schimbarea CODULUI trebuie sa schimbe hashul"


def test_nicio_referinta_catre_asset_inexistent():
    refs = va.descopera()
    lipsa = ["%s:%d -> %s (%s)" % (_rel(r["src"]), r["lineno"], r["spec"], _rel(r["tinta"]))
             for r in refs if not r["exista"]]
    assert not lipsa, "referinte catre asseturi INEXISTENTE:\n  " + "\n  ".join(lipsa)


def test_fiecare_referinta_are_tokenul_hashului_curent():
    """Inima gardului: fiecare ?v= == hash(tinta). O referinta statuta (sau fara ?v=) = ROSU."""
    refs = va.descopera()
    stalute = []
    for r in refs:
        if not r["exista"]:
            continue  # acoperit de test_nicio_referinta_catre_asset_inexistent
        if r["token_curent"] != r["token_asteptat"]:
            stalute.append("  %s:%d  %s  ?v=%s  -> ar trebui ?v=%s"
                           % (_rel(r["src"]), r["lineno"], r["spec"],
                              r["token_curent"], r["token_asteptat"]))
    assert not stalute, (
        "Referinte ?v= STATUTE (cod schimbat, ?v= nu). Ruleaza "
        "`python3 versioneaza_assets.py --scrie` ca sa le re-stampilezi:\n" + "\n".join(stalute))


def test_acelasi_asset_are_acelasi_token():
    """Consistenta: toate referintele catre aceeasi tinta poarta ACELASI ?v=."""
    refs = [r for r in va.descopera() if r["exista"]]
    pe_tinta = collections.defaultdict(set)
    unde = collections.defaultdict(list)
    for r in refs:
        pe_tinta[r["tinta"]].add(r["token_curent"])
        unde[r["tinta"]].append("%s:%d(?v=%s)" % (_rel(r["src"]), r["lineno"], r["token_curent"]))
    incoerente = ["%s: %s" % (_rel(t), ", ".join(unde[t]))
                  for t, toks in pe_tinta.items() if len(toks) > 1]
    assert not incoerente, ("Acelasi asset referit cu ?v= DIFERIT (o instanta dubla a modulului):\n  "
                            + "\n  ".join(incoerente))


def test_gardul_vede_referinte():
    """Santinela: daca descoperirea intoarce 0 referinte, gardul e orb (nu ruleaza degeaba verde)."""
    refs = va.descopera()
    assert len(refs) > 50, "prea putine referinte descoperite (%d) -> descoperirea e rupta" % len(refs)
