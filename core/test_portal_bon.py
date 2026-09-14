# -*- coding: utf-8 -*-
"""Fluxul bonului pozat — singurul loc în care **un client**, nu contabilul, scrie în contabilitate.

Auditul (R1) a numit cele trei rute printre cele 21 care schimbă date fără nicio probă de
comportament, iar pe astea le-a pus imediat după cheile de API: `POST /portal/bon`,
`POST /portal/bon/{id}/confirma`, `DELETE /portal/bon/{id}`.

CE ÎNTREABĂ, și de ce nu codul HTTP: **unde ajunge documentul**. Un bon încărcat rămâne DRAFT
(`status='extras'`) și nu intră la contabil până nu confirmă clientul — deci proba citește coloana,
nu răspunsul. Confirmarea îl mută; ștergerea îl scoate cu tot cu poze; iar peste un bon deja trimis
nici ștergerea, nici a doua confirmare nu mai au efect.

ȘI O PROBĂ CARE NU E DESPRE BAZA DE DATE: un fișier care nu e imagine se refuză **înainte** de
apelul la furnizorul de AI (R155, 05.09.2026 — refuzul cade înainte, deci și o cerere plătită mai
puțin). Aia nu se vede din cod de răspuns: proba numără dacă furnizorul a fost chemat.

CURĂȚENIE: schemă efemeră, `db.get_conn` întors spre aceeași conexiune, `rollback` la final. Pozele
merg într-un director temporar — `BON_DIR_BAZA` e mutat pe durata probei, altfel ar scrie în
depozitul real.
"""
from __future__ import annotations

import contextlib
import json

import pytest

from core import db as _db
from core import uc_comun as _uc_comun

SCH = "ztest_portal_bon"
# Octeții care fac un PNG să fie PNG (`core/common.tip_imagine` citește semnătura, nu numele).
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 64


class _ConnProxy:
    def __init__(self, real):
        object.__setattr__(self, "_real", real)

    def __getattr__(self, n):
        return getattr(self._real, n)

    def commit(self):
        pass

    def rollback(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def env(monkeypatch, tmp_path):
    from core import ai_client, tenant_provisioning as _tp
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZTEST BON') RETURNING id")
            firm = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,"
                        "accounting_firm_id,activ) VALUES "
                        "('ztest_bon_client@invalid','x','N','N','client',%s,true) RETURNING id",
                        (firm,))
            uid = cur.fetchone()[0]
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(
                open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET search_path TO public")
            cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ) "
                        "VALUES (%s,'TENANT BON','14399840',%s,true) RETURNING id", (SCH, firm))
            tid = cur.fetchone()[0]
            cur.execute("INSERT INTO public.user_tenants (user_id,tenant_id) VALUES (%s,%s)",
                        (uid, tid))

        @contextlib.contextmanager
        def _fake(schema=None):
            with conn.cursor() as c:
                c.execute('SET search_path TO "%s", public' % schema if schema
                          else "SET search_path TO public")
            yield _ConnProxy(conn)

        monkeypatch.setattr(_db, "get_conn", _fake)
        monkeypatch.setattr(_uc_comun, "BON_DIR_BAZA", str(tmp_path / "bonuri"))

        chemari = []

        def _citeste(imagini, prompt):
            chemari.append(len(imagini))
            return json.dumps({"tip": "bon", "comerciant": "ZT MAGAZIN", "cui": "14399840",
                               "data": "2026-09-14", "total": 121.0, "numar_document": "7",
                               "articole": [{"denumire": "cafea", "valoare": 100.0,
                                             "cota_tva": 21, "cont_propus": "623"}],
                               "tva": [{"cota": 21, "valoare": 21.0}],
                               "bon_complet": True, "orientare": 0})

        monkeypatch.setattr(ai_client, "disponibil", lambda: True)
        monkeypatch.setattr(ai_client, "citeste_imagini", _citeste)

        from core import auth_api
        yield {"tid": tid, "conn": conn, "chemari": chemari, "dir": tmp_path / "bonuri",
               "tok": auth_api.emite_token({"id": uid, "rol": "client",
                                            "accounting_firm_id": firm})}
    finally:
        with conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.rollback()
        p.putconn(conn)


def _client():
    import main
    from fastapi.testclient import TestClient
    return TestClient(main.app)


def _H(env):
    return {"Authorization": "Bearer " + env["tok"]}


def _incarca(cl, env, continut=PNG, nume="bon.png"):
    return cl.post("/portal/bon", files={"fisiere": (nume, continut, "image/png")},
                   headers=_H(env))


def _bonuri(env):
    with env["conn"].cursor() as cur:
        cur.execute('SELECT id, status FROM "%s".bonuri ORDER BY id' % SCH)
        return cur.fetchall()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_un_bon_incarcat_ramane_DRAFT_pana_la_confirmare(env):
    """Unde ajunge documentul, citit din coloană: `extras` = la client, nu la contabil."""
    cl = _client()
    r = _incarca(cl, env)
    assert r.status_code == 200, r.text[:300]
    bon_id = r.json()["bon_id"]
    assert _bonuri(env) == [(bon_id, "extras")], "bonul n-a rămas draft: %r" % (_bonuri(env),)
    assert env["chemari"] == [1], "furnizorul de AI n-a fost chemat o dată: %r" % env["chemari"]

    poze = list((env["dir"] / SCH / str(bon_id)).glob("img_*"))
    assert len(poze) == 1 and poze[0].read_bytes() == PNG, "poza nu s-a scris lângă bon"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_confirmarea_TRIMITE_bonul_la_contabil_si_nu_se_poate_repeta(env):
    cl = _client()
    bon_id = _incarca(cl, env).json()["bon_id"]

    r = cl.post("/portal/bon/%d/confirma" % bon_id, headers=_H(env))
    assert r.status_code == 200, r.text[:200]
    assert _bonuri(env) == [(bon_id, "de_verificat")], "confirmarea n-a mutat bonul"

    din_nou = cl.post("/portal/bon/%d/confirma" % bon_id, headers=_H(env))
    assert din_nou.status_code == 404, "a doua confirmare trece: %d" % din_nou.status_code
    assert _bonuri(env) == [(bon_id, "de_verificat")], "a doua confirmare a schimbat ceva"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_stergerea_ia_si_pozele_dar_NU_atinge_un_bon_deja_trimis(env):
    """Două jumătăți ale aceleiași reguli: clientul își poate reface poza cât e draft, dar nu poate
    retrage un document ajuns la contabil."""
    cl = _client()
    bon_id = _incarca(cl, env).json()["bon_id"]
    dir_bon = env["dir"] / SCH / str(bon_id)
    assert dir_bon.is_dir()

    r = cl.delete("/portal/bon/%d" % bon_id, headers=_H(env))
    assert r.status_code == 200, r.text[:200]
    assert _bonuri(env) == [], "draftul a rămas în tabel"
    assert not dir_bon.exists(), "pozele au rămas pe disc după ștergerea draftului"

    al_doilea = _incarca(cl, env).json()["bon_id"]
    assert cl.post("/portal/bon/%d/confirma" % al_doilea, headers=_H(env)).status_code == 200
    sters = cl.delete("/portal/bon/%d" % al_doilea, headers=_H(env))
    assert sters.status_code == 404, "un bon trimis la contabil se poate șterge de client: %d" % sters.status_code
    assert _bonuri(env) == [(al_doilea, "de_verificat")], "ștergerea refuzată a avut totuși efect"
    assert (env["dir"] / SCH / str(al_doilea)).is_dir(), "pozele unui bon trimis au dispărut"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_ce_nu_e_imagine_se_refuza_INAINTE_de_apelul_la_AI(env):
    """[R155] Tipul se citește din octeți, nu din numele fișierului. Proba nu se uită la codul HTTP,
    ci numără dacă furnizorul a fost chemat — acolo e diferența care se plătește."""
    cl = _client()
    r = _incarca(cl, env, continut=b"nu sunt o imagine, sunt un text", nume="bon.png")
    assert r.status_code in (400, 422), "un text numit .png trece: %d %s" % (r.status_code, r.text[:200])
    assert env["chemari"] == [], "furnizorul de AI a fost chemat pe un fișier care nu e imagine"
    assert _bonuri(env) == [], "s-a creat un bon dintr-un fișier care nu e imagine"
    # Egalitate pe câmpul de JSON, nu un cuvânt căutat în răspuns: mesajul e contractul rutei, și
    # trebuie să numească FIȘIERUL trimis — altfel, la patru poze, clientul nu știe care e de vină.
    assert r.json().get("detail") == (
        "«bon.png» nu e o imagine: primii octeți nu sunt de JPEG, PNG, GIF sau WEBP. "
        "Fotografiază bonul, sau încarcă poza lui."), r.text[:300]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_bonul_altui_tenant_nu_se_confirma_si_nu_se_sterge(env):
    """Izolarea, măsurată pe efect: un id care nu e al schemei mele nu se atinge — și nici nu-mi
    spune că există."""
    cl = _client()
    bon_id = _incarca(cl, env).json()["bon_id"]
    strain = bon_id + 100000
    assert cl.post("/portal/bon/%d/confirma" % strain, headers=_H(env)).status_code == 404
    assert cl.delete("/portal/bon/%d" % strain, headers=_H(env)).status_code == 404
    assert _bonuri(env) == [(bon_id, "extras")], "cererile pe un id străin au atins bonul meu"
