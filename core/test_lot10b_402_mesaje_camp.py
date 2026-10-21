# -*- coding: utf-8 -*-
"""[lotul 10, deficiența 402 — comanda Costin 10.2 pct.7b, verbatim] „refuzurile la contul de stoc fără articol spun doar «articolul» /
«cantitatea».” Clasa (410): mesajul de lângă un câmp refuzat e o frază întreagă — ce lipsește și ce se cere —, nu un cuvânt.

Două gărzi: (1) borderoul de achiziție refuzat pe un cont de stoc numește TOATE câmpurile lipsă, fiecare cu fraza lui, iar refuzul spune
exact ce lipsește; (2) GARD STRUCTURAL pe tot codul: orice mesaj de câmp scris literal (`{"camp": …, "mesaj": "…"}` în core/*.py și
main.py) începe cu literă mare, are cel puțin două cuvinte și se termină cu punct — un fragment („articolul”, „cel puțin un articol”,
„cerut, nu poate lipsi”) pică poarta. LIMITĂ: mesajele compuse la rulare (`"…" % x`, f-string) nu se văd în AST ca text; regula lor e
aceeași, verificată numai la borderou (testul 1). Temei: OMFP 2634/2015 anexa 1 pct.2 și pct.6 (vânzătorul identificat; marfa
intrată în gestiune odată cu borderoul). Schemă efemeră din template, în tranzacție anulată."""
import ast
import contextlib
import glob
import io
import os
import re

import pytest

from core import db as _db, erori, tenant_provisioning as _tp

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = "tenant_test_402_mesaje"


def mesaje_de_camp_fragment():
    """[(fișier, linie, mesaj)] — mesajele de câmp literale care nu sunt o frază întreagă."""
    rele = []
    for f in sorted(glob.glob(os.path.join(RAD, "core", "*.py"))) + [os.path.join(RAD, "main.py")]:
        if os.path.basename(f).startswith("test_"):
            continue
        for n in ast.walk(ast.parse(io.open(f, encoding="utf-8").read())):
            if not isinstance(n, ast.Dict) or any(k is None for k in n.keys):
                continue
            chei = [k.value if isinstance(k, ast.Constant) else None for k in n.keys]
            if set(chei) >= {"camp", "mesaj"}:
                v = n.values[chei.index("mesaj")]
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    s = v.value.strip()
                    if not (s[:1].isupper() and s.endswith((".", "?")) and len(s.split()) >= 2):
                        rele.append((os.path.relpath(f, RAD), n.lineno, s))
    return rele


def test_402_gard_niciun_mesaj_de_camp_fragment():
    # comanda 10.2 pct.7b: un refuz care spune „doar «articolul» / «cantitatea»” nu spune ce se cere — frază întreagă, peste tot
    assert mesaje_de_camp_fragment() == []


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


class _P:
    def __init__(s, c): s._c = c
    def commit(s): pass
    def __getattr__(s, n): return getattr(s._c, n)


@pytest.fixture
def conn(monkeypatch):
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, forma_juridica, capital_subscris, metoda_stoc) "
                            "VALUES (1, 'F1 SRL', '14399840', true, 'SRL', 200, 'cantitativ_valoric')")
            from core import auth_api, uc_comun, uc_tenants
            monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(_P(c)))
            monkeypatch.setattr(auth_api, "schema_tenant", lambda *a, **k: SCH)
            monkeypatch.setattr(uc_comun, "_cere_luna_deschisa", lambda *a, **k: None)
            yield c
        finally:
            c.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_402_refuzul_la_contul_de_stoc_spune_complet_ce_lipseste(conn):
    from core import uc_tenants
    with pytest.raises(erori.DateInvalide) as e:
        uc_tenants.achizitie_neinregistrat(1, {"data": "2026-10-20", "furnizor_nume": "Maria Ionescu", "valoare": 150,
                                               "cont_cheltuiala": "371"}, {"uid": 1})
    d = e.value.args[0]
    camp = {x["camp"]: x["mesaj"] for x in d["erori_campuri"]}
    # TOATE câmpurile lipsă deodată (clasa 410), nu numai primul grup
    assert list(camp) == ["op-furnizor_adresa", "op-furnizor_act", "op-articol", "op-cantitate"], camp
    # OMFP 2634/2015 anexa 1 pct.6: marfa intră în gestiune odată cu borderoul — câmpul spune ce se cere și unde, nu „articolul”
    assert camp["op-articol"] == "Scrie articolul care intră în stoc pe contul 371: marfa intră în gestiune odată cu borderoul.", camp
    assert camp["op-cantitate"].startswith("Scrie cantitatea care intră în stoc pe contul 371, mai mare decât zero"), camp
    # refuzul de jos numește TOATE grupurile lipsă, în ordinea formularului: ce cere borderoul despre vânzător, apoi intrarea în stoc
    assert re.findall(r"completează ([^.]+)\.", d["mesaj"]) == [
        "domiciliul vânzătorului și actul lui de identitate (seria și numărul)", "articolul și cantitatea"], d
    # numai cantitatea lipsă -> refuzul numește numai cantitatea
    with pytest.raises(erori.DateInvalide) as e:
        uc_tenants.achizitie_neinregistrat(1, {"data": "2026-10-20", "furnizor_nume": "Maria Ionescu", "furnizor_adresa": "Str. Mare 2",
                                               "furnizor_act": "PH 1", "valoare": 150, "cont_cheltuiala": "371", "articol": "grâu"},
                                           {"uid": 1})
    d = e.value.args[0]
    assert [x["camp"] for x in d["erori_campuri"]] == ["op-cantitate"] and d["mesaj"].endswith("completează cantitatea."), d
