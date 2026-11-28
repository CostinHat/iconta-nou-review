# -*- coding: utf-8 -*-
"""[17.5-F6, pct.4] Secțiunea «Consultanță» a cabinetului (Cabinet 1–5 și 8 din comanda F5): rolurile, autorizarea pe server, cele două
carduri, firmele distincte, excluderea firmelor neeligibile, suma listei = cifra cardului, rezumatele pe firmă și invalidarea lor.

Agregarea (`uc_tenants.cabinet_consultanta`) se probează pe rezumate date (fără bază): firmele distincte când aceeași firmă intră pe ambele
carduri, starea la zero, firmele «în recalculare», suma listei. Rolurile, autorizarea, regula 501 / 502 pe firmă și invalidarea se probează pe
copia de test (firmele F1–F7 ale cabinetului de probă 48765, identitățile de test): administratorul (dovada.71507, 8 firme), asistentul fără
drept de conducere (dovada.71508, F1 / F2 / F5), utilizatorul fără firme (proba_reg_indpaznk, cabinet fără firme). Scrierile sunt în
tranzacții anulate la final (rollback), cu blocajul registrului aspect–sursă luat numai pe durata probei."""
import datetime as dt
from decimal import Decimal

import pytest

from core import firma_rezumat as FR

ADMIN, ASISTENT, FARA_FIRME = 71507, 71508, 14724
F1, F2, F3, F4, F5 = 105779, 105780, 105781, 105782, 105783


def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn() as c, c.cursor() as cur:
            cur.execute("SELECT count(*) FROM public.users WHERE id = ANY(%s)", ([ADMIN, ASISTENT, FARA_FIRME],))
            return cur.fetchone()[0] == 3
    except Exception:   # noqa: BLE001
        return False


# ───────────────────────── agregarea cabinetului, fără bază ─────────────────────────
def _model(**pe_firma):
    """{tid: {aspect: rând citit}} din {tid: (date_hotarari | None, date_consultanta | None)}; None = rezumat lipsă (în recalculare)."""
    out = {}
    for tid, (h, k) in pe_firma.items():
        out[tid] = {}
        for aspect, d in (("hotarari_aga", h), ("consultanta", k)):
            out[tid][aspect] = {"stare": FR.LIPSESTE, "date": None} if d is None else {"stare": FR.CURENT, "date": d}
    return out


def _cabinet(monkeypatch, firme, model):
    from core import uc_tenants, auth_api, db

    class _C:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(db, "get_conn", lambda *a, **k: _C())
    monkeypatch.setattr(auth_api, "tenantii_userului", lambda conn, uid: [dict(f) for f in firme])
    monkeypatch.setattr(FR, "citeste", lambda conn, ids, aspecte=None, azi=None: {t: v for t, v in model.items() if t in ids})
    return uc_tenants.cabinet_consultanta({"uid": 1})


H_DA = {"eligibil": True, "disponibil": "13800.00", "ultima": None}
H_NU = {"eligibil": False, "disponibil": "0.00", "ultima": None, "motiv": "fără profit"}


def _k(ec, *coduri):
    return {"eligibil": bool(coduri), "se_aplica": [{"cod": c, "nume": c, "suma": "1.00", "sens": "x"} for c in coduri], "lipsesc": [],
            "economie": ec}


def test_firmele_distincte_pe_ambele_carduri_si_suma_listei(monkeypatch):
    firme = [{"id": 1, "nume": "A", "cui": "1"}, {"id": 2, "nume": "B", "cui": "2"}, {"id": 3, "nume": "C", "cui": "3"},
             {"id": 4, "nume": "D", "cui": "4"}]
    r = _cabinet(monkeypatch, firme, {
        1: _model(x=(H_DA, _k("120.50", "M3")))["x"],          # pe ambele carduri: se numără o dată
        2: _model(x=(H_NU, _k("0.00", "M2")))["x"],             # numai 502
        3: _model(x=(H_NU, _k("0.00")))["x"],                   # nimic de făcut: nu apare în nicio listă
        4: _model(x=(None, None))["x"]})                         # rezumat lipsă: «în recalculare», nu «nimic de făcut»
    c = r["carduri"]
    assert r["firme_accesibile"] == 4 and r["firme_distincte"] == 2
    assert [f["tenant_id"] for f in c["hotarari_aga"]["firme"]] == [1] and c["hotarari_aga"]["n"] == 1
    assert [f["tenant_id"] for f in c["consultanta"]["firme"]] == [1, 2] and c["consultanta"]["n"] == 2
    assert c["hotarari_aga"]["in_recalculare"] == 1 and c["consultanta"]["in_recalculare"] == 1
    assert Decimal(c["consultanta"]["economie"]) == sum(Decimal(f["economie"]) for f in c["consultanta"]["firme"]) == Decimal("120.50")


def test_starea_la_zero_si_fara_firme(monkeypatch):
    r = _cabinet(monkeypatch, [{"id": 1, "nume": "A", "cui": "1"}], {1: _model(x=(H_NU, _k("0.00")))["x"]})
    assert r["firme_accesibile"] == 1 and r["firme_distincte"] == 0
    assert r["carduri"]["hotarari_aga"]["n"] == 0 and r["carduri"]["consultanta"]["n"] == 0 and r["carduri"]["consultanta"]["economie"] == "0.00"
    r0 = _cabinet(monkeypatch, [], {})
    assert r0["firme_accesibile"] == 0 and r0["firme_distincte"] == 0   # pagina nu desenează secțiunea (cabinet.js: !firme_accesibile)


def test_un_rezumat_cu_eroare_sau_invalidat_nu_se_arata_drept_curent(monkeypatch):
    m = {1: {"hotarari_aga": {"stare": FR.INVALIDAT, "date": H_DA}, "consultanta": {"stare": FR.CURENT, "date": {"eroare": "x"}}}}
    r = _cabinet(monkeypatch, [{"id": 1, "nume": "A", "cui": "1"}], m)
    assert r["carduri"]["hotarari_aga"]["n"] == 0 and r["carduri"]["hotarari_aga"]["in_recalculare"] == 1
    assert r["carduri"]["consultanta"]["n"] == 0 and r["carduri"]["consultanta"]["in_recalculare"] == 1


# ───────────────────────── pe copia de test: rolurile, autorizarea, regula pe firmă, invalidarea ─────────────────────────
pytestmark_db = pytest.mark.skipif(not _db_ok(), reason="copia de test indisponibilă")


@pytestmark_db
def test_rolurile_vad_numai_firmele_lor():
    """Administratorul vede firmele cabinetului lui (8), asistentul numai cele atribuite (3, fără drept de conducere), utilizatorul fără
    firme niciuna (secțiunea nu se desenează)."""
    from core import auth_api, db
    with db.get_conn() as c:
        adm = {f["id"] for f in auth_api.tenantii_userului(c, ADMIN)}
        asi = {f["id"] for f in auth_api.tenantii_userului(c, ASISTENT)}
        gol = auth_api.tenantii_userului(c, FARA_FIRME)
        with c.cursor() as cur:
            cur.execute("SELECT rol FROM public.users WHERE id = %s", (ASISTENT,))
            rol = cur.fetchone()[0]
    assert len(adm) == 8 and {F1, F2, F3, F4, F5} <= adm
    assert asi == {F1, F2, F5} and rol == "angajat"
    assert gol == []


@pytestmark_db
def test_autorizarea_pe_server_refuza_firma_neatribuita():
    """Cererea directă a ferestrei 502 pe o firmă neatribuită asistentului (F3) e refuzată pe server (404), ca la orice altă firmă străină;
    pe o firmă atribuită (F1) răspunde. Lista cabinetului asistentului nu conține firme din afara atribuirii."""
    from core import uc_tenants, erori
    with pytest.raises(erori.Inexistent):
        uc_tenants.consultanta_fiscala(F3, {"uid": ASISTENT}, "2026-11-03")
    r = uc_tenants.consultanta_fiscala(F1, {"uid": ASISTENT}, "2026-11-03")
    assert [m["cod"] for m in r["masuri"]] == ["M1", "M2", "M3", "M4", "M5"]
    cab = uc_tenants.cabinet_consultanta({"uid": ASISTENT})
    vazute = {f["tenant_id"] for card in cab["carduri"].values() for f in card["firme"]}
    assert vazute <= {F1, F2, F5} and cab["firme_accesibile"] == 3
    assert uc_tenants.cabinet_consultanta({"uid": FARA_FIRME})["firme_accesibile"] == 0


def _rezumat(conn, tid, schema, aspect):
    """Calculul aspectului pe conexiunea dată (vede scrierile neconfirmate ale probei) și scrierea lui cu versiunea surselor de acum."""
    import psycopg2.extras as E
    with conn.cursor() as cur:
        cur.execute('SET LOCAL search_path TO "%s", public' % schema)
    v = FR.versiune_aspect(conn, tid, aspect)
    if aspect == "hotarari_aga":
        from core import hotarare_dividende as H
        with conn.cursor(cursor_factory=E.RealDictCursor) as cur:
            d = H.rezumat_cabinet(cur, schema, dt.date(2026, 11, 3))
    else:
        d = _consultanta_fara_rollback(conn, schema, dt.date(2026, 11, 3))
    FR.scrie(conn, tid, aspect, d, v, epoca=FR.epoca_pentru(aspect, dt.date(2026, 11, 3)))
    return d


class _FaraRollback:
    """Conexiunea probei, cu `rollback` oprit: calculul 502 (care își anulează singur citirile) nu anulează scrierile probei."""

    def __init__(self, conn):
        self._c = conn

    def rollback(self):
        return None

    def __getattr__(self, nume):
        return getattr(self._c, nume)


def _consultanta_fara_rollback(conn, schema, la):
    """`consultanta_fiscala.rezumat_cabinet` pe conexiunea probei (proba ține scrierile ei până la final, apoi le anulează)."""
    from core import consultanta_fiscala as CF
    return CF.rezumat_cabinet(_FaraRollback(conn), schema, la)


def _schema(conn, tid):
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM public.tenants WHERE id = %s", (tid,))
        return cur.fetchone()[0]


@pytestmark_db
def test_hotarari_aga_scrierea_in_sursa_invalideaza_si_valoarea_se_reciteste():
    """Cabinet 5, aspectul 501: F2 are profit disponibil (117 / 1171) și nicio hotărâre în 2026 -> eligibilă. O notă care poartă o hotărâre
    de distribuire din 2026 (scrierea în sursa `inregistrari`) invalidează rezumatul (citirea îl dă «invalidat», nu «curent»); recalculat, el
    spune «hotărârea anului 2026 e făcută» și firma iese din listă."""
    from core import db
    with db.get_conn() as conn:
      try:
        FR.aplica_ddl(conn)   # registrul aspect–sursă proiectat din cod, în tranzacția probei (anulat la final)
        s2 = _schema(conn, F2)
        d0 = _rezumat(conn, F2, s2, "hotarari_aga")
        assert d0["eligibil"] is True and Decimal(d0["disponibil"]) > 0, d0
        assert FR.citeste(conn, [F2], ["hotarari_aga"], azi=dt.date(2026, 11, 3))[F2]["hotarari_aga"]["stare"] == FR.CURENT
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM "%s".inregistrari WHERE status <> %%s ORDER BY id LIMIT 1' % s2, ("validata",))
            r = cur.fetchone()
            if r is None:
                cur.execute('INSERT INTO "%s".inregistrari (data, descriere, status) VALUES (%%s, %%s, %%s) RETURNING id' % s2,
                            (dt.date(2026, 11, 2), "proba F6", "ciorna"))
                r = cur.fetchone()
            cur.execute('UPDATE "%s".inregistrari SET document_ref = %%s WHERE id = %%s' % s2,
                        ("Hotărârea adunării generale a asociaților nr 77 din 02.11.2026", r[0]))
        st = FR.citeste(conn, [F2], ["hotarari_aga"], azi=dt.date(2026, 11, 3))[F2]["hotarari_aga"]
        assert st["stare"] == FR.INVALIDAT, st
        d1 = _rezumat(conn, F2, s2, "hotarari_aga")
        assert d1["eligibil"] is False and "2026 e făcută" in d1["motiv"] and d1["ultima"]["numar"] == "77", d1
        st = FR.citeste(conn, [F2], ["hotarari_aga"], azi=dt.date(2026, 11, 3))[F2]["hotarari_aga"]
        assert st["stare"] == FR.CURENT and st["date"]["eligibil"] is False
      finally:
        conn.rollback()   # nimic din probă nu rămâne în copie


@pytestmark_db
def test_consultanta_scrierea_in_sursa_invalideaza_si_valoarea_se_reciteste():
    """Cabinet 5, aspectul 502: F1 (micro) are M2 «Se aplică» și M4 «Lipsesc date». Trecerea firmei la impozit pe profit (scrierea în sursa
    `firma_profil`) invalidează rezumatul; recalculat, M4 nu mai e printre măsurile cu date lipsă (plafonul micro nu se mai aplică)."""
    from core import db
    with db.get_conn() as conn:
      try:
        FR.aplica_ddl(conn)
        s1 = _schema(conn, F1)
        d0 = _rezumat(conn, F1, s1, "consultanta")
        assert d0["eligibil"] is True and "M4" in [m["cod"] for m in d0["lipsesc"]], d0
        with conn.cursor() as cur:
            cur.execute('UPDATE "%s".firma_profil SET regim_fiscal = %%s WHERE id = 1' % s1, ("profit",))
        st = FR.citeste(conn, [F1], ["consultanta"], azi=dt.date(2026, 11, 3))[F1]["consultanta"]
        assert st["stare"] == FR.INVALIDAT, st
        d1 = _rezumat(conn, F1, s1, "consultanta")
        assert "M4" not in [m["cod"] for m in d1["lipsesc"]], d1
        st = FR.citeste(conn, [F1], ["consultanta"], azi=dt.date(2026, 11, 3))[F1]["consultanta"]
        assert st["stare"] == FR.CURENT and st["date"] == d1
      finally:
        conn.rollback()   # nimic din probă nu rămâne în copie


@pytestmark_db
def test_firmele_neeligibile_nu_intra_in_liste():
    """PFA (F4, partidă simplă): în afara ambelor carduri; F3 (capitalul subscris necompletat): nu intră la «Hotărâri AGA», cu motivul
    lipsei de date; F5 (fără profit nerepartizat): nu intră la «Hotărâri AGA». Numai citiri."""
    from core import db, hotarare_dividende as H, consultanta_fiscala as CF
    import psycopg2.extras as E
    la = dt.date(2026, 11, 3)
    with db.get_conn() as c:
        sch = {t: _schema(c, t) for t in (F3, F4, F5)}
    for t in (F3, F4, F5):
        with db.get_conn(sch[t]) as cs:
            with cs.cursor(cursor_factory=E.RealDictCursor) as cur:
                h = H.rezumat_cabinet(cur, sch[t], la)
            k = CF.rezumat_cabinet(cs, sch[t], la)
        assert h["eligibil"] is False, (t, h)
        if t == F4:
            assert "SRL" in h["motiv"] and k["eligibil"] is False and "PFA" in k["motiv"]
        if t == F3:
            assert "capitalul social subscris" in h["motiv"]
        if t == F5:
            assert Decimal(h["disponibil"]) <= 0
