"""[lotul 11, poarta 3] Firele de fundal pornite din drumul unei cereri trec printr-un singur loc, `db.fir_de_fundal`, oprit în suită.

CE S-A ÎNTÂMPLAT. Poarta 3 a lotului 11 a picat pe `core/test_scrieri_pana_in_declaratie.py` (două teste, „relation inregistrari does
not exist”), iar fișierul rulat singur trecea. După orice scriere reușită a cabinetului, middleware-ul din `main.py` pornea
`uc_coada.reia_in_fundal` direct cu `threading.Thread`, fără comutatorul pe care recalcularea rezumatelor îl avea din 08.10
(`ICONTA_RECALCUL_FUNDAL`). Testul înlocuiește `get_conn` cu o singură conexiune comună; firul o lua și punea `search_path` pe `public`
în mijlocul lui `d300.pull` din test. Sub încărcarea porții firul cădea în fereastra aceea; singur, nu. Reprodus determinist (firul
întârziat 0,3 s, `_pull_note_tva` 1 s): aceeași eroare.

CLASA: un fir care deschide conexiuni, pornit dintr-o cerere, rămas pornit în suită. Trei instanțe (recalcularea rezumatelor, reluarea
declarațiilor în așteptare, triajul sesizărilor), acum toate prin `db.fir_de_fundal`, oprit în suită de `ICONTA_FIRE_FUNDAL=0`
(conftest). Plasa e2e pornește aplicația cu mediul ei, fără comutator, deci acolo firele rulează ca pe producție.

LIMITA: garda citește `core/` și `main.py` (codul aplicației); `scripts/` sunt unelte de linie de comandă, fără cereri. Taskurile
`asyncio` din `lifespan` nu sunt fire și trăiesc numai cât bucla clientului de test (`with TestClient(...)`).
"""
import ast
import os
import threading

from core import db

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Ce pornește un fir sau un proces paralel.
_PORNESC_FIRE = {"Thread", "Timer", "ThreadPoolExecutor", "ProcessPoolExecutor", "start_new_thread"}

#: (fișier, funcție) care pot porni un fir direct, cu motivul.
EXCEPTII = {
    ("core/db.py", "fir_de_fundal"): "poarta unică însăși",
    ("core/observare.py", "alerteaza_in_fundal"): "numai apelul HTTP către Brevo (`_trimite_brevo`), fără bază; firul nu e daemon "
                                                  "(o alertă nu se pierde la oprire), iar `core/test_brevo_pe_fir_propriu.py` îl cere real",
}


def _fisiere_aplicatie():
    yield "main.py"
    for f in sorted(os.listdir(os.path.join(_RAD, "core"))):
        if f.endswith(".py") and not f.startswith("test_") and f != "conftest.py":
            yield "core/" + f


def _porniri_de_fire(sursa):
    """[(funcția care conține, linia)] pentru fiecare apel sau import care pornește un fir."""
    arb = ast.parse(sursa)
    gasite = []

    def viziteaza(nod, functie):
        for copil in ast.iter_child_nodes(nod):
            f = copil.name if isinstance(copil, (ast.FunctionDef, ast.AsyncFunctionDef)) else functie
            if isinstance(copil, ast.Call):
                nume = copil.func.attr if isinstance(copil.func, ast.Attribute) else getattr(copil.func, "id", None)
                if nume in _PORNESC_FIRE:
                    gasite.append((functie, copil.lineno))
            if isinstance(copil, ast.ImportFrom) and any(a.name in _PORNESC_FIRE for a in copil.names):
                gasite.append((functie, copil.lineno))
            viziteaza(copil, f)
    viziteaza(arb, None)
    return gasite


def test_niciun_fir_pornit_in_afara_portii_unice():
    """MUTAȚIE: `threading.Thread(target=_ruleaza, ...).start()` pus înapoi în `uc_coada.reia_in_fundal` -> pică, cu locul numit."""
    afara, vazute = [], set()
    for rel in _fisiere_aplicatie():
        for functie, linie in _porniri_de_fire(open(os.path.join(_RAD, rel), encoding="utf-8").read()):
            if (rel, functie) in EXCEPTII:
                vazute.add((rel, functie))
            else:
                afara.append("%s:%d (%s)" % (rel, linie, functie))
    assert not afara, ("fir pornit în afara lui `db.fir_de_fundal`: în suită ar lucra pe conexiunea comună a testului; treci-l prin "
                       "`db.fir_de_fundal` sau, dacă nu deschide conexiuni, numește-l în EXCEPTII cu motivul: %s" % afara)
    assert vazute == set(EXCEPTII), "excepții rămase fără fir (șterge-le): %s" % sorted(set(EXCEPTII) - vazute)


def test_firul_exceptat_al_alertei_nu_deschide_conexiuni():
    """Motivul excepției, verificat: `_trimite_brevo` nu atinge baza. MUTAȚIE: un `db.get_conn()` în `_trimite_brevo` -> pică."""
    arb = ast.parse(open(os.path.join(_RAD, "core", "observare.py"), encoding="utf-8").read())
    fn = next(n for n in ast.walk(arb) if isinstance(n, ast.FunctionDef) and n.name == "_trimite_brevo")
    atinge = sorted({n.attr for n in ast.walk(fn) if isinstance(n, ast.Attribute) and n.attr in {"get_conn", "pool", "connect"}})
    assert not atinge, "`_trimite_brevo` deschide conexiuni (%s): firul alertei trebuie să treacă prin `db.fir_de_fundal`" % atinge


def test_suita_nu_porneste_fire_de_fundal():
    """Comutatorul e pus de conftest pentru toată suita. MUTAȚIE: `os.environ.setdefault("ICONTA_FIRE_FUNDAL", "0")` scos -> pică
    (și reproducerea porții 3 iese din nou roșie)."""
    assert os.environ.get("ICONTA_FIRE_FUNDAL") == "0"
    assert db.fire_de_fundal_permise() is False


def test_poarta_porneste_numai_cand_e_permis(monkeypatch):
    chemat, gata = [], threading.Event()

    def tinta(*a):
        chemat.append(a)
        gata.set()
    monkeypatch.setenv("ICONTA_FIRE_FUNDAL", "0")
    assert db.fir_de_fundal(tinta, 1, 2, nume="proba") is False
    assert chemat == []
    monkeypatch.setenv("ICONTA_FIRE_FUNDAL", "1")
    assert db.fir_de_fundal(tinta, 1, 2, nume="proba") is True
    assert gata.wait(5) and chemat == [(1, 2)]


def test_reluarea_declaratiilor_dupa_scriere_trece_prin_poarta(monkeypatch):
    """Instanța din poarta 3: firul pornit de middleware după orice scriere a cabinetului."""
    from core import uc_coada
    chemat, gata = [], threading.Event()

    def spion(cabinet_id):
        chemat.append(cabinet_id)
        gata.set()
    monkeypatch.setattr(uc_coada, "reia_declaratiile_in_asteptare", spion)
    monkeypatch.setenv("ICONTA_FIRE_FUNDAL", "0")
    assert uc_coada.reia_in_fundal(7) is False
    assert chemat == []
    monkeypatch.setenv("ICONTA_FIRE_FUNDAL", "1")
    assert uc_coada.reia_in_fundal(7) is True
    assert gata.wait(5) and chemat == [7]
