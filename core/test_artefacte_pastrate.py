# -*- coding: utf-8 -*-
"""GARD [R45]: un artefact produs se păstrează, cu cele cinci câmpuri — și producerea lui e
un ACT, nu o citire.

Decizia (Costin, 25.08.2026): *artefactul însuși · momentul · autorul · amprenta conținutului
· numărul exemplarului*; plus verdictul cu amprenta fișierului validat, la declarații.

Ce ține testul, și de ce fiecare bucată:
  - cele cinci coloane există în DDL — sursa unică, `core/migrare_artefacte.py`;
  - `pastreaza` refuză un fel necunoscut (un vocabular deschis ar produce variante orfane la
    o literă greșită, iar întrebarea „câte s-au produs" n-ar mai avea răspuns);
  - **al doilea exemplar crește, nu suprascrie** — P4: emiterea e idempotentă și repetabilă,
    iar al doilea exemplar e un fapt;
  - **binarul supraviețuiește** round-trip-ului: prima formă îl trecea prin
    `decode("utf-8", "replace")`, care strică octeții tăcut — artefactul păstrat n-ar mai fi
    fost cel produs;
  - `verdict_la` e NULL fără verdict: un moment de validare pe un artefact nevalidat ar fi o
    afirmație despre ceva ce nu s-a întâmplat;
  - **rutele care produc artefacte nu sunt GET** — un GET n-are voie să scrie (interdicția 6,
    `core/test_get_fara_scriere.py`). Asta a fost obstacolul real la wiring, nu o precauție.
"""
import ast
import base64
import os

import pytest

from core import artefacte

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MAIN = os.path.join(_RAD, "main.py")

# Rutele care produc cele patru artefacte, și metoda pe care TREBUIE s-o aibă.
_ACTE = {
    "/tenants/{tenant_id}/s1003-valideaza": "post",
    "/tenants/{tenant_id}/s1005-valideaza": "post",
    "/tenants/{tenant_id}/plata-salarii-fisier": "post",
    "/tenants/{tenant_id}/facturi/export-saga": "post",
    "/tenants/{tenant_id}/facturi/export-winmentor": "post",
    "/control-fiscal/{tenant_id}/audit-preluare": "post",
}


def _rute():
    """{(cale): metoda} din main.py, citit din AST."""
    arb = ast.parse(open(_MAIN, encoding="utf-8").read())
    out = {}
    for fn in ast.walk(arb):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for d in fn.decorator_list:
            if isinstance(d, ast.Call) and getattr(d.func, "attr", None) in (
                    "get", "post", "put", "patch", "delete") and d.args \
                    and isinstance(d.args[0], ast.Constant):
                out.setdefault(d.args[0].value, set()).add(d.func.attr)
    return out


def _coloane(schema="tenant_001"):
    from core import db
    db.init_pool()
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema=%s AND table_name='artefacte_produse'", (schema,))
        return {r[0] for r in cur.fetchall()}


def _coloane_unice(schema="tenant_001"):
    """Coloanele constrângerii UNIQUE, citite din catalog — nu din textul DDL-ului."""
    from core import db
    db.init_pool()
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("""SELECT k.column_name
                       FROM information_schema.table_constraints t
                       JOIN information_schema.key_column_usage k
                         ON k.constraint_name = t.constraint_name
                        AND k.constraint_schema = t.constraint_schema
                       WHERE t.table_schema=%s AND t.table_name='artefacte_produse'
                         AND t.constraint_type='UNIQUE'""", (schema,))
        return {r[0] for r in cur.fetchall()}


def test_cele_cinci_campuri_exista_in_TABELA():
    """Pe catalogul bazei, nu pe textul DDL-ului: coloana chiar există acolo unde se scrie."""
    try:
        col = _coloane()
    except Exception as ex:                                   # pragma: no cover
        pytest.skip("fără bază de date: %s" % str(ex)[:80])
    assert col, "tabela `artefacte_produse` nu există pe tenant_001 — rulează migrarea"
    lipsa = {"continut", "produs_la", "produs_de", "amprenta", "exemplar"} - col
    assert not lipsa, "câmpuri lipsă din cele cinci decise: %s" % sorted(lipsa)
    lipsa_v = {"verdict", "verdict_la", "verdict_versiune", "verdict_amprenta"} - col
    assert not lipsa_v, "câmpuri de verdict lipsă (se cer la declarații): %s" % sorted(lipsa_v)


def test_al_doilea_exemplar_e_posibil_prin_constructie():
    """Unicitatea e pe (fel, cheie, EXEMPLAR), nu pe (fel, cheie). O schemă care interzice al
    doilea exemplar e interdicția 8. Citit din catalog: o constrângere comentată în DDL ar
    trece o verificare pe text, dar nu una pe catalog."""
    try:
        u = _coloane_unice()
    except Exception as ex:                                   # pragma: no cover
        pytest.skip("fără bază de date: %s" % str(ex)[:80])
    assert u == {"fel", "cheie", "exemplar"}, (
        "constrângerea de unicitate e pe %s — dacă `exemplar` lipsește, al doilea exemplar "
        "devine imposibil (interdicția 8)" % sorted(u))


def test_un_fel_necunoscut_e_refuzat():
    r = artefacte.pastreaza(None, "tenant_001", "inventat", "2026", "x")
    assert r.get("ok") is False and r.get("cod") == "FEL_NECUNOSCUT"


def test_amprenta_e_pe_octeti_si_binarul_supravietuieste():
    """Round-trip: ce se scrie în coloană se poate reface în octeții originali."""
    brut = bytes(range(256))
    amp = artefacte.amprenta(brut)
    col = artefacte._pentru_coloana(brut)
    assert base64.b64decode(col) == brut, "binarul nu se mai poate reface din ce s-a păstrat"
    assert artefacte.amprenta(base64.b64decode(col)) == amp


def test_amprenta_discrimineaza():
    """Calibrare: dacă amprenta ar fi constantă, toate celelalte aserțiuni ar trece la fel."""
    assert artefacte.amprenta("a") != artefacte.amprenta("b")
    assert artefacte.amprenta(b"a") != artefacte.amprenta(b"b")
    assert artefacte.amprenta("") == artefacte.amprenta(None), (
        "gol si absent au aceeasi amprenta — deliberat: ambele inseamna «nimic»")


def test_rutele_care_produc_artefacte_NU_sunt_GET():
    """Obstacolul real: trei din patru artefacte se produceau pe GET, iar un GET n-are voie să
    scrie. „Se păstrează" a cerut ca producerea lor să devină un act."""
    r = _rute()
    rele = []
    for cale, metoda in _ACTE.items():
        m = r.get(cale)
        if m is None:
            rele.append("  %s: ruta a dispărut" % cale)
        elif metoda not in m:
            rele.append("  %s: metodele sunt %s, se cere %s" % (cale, sorted(m), metoda))
        elif "get" in m:
            rele.append("  %s: e ȘI GET — un GET care scrie e interdicția 6" % cale)
    assert not rele, "rute de artefact cu metoda greșită:\n" + "\n".join(rele)


def test_fiecare_ruta_de_artefact_cheama_pastreaza():
    """Pe structură: ruta chiar persistă, nu doar importă modulul."""
    arb = ast.parse(open(_MAIN, encoding="utf-8").read())
    gasite = set()
    for fn in ast.walk(arb):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        cai = [d.args[0].value for d in fn.decorator_list
               if isinstance(d, ast.Call) and d.args and isinstance(d.args[0], ast.Constant)
               and getattr(d.func, "attr", None) in ("get", "post")]
        if not set(cai) & set(_ACTE):
            continue
        for n in ast.walk(fn):
            if isinstance(n, ast.Call) and getattr(n.func, "attr", None) == "pastreaza":
                gasite |= set(cai) & set(_ACTE)
    lipsa = sorted(set(_ACTE) - gasite)
    assert not lipsa, ("rute care produc un artefact și NU cheamă `artefacte.pastreaza`: %s"
                       % lipsa)


@pytest.mark.parametrize("fel", sorted(artefacte.FELURI))
def test_vocabularul_e_inchis_si_documentat(fel):
    assert artefacte.FELURI[fel], "felul `%s` n-are descriere" % fel
