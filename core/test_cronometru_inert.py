# -*- coding: utf-8 -*-
"""core/test_cronometru_inert.py — instrumentarea nu se vede în producție.

**CE PĂZEȘTE.** `core/cronometru.py` e cod de măsurare așezat pe calea de cerere, aprobat separat de
arhitect pe 10.09.2026 fiindcă din afară nu se putea afla unde stau cele ~460 ms ale unei cereri la
k=10. Un asemenea cod are o singură obligație absolută: **să nu existe când nu e pornit**.

**Probele nu se opresc la «ACTIV e False».** Cea care contează e a treia: răspunsul unei rute
instrumentate e **octet cu octet ȘI antet cu antet** cel pe care l-ar fi produs FastAPI, atâta timp
cât instrumentarea e stinsă. *O măsurătoare care schimbă lucrul măsurat nu măsoară nimic — iar una
care schimbă răspunsul livrat clientului e mai rea decât nicio măsurătoare.*

**Și cealaltă direcție:** cu instrumentarea PORNITĂ, reperele chiar apar. Altfel garda ar fi verde
pe un modul mort, iar prima măsurătoare de mâine ar raporta segmente goale.
"""
import ast
import io
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)

from core import cronometru as C  # noqa: E402


def _main_ast():
    return ast.parse(io.open(os.path.join(RAD, "main.py"), encoding="utf-8").read())


def _functie(nume):
    for n in ast.walk(_main_ast()):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == nume:
            return n
    return None


# ═══════════════════════════════════════════════════════════════════════════
#  STINSĂ — starea în care rulează producția
# ═══════════════════════════════════════════════════════════════════════════

def test_e_stinsa_implicit():
    """Fără `ICONTA_CRONOMETRU=1`, tot modulul e inert. Suita rulează fără variabilă, deci aici."""
    assert os.environ.get("ICONTA_CRONOMETRU") != "1", (
        "suita rulează CU instrumentarea pornită — proba de mai jos n-ar spune nimic despre "
        "producție")
    assert C.ACTIV is False


def test_stinsa_nu_produce_nimic():
    """Fiecare funcție iese pe prima linie. Nimic de curățat, nimic de reținut între cereri."""
    C.porneste()
    C.marca("x")
    C.marca("y")
    assert C.segmente() == []
    assert C.antete() == {}


def test_raspunsul_e_IDENTIC_cat_timp_e_stinsa():
    """PROBA CARE CONTEAZĂ: corp ȘI antete, față de ce ar fi produs framework-ul singur.

    Nu se compară cu ce cred eu că face FastAPI, ci cu ce face el chiar acum, pe aceeași sarcină.
    """
    import asyncio

    from fastapi.responses import JSONResponse
    from fastapi.routing import serialize_response

    import main as _main
    for x in ({"randuri": [{"a": 1, "b": None}], "total": 1},
              {"tranzactii": [{"suma": 1.5} for _ in range(20)], "nr": 20}):
        astept = JSONResponse(asyncio.run(serialize_response(response_content=x)))
        primit = _main._raspuns(x)
        assert primit.body == astept.body, "corpul diferă de calea framework-ului"
        supliment = {k.lower() for k in primit.headers} - {k.lower() for k in astept.headers}
        assert not supliment, (
            "instrumentarea STINSĂ adaugă antete în răspunsul livrat: %s" % sorted(supliment))


def test_niciun_antet_de_cronometru_nu_scapa_stins():
    """Anti-vacuu pe proba de mai sus: prefixul chiar e cel căutat, nu unul inventat."""
    assert C.ANTET and C.ANTET.startswith("x-"), "prefixul antetelor s-a schimbat: %r" % C.ANTET
    import main as _main
    r = _main._raspuns({"a": 1})
    assert not [k for k in r.headers if k.lower().startswith(C.ANTET)]


# ═══════════════════════════════════════════════════════════════════════════
#  APRINSĂ — altfel garda ar fi verde pe un modul mort
# ═══════════════════════════════════════════════════════════════════════════

def test_aprinsa_chiar_masoara(monkeypatch):
    """Cealaltă direcție (METODA §22): pornită, produce reperele și le închide în antete."""
    monkeypatch.setattr(C, "ACTIV", True)
    C.porneste("start")
    C.marca("unu")
    C.marca("doi")
    h = C.antete()
    assert C.ANTET + "start" in h and C.ANTET + "end" in h, (
        "lipsesc reperele de ceas de perete — sonda n-ar putea afla ce s-a întâmplat ÎNAINTE de "
        "handler, adică exact partea care s-a dovedit cea mai mare")
    assert C.ANTET + "unu" in h and C.ANTET + "doi" in h
    assert float(h[C.ANTET + "unu"]) >= 0


def test_aprinsa_fara_porneste_nu_cade(monkeypatch):
    """Un `marca()` fără `porneste()` — cum se întâmplă pe rutele neinstrumentate — nu ridică."""
    monkeypatch.setattr(C, "ACTIV", True)
    C.segmente()          # golește starea rămasă
    C.marca("orfan")
    assert C.antete() == {} or isinstance(C.antete(), dict)


# ═══════════════════════════════════════════════════════════════════════════
#  LEGĂTURA — instrumentarea chiar e pe calea de cerere, nu doar în modul
# ═══════════════════════════════════════════════════════════════════════════

def test_cronometrul_porneste_din_cel_mai_din_AFARA_middleware():
    """Dacă ar porni mai înăuntru, segmentul `intrare` ar ascunde tocmai ce s-a dovedit mai mare.

    Se citește din AST: în `_edge_canonic_head` există un apel `_crono.porneste()`.
    """
    fn = _functie("_edge_canonic_head")
    assert fn is not None, "middleware-ul cel mai din afară a dispărut sau s-a redenumit"
    apeluri = {a.func.attr for a in ast.walk(fn)
               if isinstance(a, ast.Call) and isinstance(a.func, ast.Attribute)
               and isinstance(a.func.value, ast.Name) and a.func.value.id == "_crono"}
    assert apeluri >= {"porneste"}, (
        "cronometrul nu mai pornește din cel mai din afară middleware (apeluri găsite: %s) — "
        "`intrare` ar deveni o cutie neagră tocmai unde stă cea mai mare parte a timpului"
        % sorted(apeluri))


def test_ruta_subiect_are_reperele_ei():
    """Ruta măsurată de banc trebuie să-și păstreze reperele, altfel profilul se golește tăcut."""
    fn = _functie("banca_parse_extras")
    assert fn is not None
    marci = [a.args[0].value for a in ast.walk(fn)
             if isinstance(a, ast.Call) and isinstance(a.func, ast.Attribute)
             and a.func.attr == "marca" and a.args
             and isinstance(a.args[0], ast.Constant)]
    lipsa = {"intrare_handler", "conexiune", "acces", "parsare", "reguli"} - set(marci)
    assert not lipsa, "repere pierdute din ruta subiect: %s" % sorted(lipsa)
