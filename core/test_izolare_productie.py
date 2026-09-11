# -*- coding: utf-8 -*-
"""core/test_izolare_productie.py — ACCEPTANTA R68 (arhitect, 11.09.2026).

Cele sapte probe cerute, cu numele functiei identic cu cheia de acceptanta, ca maparea sa fie
MECANICA: cine citeste raportul nu trebuie sa creada pe cuvant ca proba X acopera cheia X.

**Doua directii peste tot** (METODA §22). O garda care refuza ORICE trece la fel de usor ca una
care accepta orice, si amandoua sunt inutile. Deci fiecare proba de refuz are perechea ei de
ACCEPTARE: acreditarile de test trebuie sa mearga pe baza de test — altfel «refuzat pe productie»
n-ar dovedi frontiera, ci doar o parola gresita.

**Fail-closed, nu skip.** Daca mediul izolat nu exista, probele astea PICA; nu sar. Un skip ar fi
exact tacerea pe care R68 o repara: absenta mediului nu e permisiune, e lipsa frontierei.
"""
from __future__ import annotations

import os

import pytest

from core import mediu_test as mt

pytestmark = pytest.mark.izolare


# ============================================================
#  CALIBRARE — garda trebuie sa stie sa spuna si DA, si NU
# ============================================================
ENV_PRODUCTIE = {
    "DATABASE_URL": "postgresql://iconta_user:x@localhost:5432/iconta_v2",
    "ICONTA_MEDIU": "test",          # chiar MINTIND ca e test, baza o da de gol
}
ENV_TEST = {
    "ICONTA_MEDIU": "test",
    "DATABASE_URL": "postgresql://iconta_test_user:x@localhost:5432/iconta_test",
}


def test_calibrare_garda_refuza_productia():
    """Directia 1: pe un mediu de productie, garda are ce spune."""
    c = mt.coduri(ENV_PRODUCTIE)
    assert c, "garda a ACCEPTAT un DSN de productie — atunci n-a aparat nimic niciodata"
    # pe COD, nu pe subsir din proza: motivul e un obiect cu campuri (METODA §23)
    assert mt.COD_BAZA_PRODUCTIE in c, "refuzul nu recunoaste baza de productie: %r" % sorted(c)


def test_calibrare_garda_accepta_mediul_izolat():
    """Directia 2: pe mediul izolat, garda TACE. Fara asta, o garda care refuza mereu ar trece
    prima proba si ar bloca totul, iar noi am crede ca avem frontiera."""
    assert mt.motive(ENV_TEST) == [], (
        "garda refuza chiar mediul izolat — atunci refuzul ei nu e o informatie")


def test_calibrare_tacerea_nu_trece():
    """Un mediu care NU declara nimic e refuzat. Lipsa informatiei nu e permisiune."""
    assert mt.motive({}), "un mediu gol a trecut — fail-open, exact pe dos"
    fara_marca = dict(ENV_TEST)
    fara_marca.pop("ICONTA_MEDIU")
    assert mt.motive(fara_marca), "un DSN de test FARA ICONTA_MEDIU a trecut pe baza formei DSN-ului"


def test_calibrare_dsn_cu_parola_ciudata_nu_minte():
    """Parola cu `@` si `/` in ea: raspunsul gresit cu incredere e felul de esec care ne-a adus
    aici, deci se probeaza explicit."""
    d = mt.desface_dsn("postgresql://iconta_user:a@b/c@localhost:5432/iconta_v2")
    assert d["dbname"] == "iconta_v2", d
    assert d["user"] == "iconta_user", d


# ============================================================
#  ACCEPTANTA — cele sapte chei
# ============================================================
def _stare():
    return mt.descrie(os.environ)


def test_test_db_is_distinct_from_production():
    """TEST_DB_IS_DISTINCT_FROM_PRODUCTION"""
    st = _stare()
    assert st["dbname"], "mediul nu numeste nicio baza"
    assert st["dbname"] != mt.PRODUCTIE_DBNAME, (
        "suita ruleaza pe baza de PRODUCTIE (%s)" % st["dbname"])


def test_test_credentials_distinct():
    """TEST_CREDENTIALS_DISTINCT"""
    st = _stare()
    assert st["user"], "mediul nu numeste niciun utilizator"
    assert st["user"] != mt.PRODUCTIE_USER, (
        "suita ruleaza cu rolul de PRODUCTIE (%s) — o baza diferita nu ajuta daca rolul e acelasi, "
        "fiindca rolul asta are drepturi si pe productie" % st["user"])


def test_production_dsn_guard():
    """TEST_PRODUCTION_DSN_GUARD — garda refuza pornirea pe DSN de productie, si SPUNE de ce."""
    with pytest.raises(mt.MediuNedovedit) as exc:
        mt.verifica(ENV_PRODUCTIE)
    assert mt.COD_BAZA_PRODUCTIE in exc.value.coduri, (
        "refuzul nu recunoaste baza: %r" % sorted(exc.value.coduri))
    assert exc.value.cale_remediu == mt.CALE_TEST_ENV, (
        "refuzul nu poarta iesirea — un refuz fara iesire scrisa se ocoleste, nu se respecta: %r"
        % exc.value.cale_remediu)
    # si, in cealalta directie, pe mediul curent nu ridica
    assert mt.verifica(os.environ) is True


def _cere_mediu_izolat():
    """Probele care INCEARCA sa scrie nu au voie sa porneasca pe un mediu nedovedit.

    **Scris dupa ce am gresit exact asta, pe 11.09.2026 la 03:55.** Am rulat probele de mai jos
    inainte sa existe frontiera. Ele si-au facut treaba — au dovedit ca rolul suitei ajunge in
    productie si ca un `commit` explicit ateriza acolo —, dar au dovedit-o *exercitand* capacitatea,
    adica lasand `public.sonda_izolare` cu doua randuri comise in baza de productie.

    O proba care demonstreaza o bariera nu se poate rula acolo unde bariera lipseste: acolo, ea E
    incalcarea. Deci se refuza INAINTE de orice conexiune, nu dupa.
    """
    m = mt.motive(os.environ)
    if m:
        pytest.fail(
            "proba de SCRIERE refuza sa porneasca pe un mediu nedovedit de test — aici, ea ar fi "
            "chiar scrierea pe care o interzice:\n%s"
            % "\n".join("  - " + x for x in m))


def _psycopg2():
    import psycopg2
    return psycopg2


def _dsn_productie_cu_acreditarea_de_test():
    """DSN-ul catre baza de PRODUCTIE, dar cu utilizatorul si parola SUITEI. Asta e intrebarea
    care conteaza: are rolul cu care rulam voie sa ajunga acolo?"""
    st = _stare()
    parola = os.environ.get("DB_PASSWORD", "")
    return "postgresql://%s:%s@%s:%s/%s" % (
        st["user"], parola, st["host"] or "localhost", st["port"] or "5432", mt.PRODUCTIE_DBNAME)


def _conectare_esueaza(dsn):
    """(a_esuat, mesajul). Nu inghite exceptia: motivul se intoarce, ca sa intre in raport."""
    psycopg2 = _psycopg2()
    try:
        c = psycopg2.connect(dsn, connect_timeout=5)
    except Exception as e:                       # noqa: BLE001 — motivul se PROPAGA, nu se pierde
        return True, "%s: %s" % (type(e).__name__, str(e).strip().splitlines()[0] if str(e) else "")
    c.close()
    return False, ""


def test_production_write_attempt_fails_closed():
    """TEST_PRODUCTION_WRITE_ATTEMPT_FAILS_CLOSED — nu «scrierea e refuzata», ci CONEXIUNEA."""
    _cere_mediu_izolat()
    a_esuat, motiv = _conectare_esueaza(_dsn_productie_cu_acreditarea_de_test())
    assert a_esuat, (
        "rolul suitei S-A CONECTAT la baza de productie. Frontiera nu exista: orice test care "
        "uita rollback poate persista acolo.")
    # ANTI-VACUUM: aceleasi acreditari TREBUIE sa mearga pe baza lor. Altfel proba de mai sus ar
    # trece si cu o parola gresita, si n-am dovedit nicio frontiera.
    a_esuat_test, motiv_test = _conectare_esueaza(os.environ["DATABASE_URL"])
    assert not a_esuat_test, (
        "acreditarile nu merg nici pe baza de test (%s) — deci refuzul de mai sus nu dovedeste "
        "frontiera, ci doar ca nu ne putem conecta nicaieri" % motiv_test)
    assert motiv, "conexiunea a esuat fara motiv citibil"


def _scrie_si(conn, cum):
    """Scrie un rand-sonda si termina tranzactia in felul cerut. Intoarce baza in care a scris."""
    with conn.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS public.sonda_izolare "
                    "(id serial PRIMARY KEY, cum text, creat_la timestamptz DEFAULT now())")
        cur.execute("INSERT INTO public.sonda_izolare (cum) VALUES (%s)", (cum,))
        cur.execute("SELECT current_database()")
        unde = cur.fetchone()[0]
    if cum == "commit":
        conn.commit()
    elif cum == "rollback":
        conn.rollback()
    # cum == "nimic": exact cazul care ne-a adus aici — nici commit, nici rollback
    return unde


def test_explicit_commit_cannot_persist_to_production():
    """TEST_EXPLICIT_COMMIT_CANNOT_PERSIST_TO_PRODUCTION — un `commit()` EXPLICIT, nu o scapare."""
    _cere_mediu_izolat()
    psycopg2 = _psycopg2()
    c = psycopg2.connect(os.environ["DATABASE_URL"], connect_timeout=5)
    try:
        unde = _scrie_si(c, "commit")
        assert unde != mt.PRODUCTIE_DBNAME, "commit explicit a aterizat in productie"
        assert unde == _stare()["dbname"], (
            "commitul a aterizat in %r, nu in baza declarata %r" % (unde, _stare()["dbname"]))
        # ANTI-VACUUM: sa se fi si scris ceva, altfel proba trece pe o scriere care n-a avut loc
        with c.cursor() as cur:
            cur.execute("SELECT count(*) FROM public.sonda_izolare WHERE cum='commit'")
            assert cur.fetchone()[0] > 0, "nu s-a persistat nimic — proba n-a exercitat nimic"
    finally:
        c.close()


def test_second_connection_cannot_persist_to_production():
    """TEST_SECOND_CONNECTION_CANNOT_PERSIST_TO_PRODUCTION — a DOUA conexiune, deschisa pe langa
    pool, exact tiparul care ocoleste orice disciplina de tranzactie din `db.get_conn`."""
    _cere_mediu_izolat()
    from core import db
    psycopg2 = _psycopg2()
    db.init_pool()
    with db.get_conn() as prima:
        with prima.cursor() as cur:
            cur.execute("SELECT current_database()")
            unde_pool = cur.fetchone()[0]
        a_doua = psycopg2.connect(os.environ["DATABASE_URL"], connect_timeout=5)
        try:
            unde_a_doua = _scrie_si(a_doua, "commit")
        finally:
            a_doua.close()
        prima.rollback()
    assert unde_pool != mt.PRODUCTIE_DBNAME, "pool-ul suitei e legat la productie"
    assert unde_a_doua != mt.PRODUCTIE_DBNAME, "a doua conexiune a aterizat in productie"
    assert unde_pool == unde_a_doua, (
        "pool-ul si conexiunea directa ajung in baze DIFERITE (%r vs %r) — atunci nu se stie ce "
        "aparam" % (unde_pool, unde_a_doua))


def test_missing_rollback_cannot_persist_to_production():
    """TEST_MISSING_ROLLBACK_CANNOT_PERSIST_TO_PRODUCTION — cazul REAL din 10.09: se scrie si nu se
    incheie tranzactia. Chiar si asa, nimic nu poate ajunge in productie."""
    _cere_mediu_izolat()
    psycopg2 = _psycopg2()
    c = psycopg2.connect(os.environ["DATABASE_URL"], connect_timeout=5)
    try:
        unde = _scrie_si(c, "nimic")       # fara commit, fara rollback — ca la incident
        assert unde != mt.PRODUCTIE_DBNAME, (
            "o tranzactie neincheiata a putut atinge productia")
    finally:
        c.close()                           # inchiderea da inapoi tranzactia, in baza de TEST
