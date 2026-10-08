# -*- coding: utf-8 -*-
"""GARDA deciziei Costin 08.10.2026 §6 pct.4 (verbatim în DECIZII):

  „Luna preluării: editabilă în Date firmă, cu valoarea dedusă ca propunere, dar niciodată după luna primei note. Recalculează
  propunerea pentru F3 (are note din iunie). Schimbarea se jurnalizează.”

CE FACE IMPOSIBIL: o lună a preluării după prima notă din jurnal (refuz, lângă câmp — `erori_campuri` până la ecran); o schimbare
nejurnalizată; o propunere care sare peste nota cea mai veche; Control fiscal care ignoră luna aleasă.
Schemă efemeră din `tenant_template.sql`, ștearsă la ieșire. Nimic în tabele partajate.
"""
import io

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_luna_preluare"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture()
def conn():
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("INSERT INTO %s.firma_profil (id, nume, cui) VALUES (1, 'PRELUARE SRL', 'RO14399840')" % SCH)
            cur.execute("INSERT INTO %s.inregistrari (data, descriere, sursa, status) VALUES ('2099-06-15', 'prima', 'manual', 'ciorna')" % SCH)
        c.commit()
    with _db.get_conn(SCH) as c:
        yield c
        c.rollback()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def test_dupa_prima_nota_se_refuza_langa_camp(conn):
    """„niciodată după luna primei note” — refuzul își numește câmpul. MUTAȚIE: verificarea `_lp.eroare` scoasă din salveaza_date ->
    07/2099 se salvează -> pică."""
    from core import firma_profil_api as fp
    r = fp.salveaza_date(conn, {"luna_preluare": "2099-07"}, user_id=1)
    from core import luna_preluare as lp
    import datetime
    assert (r["ok"], r["camp"], r["mesaj"]) == (False, "luna_preluare",
                                                 lp.eroare(datetime.date(2099, 7, 1), datetime.date(2099, 6, 15)))


def test_salvata_jurnalizata_si_efectiva(conn):
    """„Schimbarea se jurnalizează.” MUTAȚIE: "luna_preluare" scos din CAMPURI_JURNAL -> niciun rând în jurnal -> pică."""
    from core import firma_profil_api as fp
    d = fp.citeste_date(conn)["profil"]["luna_preluare"]
    assert (d["salvata"], d["propunere"], d["prima_nota"]) == (None, "2099-06", "2099-06")   # fără tenant: numai prima notă
    assert fp.salveaza_date(conn, {"luna_preluare": "2099-04"}, user_id=7)["ok"]
    d = fp.citeste_date(conn)["profil"]["luna_preluare"]
    assert (d["salvata"], d["efectiva"]) == ("2099-04", "2099-04")
    with conn.cursor() as cur:
        cur.execute("SELECT camp, valoare_veche, valoare_noua, user_id FROM firma_profil_jurnal")
        assert cur.fetchall() == [("luna_preluare", None, "2099-04-01", 7)]


def test_ruta_trimite_campul_refuzului(monkeypatch):
    """Refuzul din Date firmă ajunge la ecran cu câmpul lui (`erori_campuri`), nu numai cu fraza. MUTAȚIE: ruta ridică numai mesajul
    -> pică."""
    from core import erori, uc_tenants as uc, firma_profil_api as fp
    monkeypatch.setattr(uc._uc_comun, "_schema_sau_404", lambda ctx, tid: SCH)
    monkeypatch.setattr(fp, "salveaza_date", lambda conn, date, **k: {"ok": False, "camp": "luna_preluare", "mesaj": "nu"})
    with pytest.raises(erori.DateInvalide) as e:
        uc.firma_profil_date_salveaza(1, {"luna_preluare": "2099-07"}, {"uid": 1})
    d = e.value.args[0]
    assert d["erori_campuri"] == [{"camp": "luna_preluare", "mesaj": "nu"}]


def test_control_fiscal_citeste_luna_efectiva():
    """Control fiscal numără de la luna EFECTIVĂ (salvată, altfel propunerea). MUTAȚIE: `efectiva` -> `deduse` în control_fiscal_api ->
    luna salvată ignorată -> pică."""
    import ast
    import inspect
    from core import control_fiscal_api as cf
    apeluri = {(n.func.value.id if isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) else None,
                n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func, "id", None))
               for n in ast.walk(ast.parse(inspect.getsource(cf))) if isinstance(n, ast.Call)}
    assert ("_lp", "efectiva") in apeluri and ("_lp", "deduse") not in apeluri
