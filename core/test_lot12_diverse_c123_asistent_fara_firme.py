# -*- coding: utf-8 -*-
"""[lotul 12, C123] „Scoate firma”: asistentul rămas fără nicio firmă rămânea activ — regula „zero firme” a cabinetului
(`asistenti_api.aplica_regula_zero_firme`: competențele se golesc, contul se dezactivează, rămâne în istoric) se aplica numai din ecranul
colegului.

Clasa — drumurile care rup legătura unui asistent cu o firmă (căutate: `grep -rnE "user_tenants|TABEL_LEGATURA_FIRME" core main.py scripts
| grep -i delete`):
  1. `tenant_stergere.sterge` (Scoate firma; și GDPR, care trece prin ea pentru fiecare firmă) — REPARAT aici: aplică regula;
  2. `asistenti_api.elimina_firma` + `POST /asistenti/{uid}/finalizeaza-firme` (ecranul colegului) — regula, după toate bifele;
  3. `gdpr_sterge` — șterge apoi conturile cabinetului întreg (nu rămâne niciun cont activ);
  4. `uc_portal.portal_revoca_acces` (`dezleaga_contul_de_firma`) — numai conturi de client (`dezactiveaza_contul_client`).
Datele existente: `core/migrare_asistenti_fara_firme.py` (aceeași funcție, pe asistenții activi deja fără firme).

Probele rulează pe baza de TEST, într-o tranzacție ANULATĂ la final: firma de probă se creează pe drumul aplicației (`provision_tenant`),
se scoate cu `sterge`, nimic nu rămâne. Temei: N/A — regulă de produs (asistenții lucrează pe firmele alocate), nu fiscală.
"""
import io
import os
import time

import pytest

from core import asistenti_api, db, tenant_stergere as ts

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture()
def conn():
    db.init_pool()
    with db.get_conn() as c:
        try:
            yield c
        finally:
            c.rollback()


def _cabinet(c):
    with c.cursor() as cur:
        cur.execute("SELECT id, accounting_firm_id FROM public.users WHERE email = 'patron@prisma-cont.test'")
        return cur.fetchone()


def _cui_proba():
    """CUI de probă cu cifra de control calculată după algoritmul oficial (CLAUDE.md „Date de test”), verificată cu `cui_valid`."""
    from core.tenant_provisioning import cui_valid
    corp = str(80000000 + int(time.time() * 1000) % 9000000).rjust(9, "0")
    r = sum(int(corp[i]) * k for i, k in enumerate([7, 5, 3, 2, 1, 7, 5, 3, 2])) * 10 % 11
    cui = corp.lstrip("0") + str(0 if r == 10 else r)
    assert cui_valid(cui), cui
    return cui


@pytest.fixture()
def firma_noua(contor_schema_pastrat, conn):
    """(uid, cabinet, tenant_id): firma de probă a cabinetului, creată pe drumul aplicației (`provision_tenant`). `rollback` nu întoarce
    secvența numerelor de schemă: `contor_schema_pastrat` o readuce după rollback-ul lui `conn` (`core/test_predare_cifre.py`)."""
    from core import tenant_provisioning as tp
    uid, cab = _cabinet(conn)
    sql_t = io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read()
    r = tp.provision_tenant(conn, "PROBA C123 %d SRL" % (int(time.time() * 1000) % 10000000), _cui_proba(), cab, uid, sql_t)
    return uid, cab, r["tenant_id"]


def _asistent(c, cab, eticheta, firme):
    from core import repo_utilizatori
    with c.cursor() as cur:
        uid = repo_utilizatori.creeaza_cont_asistent(cur, "c123-%s-%d@prisma-cont.test" % (eticheta, int(time.time() * 1e6) % 10 ** 9),
                                                     "!", "Asistent C123 %s" % eticheta, cab, True, True)[0]
    for t in firme:
        assert asistenti_api.atribuie_firma(c, cab, uid, t)["ok"]
    return uid


def _stare(c, uid):
    with c.cursor() as cur:
        cur.execute("SELECT activ, poate_pregati, poate_valida, poate_depune FROM public.users WHERE id = %s", (uid,))
        return cur.fetchone()


def test_def_c123_scoaterea_firmei_dezactiveaza_asistentul_ramas_fara_firme(conn, firma_noua):
    """Firma nouă (fără evidență), doi asistenți: A lucrează numai pe ea, B și pe altă firmă a cabinetului. Previzualizarea îl numește pe A
    (`asistenti_de_dezactivat`), `sterge` îi aplică regula „zero firme”: inactiv, fără competențe, contul păstrat; B rămâne neatins.
    MUTAȚIE: în `sterge`, `asistenti = []` -> A rămâne activ -> pică."""
    uid, cab, tid = firma_noua
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM public.tenants WHERE accounting_firm_id = %s AND id <> %s ORDER BY id LIMIT 1", (cab, tid))
        alta = cur.fetchone()[0]
        cur.execute("SELECT cui FROM public.tenants WHERE id = %s", (tid,))
        cui = cur.fetchone()[0]
    a = _asistent(conn, cab, "a", [tid])
    b = _asistent(conn, cab, "b", [tid, alta])
    p = ts.previzualizare(conn, tid)
    assert p["se_poate_sterge"], p["evidenta"]
    assert [x["id"] for x in p["asistenti_de_dezactivat"]] == [a], p["asistenti_de_dezactivat"]
    assert p["asistenti_de_dezactivat"][0]["nume"] == "Asistent C123 a"
    r = ts.sterge(conn, tid, "scoatere_firma", uid, confirmare=cui)
    assert [x["id"] for x in r["asistenti_dezactivati"]] == [a] and r["randuri_sterse"]["asistenti_dezactivati"] == 1, r
    assert _stare(conn, a) == (False, False, False, False), "asistentul rămas fără firme a rămas activ / cu competențe"
    assert _stare(conn, b) == (True, True, True, False), "asistentul care mai are o firmă a fost atins"
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM public.users WHERE id = %s", (a,))
        assert cur.fetchone()[0] == 1, "contul asistentului s-a șters — trebuia doar dezactivat (rămâne în istoric)"


def test_def_c123_migrarea_dezactiveaza_asistentii_activi_deja_fara_firme(conn):
    """Datele existente: un asistent activ fără niciun rând în `user_tenants` (cum îl lăsa „Scoate firma” înainte) -> migrarea îi aplică
    regula; un asistent cu firme și administratorul rămân neatinși; a doua rulare nu mai găsește nimic.
    MUTAȚIE: în `migrare_asistenti_fara_firme.SQL_RAMASI` `u.rol = 'angajat'` -> `u.rol = 'client'` -> asistentul rămâne activ -> pică."""
    from core import migrare_asistenti_fara_firme as m
    uid, cab = _cabinet(conn)
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM public.tenants WHERE accounting_firm_id = %s ORDER BY id LIMIT 1", (cab,))
        o_firma = cur.fetchone()[0]
    orfan = _asistent(conn, cab, "orfan", [])
    cu_firma = _asistent(conn, cab, "cufirma", [o_firma])
    admin_inainte = _stare(conn, uid)
    assert (orfan, cab) in m.ramasi(conn)
    assert m.aplica(conn) >= 1
    assert _stare(conn, orfan) == (False, False, False, False)
    assert _stare(conn, cu_firma) == (True, True, True, False)
    assert _stare(conn, uid) == admin_inainte
    assert m.ramasi(conn) == [] and m.aplica(conn) == 0


def test_def_c123_toate_drumurile_care_rup_legatura_sunt_numite():
    """Garda clasei: orice `DELETE` din `user_tenants` în cod stă într-unul din drumurile numite în antet (cu regula aplicată sau cu motivul
    pentru care nu se aplică). Un drum NOU pică aici până se clasifică. MUTAȚIE: un `DELETE FROM public.user_tenants` adăugat într-un modul
    nou -> pică."""
    import re
    numite = {"core/tenant_stergere.py",    # prin TABELE_TENANT (`DELETE FROM public."%s"`), apoi regula pe asistenți
              "core/asistenti_api.py",      # elimina_firma; regula: `finalizeaza-firme`, după toate bifele ecranului colegului
              "core/gdpr_sterge.py",        # conturile cabinetului se șterg imediat după
              "core/repo_utilizatori.py"}   # `dezleaga_contul_de_firma`: portalul clientului, numai conturi de client
    gasite = set()
    for d, _, fs in os.walk(os.path.join(RAD, "core")):
        for f in fs:
            if f.endswith(".py") and not f.startswith("test_"):
                p = os.path.join(d, f)
                t = io.open(p, encoding="utf-8").read()
                if re.search(r"DELETE FROM (?:public\.user_tenants|\{TABEL_LEGATURA_FIRME\})", t):
                    gasite.add(os.path.relpath(p, RAD))
    main = io.open(os.path.join(RAD, "main.py"), encoding="utf-8").read()
    assert not re.search(r"DELETE FROM public\.user_tenants", main), "main.py rupe direct legătura unui cont cu o firmă"
    assert gasite - {"core/tenant_stergere.py"} == numite - {"core/tenant_stergere.py"}, sorted(gasite ^ numite)
    assert {"user_tenants"} <= set(ts.TABELE_TENANT), "Scoate firma nu mai rupe legăturile prin lista tabelelor firmei"
    # pe ARBORE: `sterge` cheamă regula „zero firme” din `asistenti_api` (aliasul `_asist`), pe conexiunea tranzacției
    import ast
    arb = ast.parse(io.open(os.path.join(RAD, "core", "tenant_stergere.py"), encoding="utf-8").read())
    assert any(isinstance(n, ast.ImportFrom) and n.module == "core" and ("asistenti_api", "_asist") in {(a.name, a.asname) for a in n.names}
               for n in ast.walk(arb)), "`_asist` nu mai e `core.asistenti_api` în tenant_stergere.py"
    sterge = [f for f in arb.body if isinstance(f, ast.FunctionDef) and f.name == "sterge"]
    regula = [c for c in ast.walk(sterge[0]) if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
              and c.func.attr == "aplica_regula_zero_firme" and isinstance(c.func.value, ast.Name) and c.func.value.id == "_asist"]
    assert len(sterge) == 1 and [ast.unparse(c.args[0]) for c in regula] == ["conn"], \
        "Scoate firma nu mai aplică regula „zero firme” asistenților: %s" % [ast.unparse(c) for c in regula]
