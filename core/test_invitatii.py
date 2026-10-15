# -*- coding: utf-8 -*-
"""Conturile noi de cabinet NUMAI prin invitație (comanda Costin 14.10.2026, pct.3, verbatim în DECIZII „Lotul 2”).

Pe baza de test, într-o tranzacție anulată: invitația e valabilă 14 zile, o singură dată, numai pentru emailul invitat; tokenul nu stă
în bază (numai hash-ul lui); înregistrarea fără invitație e refuzată ÎNAINTE de orice scriere.
MUTAȚII: `consuma` fără verificarea emailului -> ROȘU; `register` fără cererea invitației -> ROȘU."""
import datetime
import secrets
import types

import pytest

from core import db, erori, invitatii as inv


@pytest.fixture()
def cur():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as c:
            yield c
        conn.rollback()


def test_invitatia_valida_o_singura_data_numai_pentru_emailul_ei(cur):
    tok = inv.creeaza(cur, " Cabinet@Exemplu.RO ", None)
    assert inv.stare(cur, tok) == {"valida": True, "email": "cabinet@exemplu.ro", "refuz": None}
    with pytest.raises(ValueError) as e:
        inv.consuma(cur, tok, "altcineva@exemplu.ro", 1)
    assert str(e.value).startswith("Invitația e pentru alt email")
    inv.consuma(cur, tok, "cabinet@exemplu.ro", 1)
    s = inv.stare(cur, tok)
    assert (s["valida"], s["email"]) == (False, "cabinet@exemplu.ro") and (s["refuz"]["fel"], s["refuz"]["cod"]) == ("neconformitate", "FOLOSITA")
    with pytest.raises(ValueError):
        inv.consuma(cur, tok, "cabinet@exemplu.ro", 1)


def test_tokenul_nu_sta_in_baza_si_invitatia_expira(cur):
    tok = inv.creeaza(cur, "exp@exemplu.ro", None)
    cur.execute("SELECT count(*) FROM public.invitatii_cabinet WHERE token_hash = %s", (tok,))
    assert cur.fetchone()[0] == 0                                              # numai hash-ul e în bază
    peste = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=inv.VALABILITATE_ZILE, hours=1)
    s = inv.stare(cur, tok, acum=peste)
    assert s["valida"] is False and s["refuz"]["cod"] == "EXPIRATA"
    assert inv.stare(cur, "token-inventat")["valida"] is False


def test_inregistrarea_fara_invitatie_e_refuzata_inainte_de_orice_scriere(monkeypatch):
    """[15.10.2026, lotul 4] cu comutatorul pe „numai prin invitație” (fără invitație, refuzul depinde de mod)."""
    from core import uc_auth, auth_api, setari_platforma
    monkeypatch.setattr(setari_platforma, "mod_inregistrare", lambda cur: {"mod": setari_platforma.INVITATIE})
    chemat = []
    monkeypatch.setattr(auth_api, "inregistreaza_cabinet", lambda *a, **k: chemat.append(1) or {"ok": False, "mesaj": "x"})
    date = types.SimpleNamespace(email="nou@exemplu.ro", parola=secrets.token_urlsafe(18),   # refuzată înainte de orice scriere: n-ajunge nicăieri
                                   nume_cabinet="Cabinet Nou", nume=None,
                                 prenume=None, cui=None, accept_termeni=True, invitatie=None)
    with pytest.raises(erori.FaraDrept) as e:
        uc_auth.register(date)
    assert str(e.value) == inv.MESAJ_FARA_INVITATIE and chemat == []
    date.invitatie = "token-inventat"
    with pytest.raises(erori.FaraDrept) as e:
        uc_auth.register(date)
    assert str(e.value).startswith("Invitația nu există") and chemat == []
