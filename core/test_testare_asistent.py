# -*- coding: utf-8 -*-
"""GARD — constatările din testarea ca asistent (comanda Costin 04.10.2026), punctele 3 și 6 + invitația.

  pct.3  „Câmpul «Email client» la adăugarea firmei acceptă emailul unui cont existent cu alt rol (superadmin)
         fără avertisment. Refuz numit: adresa aparține deja unui cont cu alt rol.” — și, măsurat: refuzul (când
         venea) venea DUPĂ ce firma era creată. Acum emailul se judecă ÎNAINTE de orice scriere, pe câmp.
         Aceeași funcție (`uc_comun._refuz_email_ocupat`) la accesul clientului, în portal și la invitația de asistent.
  pct.6  „Ecranul Asistenți: contorul «1 asistent · 1 activ» numără administratorul cabinetului. Separă-l.”
  pe drum: invitația de asistent nu dădea „Poate pregăti” (asistentul nou ieșea fără niciun drept), iar funcția de
         creare avea parametrii numiți greșit (`rol` primea cabinetul).
"""
from __future__ import annotations

import contextlib
import os

import pytest

from core import auth_api, uc_comun
from core import db as _db
from core.mesaje import EMAIL_ALT_ROL, EMAIL_ASISTENT_EXISTA, EMAIL_CLIENT_ACTIV

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── regula pură ──────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("ex,rol_dorit,asteptat", [
    (None, "client", None),
    ({"rol": "superadmin", "activ": True}, "client", EMAIL_ALT_ROL % ("a@b.ro", "X")),       # pct.3, instanța lui Costin
    ({"rol": "admin_firma", "activ": True}, "client", EMAIL_ALT_ROL % ("a@b.ro", "X")),
    ({"rol": "client", "activ": True}, "client", EMAIL_CLIENT_ACTIV % ("a@b.ro", "X")),
    ({"rol": "client", "activ": False}, "client", None),     # reactivarea rămâne posibilă (izolarea: R62)
    ({"rol": "client", "activ": True}, "angajat", EMAIL_ALT_ROL % ("a@b.ro", "X")),
    ({"rol": "angajat", "activ": False}, "angajat", EMAIL_ASISTENT_EXISTA % "a@b.ro"),
])
def test_refuzul_numeste_situatia(ex, rol_dorit, asteptat):
    assert uc_comun._refuz_email_ocupat(ex, rol_dorit, "a@b.ro", "X") == asteptat


# ── pe aplicația vie, cu date sintetice, în ROLLBACK ────────────────────────────────────────────────
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


SCH = "ztest_testare_asistent"
E_SUPER = "zt_ta_super@invalid.ro"     # cont cu ALT rol (instanța: emailul superadminului)
E_CLIENT = "zt_ta_client@invalid.ro"
E_ASIST = "zt_ta_asist@invalid.ro"


@pytest.fixture
def cab(monkeypatch):
    from core import observare as _obs
    from core import tenant_provisioning as _tp
    trimise = []
    monkeypatch.setattr(_obs, "trimite_email_html", lambda *a, **k: trimise.append(a))
    # șablonul real (aplicația îl încarcă la pornire): fără el, o cerere de creare s-ar opri ÎNAINTE de verificarea
    # emailului, iar testul ar trece pe un motiv greșit — cu el, lipsa verificării chiar ar crea firma
    monkeypatch.setattr(uc_comun, "_TENANT_TEMPLATE",
                        open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read())
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZT TESTARE ASISTENT') RETURNING id")
            firm = cur.fetchone()[0]

            def _u(email, rol, firma):
                cur.execute("INSERT INTO public.users (email,password_hash,nume,rol,accounting_firm_id,activ,"
                            "poate_pregati,poate_valida,poate_depune) VALUES (%s,'x','ZT',%s,%s,true,%s,%s,%s) RETURNING id",
                            (email, rol, firma, rol == "admin_firma", rol == "admin_firma", rol == "admin_firma"))
                return cur.fetchone()[0]
            uid_admin = _u("zt_ta_admin@invalid.ro", "admin_firma", firm)
            _u(E_SUPER, "superadmin", None)
            _u(E_CLIENT, "client", firm)
            _u(E_ASIST, "angajat", firm)
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(open(os.path.join(RAD, "tenant_template.sql"),
                                                         encoding="utf-8").read(), SCH))
            cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ) "
                        "VALUES (%s,'ZT TA firma','14399840',%s,true) RETURNING id", (SCH, firm))
            tid = cur.fetchone()[0]

        @contextlib.contextmanager
        def _fake(schema=None):
            with conn.cursor() as c:
                c.execute('SET search_path TO "%s", public' % schema if schema else "SET search_path TO public")
            yield _ConnProxy(conn)

        monkeypatch.setattr(_db, "get_conn", _fake)
        yield {"conn": conn, "firm": firm, "tid": tid, "trimise": trimise,
               "tok": auth_api.emite_token({"id": uid_admin, "rol": "admin_firma", "accounting_firm_id": firm})}
    finally:
        with conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.rollback()
        p.putconn(conn)


def _cl():
    import main
    from fastapi.testclient import TestClient
    return TestClient(main.app)


def _H(t):
    return {"Authorization": "Bearer " + t}


def _nr_firme(env):
    with env["conn"].cursor() as c:
        c.execute("SET search_path TO public")
        c.execute("SELECT count(*) FROM public.tenants WHERE accounting_firm_id = %s", (env["firm"],))
        return c.fetchone()[0]


def _camp(r):
    d = r.json()["detail"]
    return {(c["camp"], c["mesaj"]) for c in d["erori_campuri"]}, d["mesaj"]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_firma_nu_se_creeaza_cu_emailul_unui_cont_cu_alt_rol(cab):
    """pct.3: refuz NUMIT, PE CÂMP, și NICIO firmă creată (înainte: firma se crea, refuzul venea după)."""
    inainte = _nr_firme(cab)
    r = _cl().post("/tenants", headers=_H(cab["tok"]),
                   json={"nume": "ZT TA noua", "cui": "14837428", "email_client": E_SUPER})
    assert r.status_code == 400, r.text
    campuri, mesaj = _camp(r)
    asteptat = EMAIL_ALT_ROL % (E_SUPER, "clientul firmei")
    assert campuri == {("email_client", asteptat)} and mesaj == asteptat
    assert _nr_firme(cab) == inainte, "firma s-a creat deși emailul clientului a fost refuzat"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_accesul_clientului_refuza_numit_contul_cu_alt_rol(cab):
    r = _cl().post("/tenants/%d/client-acces" % cab["tid"], headers=_H(cab["tok"]), json={"email": E_ASIST})
    assert r.status_code == 400, r.text
    assert _camp(r) == ({("email", EMAIL_ALT_ROL % (E_ASIST, "clientul firmei"))},
                        EMAIL_ALT_ROL % (E_ASIST, "clientul firmei"))
    assert cab["trimise"] == [], "s-a trimis invitația deși adresa e refuzată"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_invitatia_de_asistent_refuza_numit(cab):
    cl = _cl()
    r = cl.post("/asistenti", headers=_H(cab["tok"]), json={"email": E_CLIENT})
    assert r.status_code == 422, r.text
    assert _camp(r)[1] == EMAIL_ALT_ROL % (E_CLIENT, "asistent")
    r = cl.post("/asistenti", headers=_H(cab["tok"]), json={"email": E_ASIST})
    assert r.status_code == 422 and _camp(r)[1] == EMAIL_ASISTENT_EXISTA % E_ASIST, r.text


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_invitatia_da_poate_pregati_implicit_si_pune_cabinetul_corect(cab):
    """Decizia Costin 04.10: „Poate pregăti” (orice asistent). Și funcția de creare scrie cabinetul în
    `accounting_firm_id` și bifa în `poate_valida` — nu le mai inversează din poziție."""
    r = _cl().post("/asistenti", headers=_H(cab["tok"]), json={"email": "zt_ta_nou@invalid.ro"})
    assert r.status_code == 200, r.text
    with cab["conn"].cursor() as c:
        c.execute("SET search_path TO public")
        c.execute("SELECT rol, accounting_firm_id, poate_pregati, poate_valida, poate_depune FROM public.users "
                  "WHERE id = %s", (r.json()["user_id"],))
        assert c.fetchone() == ("angajat", cab["firm"], True, False, False)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_contorul_separa_administratorul(cab):
    """pct.6: un administrator + un asistent NU sunt „2 asistenți”."""
    r = _cl().get("/asistenti", headers=_H(cab["tok"]))
    assert r.status_code == 200, r.text
    assert r.json()["sumar"] == {"administratori": 1, "asistenti": 1, "asistenti_activi": 1}
