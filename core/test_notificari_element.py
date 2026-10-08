# -*- coding: utf-8 -*-
"""GARDA deciziei Costin 08.10.2026, pct.4 (verbatim în DECIZII 08.10.2026): „Notificările fără element (44, 45, 46, 48) nu rămân
active în clopoțel: se marchează rezolvate, cu motivul «elementul nu mai există».”

CLASA, nu cele patru rânduri: o notificare DE ACȚIUNE (`de_validat`, `respinsa`) fără element în legătură nu se poate rezolva
niciodată. CE FACE IMPOSIBIL:
  * o astfel de notificare nerezolvată în bază — `notificari_element_ck` o refuză (gard în bază, nu disciplină în cod);
  * ca rezerva veche (`link="validat"`) să se mai nască din cod — `_link_element` cere elementul;
  * ca migrarea să lase vreuna activă — le marchează `inexistent`;
  * ca „a fost respinsă” a unei declarații să rămână activă după ce declarația intră din nou în coadă (trigger, `inlocuit`);
  * ca o valoare de `rezolvata` să n-aibă etichetă în clopoțel.

Rulează într-o tranzacție anulată (tabele partajate `public.*`); perioada 2099, sintetică.
"""
import io
import os
import re

import psycopg2
import pytest

from core import db as _db

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture()
def tx():
    p = _db.pool()
    conn = p.getconn()
    cur = conn.cursor()
    cur.execute("SELECT id, accounting_firm_id FROM public.users WHERE accounting_firm_id IS NOT NULL ORDER BY id LIMIT 1")
    uid, cab = cur.fetchone()
    try:
        yield conn, cur, uid, cab
    finally:
        conn.rollback()
        p.putconn(conn)


def _incearca(cur, tip, link):
    cur.execute("SAVEPOINT s")
    try:
        cur.execute("INSERT INTO public.notificari (user_id, tip, text, link) VALUES (%s, %s, 'proba', %s)",
                    (_UID[0], tip, link))
        cur.execute("RELEASE SAVEPOINT s")
        return True
    except psycopg2.errors.CheckViolation:
        cur.execute("ROLLBACK TO SAVEPOINT s")
        return False


_UID = [None]


def test_baza_refuza_notificarea_de_actiune_fara_element(tx):
    """MUTAȚIE: `notificari_element_ck` scos din `SQL_PUBLIC` (și baza remigrată) -> inserarea trece -> pică."""
    conn, cur, uid, cab = tx
    _UID[0] = uid
    refuzate = {(t, l) for t in ("de_validat", "respinsa") for l in ("validat", None, "jurnal:") if not _incearca(cur, t, l)}
    assert refuzate == {(t, l) for t in ("de_validat", "respinsa") for l in ("validat", None, "jurnal:")}
    assert all(_incearca(cur, t, l) for t, l in (("de_validat", "validat:7"), ("respinsa", "jurnal:1:2:2099:1"),
                                               ("aprobata", "validat")))   # informativele nu cer element


def test_migrarea_marcheaza_inexistent_si_reface_gardul(tx):
    """Cele patru de pe producție erau `de_validat`/`respinsa` cu `link='validat'`. MUTAȚIE: UPDATE-ul din `SQL_PUBLIC` scos ->
    ADD CONSTRAINT cade pe rândurile vechi -> pică."""
    from core import migrare_decizii_0810 as m
    conn, cur, uid, cab = tx
    _UID[0] = uid
    cur.execute("ALTER TABLE public.notificari DROP CONSTRAINT notificari_element_ck")
    ids = []
    for tip in ("de_validat", "respinsa"):
        cur.execute("INSERT INTO public.notificari (user_id, tip, text, link) VALUES (%s, %s, 'veche', 'validat') RETURNING id",
                    (uid, tip))
        ids.append(cur.fetchone()[0])
    marcate = m.public_ddl(conn)
    assert set(ids) <= {x[0] for x in marcate}
    cur.execute("SELECT DISTINCT rezolvata FROM public.notificari WHERE id = ANY(%s)", (ids,))
    assert cur.fetchall() == [("inexistent",)]
    cur.execute("SELECT 1 FROM pg_constraint WHERE conname = 'notificari_element_ck'")
    assert cur.fetchone()


def test_declaratia_retrimisa_rezolva_a_fost_respinsa(tx):
    """MUTAȚIE: ramura `TG_OP = 'INSERT'` scoasă din trigger -> notificarea rămâne activă -> pică."""
    from core import coada_api as c, uc_comun as u
    conn, cur, uid, cab = tx
    cur.execute("INSERT INTO public.tenants (schema_name, nume, accounting_firm_id) VALUES ('zt_notif_0810', 'ZT notif', %s) "
                "RETURNING id", (cab,))
    tid = cur.fetchone()[0]
    r = c.adauga_in_coada(conn, cab, tid, "d300", 2099, {"xml": "<a/>"}, "proba", luna=1, creat_de_id=uid)
    assert r["ok"], r
    cur.execute("UPDATE public.declaratii_coada SET stare = 'respinsa' WHERE id = %s", (r["coada_id"],))
    u._notif_pregatitor(conn, r["coada_id"], "respinsa", "lipsește un rând")
    cur.execute("SELECT id, link, rezolvata FROM public.notificari WHERE user_id = %s AND tip = 'respinsa' ORDER BY id DESC LIMIT 1",
                (uid,))
    nid, link, rez = cur.fetchone()
    assert (link, rez) == ("validat:%d" % r["coada_id"], None)        # cu elementul, activă
    assert c.adauga_in_coada(conn, cab, tid, "d300", 2099, {"xml": "<b/>"}, "proba", luna=1, creat_de_id=uid)["ok"]
    cur.execute("SELECT rezolvata FROM public.notificari WHERE id = %s", (nid,))
    assert cur.fetchone() == ("inlocuit",)


def test_codul_nu_mai_naste_legatura_fara_element():
    """Rezerva `"validat"` a dispărut; lipsa elementului e eroare. MUTAȚIE: rezerva pusă înapoi în `_link_element` -> pică."""
    from core import uc_comun as u
    assert u._link_element(12) == "validat:12"
    for gol in (None, 0, ""):
        with pytest.raises(ValueError):
            u._link_element(gol)


def test_fiecare_valoare_rezolvata_are_eticheta_in_clopotel():
    """Valorile permise în bază (`notificari_rezolvata_ck`) = cheile etichetelor din clopoțel. MUTAȚIE: `inexistent` scos din
    `REZ` (navigator.js) -> pică."""
    from core import migrare_decizii_0810 as m
    permise = set(re.findall(r"'(\w+)'", m.SQL_PUBLIC.split("notificari_rezolvata_ck", 2)[2].split(")")[0] + ")"))
    js = io.open(os.path.join(_RAD, "static", "js", "navigator.js"), encoding="utf-8").read()
    rez = js.split("const REZ = {", 1)[1].split("};", 1)[0]
    chei = set(re.findall(r"(\w+):\s*\"", rez))
    assert permise == {"validat", "respins", "inlocuit", "inexistent"}
    assert chei == permise
