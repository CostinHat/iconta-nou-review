# -*- coding: utf-8 -*-
"""GARD "gaura de metoda" (09.08.2026, cerut de Costin): a PROBA un cont = prin calea de autentificare
(auth_api.login, aceeasi pe care o foloseste POST /auth/login din browser), NU prin verifica_parola pe hash.

Un cont cu hash VALID dar activ=false TRECE verifica_parola dar PICA la login() -> o "proba" pe DB/hash poate
spune "merge" cand loginul din browser esueaza. Testul demonstreaza divergenta (hash-ok, login-esec) pe cont
inactiv si convergenta pe cont activ. Cont efemer, ROLLBACK la final (nimic nu se commite; zero poluare).
Mutatie: daca login() n-ar mai verifica activ (doar hash), assert-ul (2) pica."""
import pytest
from core import db as _db, auth_api, nucleu


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_proba_login_e_prin_endpoint_nu_prin_hash():
    _db.init_pool(); pool = _db.pool(); conn = pool.getconn()
    PW = "ZtestMetodaLogin-2026-Xy"; H = nucleu.hash_parola(PW)
    email = "ztest_metoda_login@invalid"
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,activ) "
                        "VALUES (%s,%s,'Z','Z','superadmin',false)", (email, H))
        assert auth_api.verifica_parola_orice(PW, H) is True          # (1) hash valid
        assert auth_api.login(conn, email, PW)["ok"] is False         # (2) dar login() pica (activ=false)
        with conn.cursor() as cur:
            cur.execute("UPDATE public.users SET activ=true WHERE email=%s", (email,))
        r = auth_api.login(conn, email, PW)
        assert r["ok"] is True and r.get("token")                     # (3) activ=true -> login() reuseste
    finally:
        conn.rollback()          # nimic nu se commite -> contul efemer dispare, pool-ul ramane curat
        pool.putconn(conn)
