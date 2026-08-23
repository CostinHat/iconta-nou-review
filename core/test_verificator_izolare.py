# -*- coding: utf-8 -*-
"""GARDĂ PESTE VERIFICATOR: analizorul lui de izolare clasifică corect rute known-good / known-bad.

**Datoria din 31.07.2026** (`core/test_datorie.py`) o cere pe nume: *„`verificator_conformitate.py` a
produs 13 fals-pozitive prin propriul bug — regexul de rute rata `async def` și a marcat 13 rute ca
fără `schema_tenant` când ele îl aveau. **Instrumentul care MĂSOARĂ conformitatea nu e el însuși
măsurat**: niciun test nu verifică că analizorul clasifică corect. Un gard cu fals-pozitive se
dezactivează și moare; un gard cu fals-NEGATIVE tace pe un leak real."* Deschisă **23 de zile**.

E cea mai veche instanță a **interdicției 76** — un instrument fără calibrare pe propriul mod de eșec —
și cea mai expusă: verificatorul rulează la **fiecare poartă** și e citat în fiecare raport.

CUM E POSIBIL TESTUL: analiza a fost **extrasă în `analiza_izolare(rad)`** pe 23.08, fără schimbare de
comportament (dovedit prin comparația ieșirii, identică octet cu octet). Testele cheamă **logica
reală**, nu o copie — o reimplementare ar fi fost logică paralelă, adică exact ce nu se face.

AMBELE DIRECȚII, fiindcă un gard poate greși în două feluri:
  FALS-POZITIV  — acuză o rută care ARE acces  → gardul se dezactivează și moare
  FALS-NEGATIV  — tace pe o rută care N-ARE    → gardul tace pe un leak real
"""
import importlib.util
import pathlib
import textwrap

import pytest

_CALE = pathlib.Path(__file__).resolve().parents[1] / "verificator_conformitate.py"


@pytest.fixture(scope="module")
def vc():
    spec = importlib.util.spec_from_file_location("verificator_conformitate", _CALE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)      # ruleaza si auditul; ne interesează doar funcția
    return m


def _scrie(rad, nume, cod):
    (rad / nume).write_text(textwrap.dedent(cod).lstrip("\n"), encoding="utf-8")


def test_ruta_fara_acces_e_prinsa(tmp_path, vc):
    """KNOWN-BAD. Rută cu {tenant_id} care deschide conexiunea fără să rezolve accesul."""
    _scrie(tmp_path, "rute_rele.py", '''
        @app.get("/tenants/{tenant_id}/secret")
        def citeste_secret(tenant_id: int):
            with db.get_conn() as conn:
                return conn.execute("select 1")
        ''')
    gap = vc.analiza_izolare(str(tmp_path))["gap"]
    assert any(d == "citeste_secret" for _f, _p, d in gap), (
        "FALS-NEGATIV: o rută {tenant_id} care atinge baza fără acces n-a fost prinsă. "
        "Gardul ar tăcea pe un leak real. Găsit: %s" % gap)


def test_ruta_cu_schema_tenant_nu_e_acuzata(tmp_path, vc):
    """KNOWN-GOOD. Rezolvă accesul direct."""
    _scrie(tmp_path, "rute_bune.py", '''
        @app.get("/tenants/{tenant_id}/ok")
        def citeste_ok(tenant_id: int, ctx=Depends(cere_cabinet)):
            with db.get_conn() as conn:
                schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
                return schema
        ''')
    gap = vc.analiza_izolare(str(tmp_path))["gap"]
    assert not gap, "FALS-POZITIV: o rută care rezolvă accesul a fost acuzată: %s" % gap


def test_ruta_async_nu_e_fals_pozitiv(tmp_path, vc):
    """CAZUL DATORIEI, pinat pe nume: `async def`.

    Ăsta e chiar bug-ul din 31.07 — regexul rata `async def` și marca 13 rute conforme ca fiind fără
    acces. Dacă testul ăsta cade, gardul a redevenit un producător de fals-pozitive."""
    _scrie(tmp_path, "rute_async.py", '''
        @app.get("/tenants/{tenant_id}/async-ok")
        async def citeste_async(tenant_id: int, ctx=Depends(cere_cabinet)):
            with db.get_conn() as conn:
                schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
                return schema
        ''')
    gap = vc.analiza_izolare(str(tmp_path))["gap"]
    assert not gap, (
        "FALS-POZITIV pe `async def` — exact regresia din 31.07.2026, cea care a marcat 13 rute "
        "conforme ca fără acces: %s" % gap)


def test_ruta_ASYNC_fara_acces_e_prinsa(tmp_path, vc):
    """CAZUL DATORIEI, forma care CHIAR cade la mutație — și prima mea fixtură n-o avea.

    RED-proof-ul din 23.08 a arătat că fixtura precedentă pe `async def` **nu se aprinde** dacă
    regexurile pierd `(?:async )?`: cu mutația, granița corpului nu se mai găsește, ruta e **sărită**,
    și atunci un fals-POZITIV nu apare — dar apare unul **NEGATIV**, care e mai rău: *gardul tace pe o
    rută fără acces*. Deci calibrarea trebuie făcută pe ruta async **care N-ARE acces**, nu pe cea
    care îl are.

    Prima formă a fixturilor avea calibrare **cu numele, nu cu efectul** — interdicția 76 aplicată
    propriei gărzi, la o oră după ce a fost scrisă.
    """
    # SQL-ul fixturii nu numeste tabele reale (`select 1`, nu `select * from facturi`):
    # `test_schema_coloane` scaneaza sirurile SQL din TOT codul si nu poate deosebi o fixtura
    # de cod de productie. M-a prins pe 23.08, corect, la prima poarta dupa ce am scris-o.
    _scrie(tmp_path, "rute_async_rele.py", '''
        @app.get("/tenants/{tenant_id}/async-leak")
        async def scurge_async(tenant_id: int):
            with db.get_conn() as conn:
                return conn.execute("select 1")
        ''')
    gap = vc.analiza_izolare(str(tmp_path))["gap"]
    assert any(d == "scurge_async" for _f, _p, d in gap), (
        "FALS-NEGATIV pe `async def`: o rută care atinge baza fără acces a fost SĂRITĂ. Asta e forma "
        "periculoasă a bug-ului din 31.07 — gardul tace pe un leak real. Găsit: %s" % gap)


def test_ruta_care_nu_atinge_baza_nu_e_acuzata(tmp_path, vc):
    """KNOWN-GOOD. Fără `get_conn(` nu are ce să scurgă."""
    _scrie(tmp_path, "rute_fara_db.py", '''
        @app.get("/tenants/{tenant_id}/eticheta")
        def doar_text(tenant_id: int):
            return {"eticheta": "fara baza"}
        ''')
    assert not vc.analiza_izolare(str(tmp_path))["gap"]


def test_acces_prin_resolver_definit_aiurea_e_recunoscut(tmp_path, vc):
    """KNOWN-GOOD, forma indirectă: accesul se rezolvă printr-o funcție din alt fișier."""
    _scrie(tmp_path, "resolver.py", '''
        def rezolva_acces(conn, uid, tenant_id):
            return auth_api.schema_tenant(conn, uid, tenant_id)
        ''')
    _scrie(tmp_path, "rute_indirect.py", '''
        @app.get("/tenants/{tenant_id}/indirect")
        def prin_resolver(tenant_id: int, ctx=Depends(cere_cabinet)):
            with db.get_conn() as conn:
                return rezolva_acces(conn, ctx["uid"], tenant_id)
        ''')
    gap = vc.analiza_izolare(str(tmp_path))["gap"]
    assert not gap, "FALS-POZITIV: accesul prin resolver nu e recunoscut: %s" % gap


def test_router_nemontat_e_semnalat(tmp_path, vc):
    """Un `APIRouter` definit și nemontat înseamnă rute pe care nimeni nu le-a verificat."""
    _scrie(tmp_path, "router_orfan.py", '''
        rut = APIRouter()

        @rut.get("/tenants/{tenant_id}/x")
        def ceva(tenant_id: int):
            return 1
        ''')
    meta = vc.analiza_izolare(str(tmp_path))["meta"]
    assert any(rv == "rut" for _f, rv in meta), "routerul nemontat n-a fost semnalat: %s" % meta


def test_analiza_nu_e_vida_pe_codul_real(vc):
    """ANTI-VACUU. Pe codebase-ul real analiza trebuie să VADĂ ceva: dacă walk-ul se rupe, gap-ul e
    gol și gardul raportează verde despre o lume pe care n-o vede."""
    rez = vc.analiza_izolare(str(_CALE.parent))
    assert len(rez["route_files"]) >= 1, "niciun fișier cu rute găsit — walk-ul s-a rupt"
    assert len(rez["resolveri"]) >= 50, (
        "doar %d resolveri — detectarea lor s-a rupt, iar atunci fiecare rută ar părea fără acces"
        % len(rez["resolveri"]))
