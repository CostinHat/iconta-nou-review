# -*- coding: utf-8 -*-
"""[lotul 11, deficiența 440 — W3a, comanda Costin 11.1 pct.16, verbatim în DECIZII „Comanda 11.1”: „toate erorile apar deodată, fiecare
cu textul ei, în casetă și lângă câmp; pe toată aplicația”.]

Pentru fiecare formular reparat în W3a: un corp cu CEL PUȚIN DOUĂ greșeli primește un singur refuz care le numește pe TOATE
(`erori_campuri` cu ≥ 2 rânduri, fiecare cu câmpul ei — id-ul de pe ecran sau numele din cerere pe care ecranul îl traduce). Înainte,
fiecare se oprea la prima. Fără temei fiscal: e regula formularului (DS cap.6 v2.99, `core.erori.ErorileFormularului`); valorile fiscale
din mesaje (plafoane, cote) nu se afirmă aici, se citesc din modulul lor.

Pe bază (unde formularul citește firma): schemă efemeră din `tenant_template.sql`, în ROLLBACK. Use-case-urile din `uc_tenants` se
cheamă cu accesul și luna deschisă înlocuite (monkeypatch) — refuzul se ia ÎNAINTEA oricărei scrieri, deci nu atinge nicio bază.
"""
import contextlib
import io
import os
import types

import pytest

from core import erori

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = "ztest_lot11_w3a"


def _campuri(det):
    return [c["camp"] for c in (det.get("erori_campuri") or [])]


def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    from core import db, tenant_provisioning as _tp
    db.init_pool()
    with db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
                cur.execute("INSERT INTO firma_profil (id, nume, cui) VALUES (1, 'ZT W3A', '14399840')")
            yield c
        finally:
            c.rollback()


# ── B1 / A1: Date firmă ─────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_b1_date_firma_toate_erorile_deodata_nimic_scris(conn):
    """MUTAȚIE: `return _refuz_formular(er, coduri)` mutat după prima eroare (forma veche `return {... _er[0] ...}`) -> 1 eroare -> pică."""
    from core import firma_profil_api as fp
    r = fp.salveaza_date(conn, {"telefon": "0722000440", "serie_chitanta": "CH-440!", "data_infiintare": "2999-01-01",
                                "capital_subscris": "-5", "cont_venit_implicit": "401"}, tenant_id=None, user_id=7)
    assert r["ok"] is False, r
    assert set(_campuri(r)) >= {"serie_chitanta", "data_infiintare", "capital_subscris", "cont_venit_implicit"}, r   # 440: toate deodată
    assert r["camp"] == r["erori_campuri"][0]["camp"]                     # apelanții care citeau un singur câmp îl găsesc pe primul
    assert all(c["mesaj"] in r["mesaj"] for c in r["erori_campuri"]), r   # „fiecare cu textul ei” și în casetă
    with conn.cursor() as cur:
        cur.execute("SELECT telefon FROM firma_profil")
        assert cur.fetchone() == (None,)                                   # nimic scris pe jumătate


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_a1_use_case_date_firma_trimite_toate_erorile(conn, monkeypatch):
    """`uc_tenants.firma_profil_date_salveaza` nu mai turtește refuzul la primul câmp. MUTAȚIE: `_ec = r.get("erori_campuri") or` scos ->
    o singură eroare -> pică."""
    from core import uc_tenants as uc, uc_comun
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda ctx, tid: SCH)
    monkeypatch.setattr(uc.db, "get_conn", lambda *a, **k: contextlib.nullcontext(conn))
    with pytest.raises(erori.DateInvalide) as ei:
        uc.firma_profil_date_salveaza(1, {"serie_chitanta": "CH-440!", "data_infiintare": "nu-e-data"}, {"uid": 7})
    assert _campuri(ei.value.detaliu) == ["serie_chitanta", "data_infiintare"], ei.value.detaliu


# ── B19 / A2: regimul TVA la încasare ───────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_b19_tva_incasare_ambele_date_invalide(conn):
    """MUTAȚIE: `if ef: return _refuz_adunat(ef)` mutat după prima dată -> o eroare -> pică."""
    from core import regim_tva_incasare as rti
    with conn.cursor() as cur:
        r = rti.salveaza(cur, True, de_la="31.02.2026", pana_la="x", user_id=7)
    assert r["ok"] is False and _campuri(r) == ["tva_incasare_de_la", "tva_incasare_pana_la"], r


# ── B10: vectorul fiscal ────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_b10_vector_fiscal_toate_alegerile_lipsa(conn):
    """MUTAȚIE: `return _refuz_adunat(er)` pus imediat după prima `er.append` -> pică."""
    from core import vector_fiscal_api as vf
    r = vf.salveaza(conn, "", None, None, None, user_id=7)
    assert r["ok"] is False, r
    assert set(_campuri(r)) == {"platitor_tva", "operatiuni_ic", "regim_fiscal"}, r
    assert r["cod"] == "TVA_LIPSA" and r["camp"] == "platitor_tva", r     # codul și câmpul primei, ca înainte


# ── B2 / A3: Casă (dispoziția) ──────────────────────────────────────────────────────────────────────────────────────────────────
def test_b2_casa_dispozitie_data_categorie_suma_deodata():
    """Refuzul se ia înainte de orice citire din bază (conn=None). MUTAȚIE: `if er: return _refuz_adunat(er, coduri)` mutat după
    verificarea datei -> o eroare -> pică."""
    from core import casa_api as ca
    r = ca.adauga(None, "s", {"data": "2026-02-31", "categorie": "nu_exista", "suma": 0})
    assert _campuri(r) == ["c-data", "c-cat", "c-suma"], r               # id-urile din formularul Casă (firme.js)
    assert all(c["mesaj"] in r["eroare"] for c in r["erori_campuri"]), r


def test_a3_use_case_casa_pastreaza_erori_campuri(monkeypatch):
    """`uc_tenants.casa_adauga` trimitea numai textul (`c-avans-dest` se pierdea). MUTAȚIE: ramura `if rez.get("erori_campuri")` scoasă
    -> detaliul e text -> pică."""
    from core import uc_tenants as uc, casa_api as ca
    monkeypatch.setattr(uc.db, "get_conn", lambda *a, **k: contextlib.nullcontext(None))
    monkeypatch.setattr(uc.auth_api, "schema_tenant", lambda *a, **k: "s")
    monkeypatch.setattr(ca, "adauga", lambda conn, schema, corp: {"eroare": "a; b", "cod": "X",
                                                                   "erori_campuri": [{"camp": "c-suma", "mesaj": "a"},
                                                                                     {"camp": "c-avans-dest", "mesaj": "b"}]})
    with pytest.raises(erori.CerereGresita) as ei:
        uc.casa_adauga(1, {}, {"uid": 7})
    assert _campuri(ei.value.detaliu) == ["c-suma", "c-avans-dest"], ei.value.detaliu


# ── B3: NIR ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_b3_nir_decizia_si_cota_fiecarei_linii(conn):
    """Factura sosită nealeasă, cota transportului nealeasă și DOUĂ linii fără cotă: un refuz cu toate patru. MUTAȚIE: `fara_cota`
    redus la prima linie (`[:1]`) -> pică."""
    from core import stocuri_api as sa, metoda_stoc as ms
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET metoda_stoc = %s", (ms.CV,))
    linii = [{"denumire": "A", "cantitate": 1, "pret_achizitie": 10}, {"denumire": "B", "cantitate": 2, "pret_achizitie": 5}]
    r = sa.adauga_nir(conn, SCH, {"numar": "1", "data": "2026-10-01", "linii": linii, "transport": 5}, cere_decizia=True)
    assert _campuri(r) == ["sn-factura-sosita", "sn-transport-cota", "nir-l0-cota_tva", "nir-l1-cota_tva"], r
    assert r["cod"] == sa.COD_FACTURA_NEDECLARATA, r


# ── B5: factura (formă) ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_b5_factura_cota_fiecarei_linii_si_scadenta():
    """MUTAȚIE: `if _er: raise FacturaRefuzata(_er)` mutat în bucla cotei -> o eroare -> pică."""
    from core import facturi_api as fa
    with pytest.raises(fa.FacturaRefuzata) as ei:
        fa.creeaza_factura(None, "1", "2026-10-10", "emisa", [{"descriere": "x"}, {"descriere": "y"}], tert_pf=True,
                           data_scadenta="2026-10-01", tip_operatiune="ciudat")
    assert _campuri(ei.value.detaliu()) == ["linii[0].cota_tva", "linii[1].cota_tva", "data_scadenta", "tip_operatiune"]
    assert isinstance(ei.value, ValueError)                               # apelanții care prindeau `ValueError` îl prind la fel


# ── B7: concediul medical ───────────────────────────────────────────────────────────────────────────────────────────────────────
def test_b7_concediu_toate_campurile_certificatului():
    """Refuzul se ia înainte de orice citire (conn=None). MUTAȚIE: `_er.refuza()` mutat după verificarea codului -> pică."""
    from core import salariati_api as sa
    with pytest.raises(erori.DateInvalide) as ei:
        sa.salveaza_concediu(None, 1, {"cod": "99", "data_inceput": "2026-10-10", "data_sfarsit": "2026-10-01",
                                       "zile_cm": 0, "venituri_6_luni": 0, "zile_6_luni": 0})
    # (zilele din cele 6 luni: golul / 0 devine 1 la citire — `zile_6_luni or 1` —, deci nu intră aici)
    assert set(_campuri(ei.value.detaliu)) == {"cm-cod", "cm-sfarsit", "cm-ven6", "cm-zile"}, ei.value.detaliu


# ── B9: beneficiul lunar ────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_b9_beneficiu_eveniment_si_valoare():
    """MUTAȚIE: `return _refuz_adunat(er)` pus imediat după eroarea evenimentului -> pică."""
    from core import beneficii_api as ba
    r = ba.seteaza(None, "s", 1, 2026, 5, "cadou", -10, eveniment="ziua_mea")
    assert _campuri(r) == ["eveniment", "valoare"], r


# ── B17: întocmitorul bilanțului ────────────────────────────────────────────────────────────────────────────────────────────────
def test_b17_intocmitor_calitate_si_nume():
    """Refuzul se ia înainte de scriere (conn=None). MUTAȚIE: `if er:` mutat după calitate -> pică."""
    from core import uc_cabinet as uc
    r = uc.salveaza_intocmitor_conn(None, 1, {"calit_intocmit": "99", "nume_intocmit": "X" * 76, "nri_intocmit": "Y" * 16})
    assert r["ok"] is False and _campuri(r) == ["calit_intocmit", "nume_intocmit", "nri_intocmit"], r


# ── B18: înregistrarea cabinetului ──────────────────────────────────────────────────────────────────────────────────────────────
def test_b18_inregistrare_termeni_email_cabinet():
    """MUTAȚIE: `raise` repus după prima verificare (bifa termenilor) -> o eroare -> pică."""
    from core import uc_auth
    d = types.SimpleNamespace(accept_termeni=False, parola="Parola-Buna-440!", email="nu-e-email", nume_cabinet="", telefon="")
    with pytest.raises(erori.CerereGresita) as ei:
        uc_auth._valideaza_formularul(d)
    assert _campuri(ei.value.detaliu) == ["reg-termeni", "reg-email", "reg-cabinet"], ei.value.detaliu


# ── A4: câmpurile lipsă ale use-case-urilor (Operațiuni) ────────────────────────────────────────────────────────────────────────
def test_a4_campuri_lipsa_toate():
    """MUTAȚIE: `lipsa = [...]` redus la primul element -> pică."""
    from core import uc_comun
    with pytest.raises(erori.DateInvalide) as ei:
        uc_comun._campuri_lipsa({"suma": "", "cota": None, "data": "2026-10-01"}, ("suma", "cota", "data"))
    assert _campuri(ei.value.detaliu) == ["op-suma", "op-cota"], ei.value.detaliu
    assert uc_comun._campuri_lipsa({"a": 0}, ("a",)) == []                # 0 e o valoare, nu o lipsă


def _fara_baza(monkeypatch):
    from core import uc_tenants as uc, uc_comun
    _conn = types.SimpleNamespace(cursor=lambda *a, **k: contextlib.nullcontext(None))   # nicio interogare nu ajunge la bază
    monkeypatch.setattr(uc.db, "get_conn", lambda *a, **k: contextlib.nullcontext(_conn))
    monkeypatch.setattr(uc.repo_firma_profil, "platitor_tva", lambda *a, **k: (True,))
    monkeypatch.setattr(uc.auth_api, "schema_tenant", lambda *a, **k: "s")
    monkeypatch.setattr(uc_comun, "_cere_luna_deschisa", lambda *a, **k: None)
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda *a, **k: "s")
    return uc


@pytest.mark.parametrize("fn, corp, asteptat", [
    ("nota_leasing", {"tip": "rata"}, ["op-capital", "op-cota"]),
    ("vanzare_marja", {}, ["op-pret_vanzare", "op-pret_cumparare", "op-cota"]),
    ("nota_chirie", {"fel": "refacturare"}, ["op-total_factura", "op-parte_refacturata", "op-cota"]),
])
def test_a4_use_case_numeste_toate_campurile_lipsa(monkeypatch, fn, corp, asteptat):
    """Înainte: `KeyError` pe primul câmp -> „Lipsește câmpul `capital`” și atât. MUTAȚIE: chemarea `_campuri_lipsa` scoasă din
    use-case -> refuzul vechi, fără `erori_campuri` -> pică."""
    uc = _fara_baza(monkeypatch)
    with pytest.raises(erori.DateInvalide) as ei:
        getattr(uc, fn)(1, corp, {"uid": 7})
    assert _campuri(ei.value.detaliu) == asteptat, ei.value.detaliu


# ── B8 / B14 / B15 / B13: achizițiile și livrarea din Operațiuni ────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("fn, corp, asteptat", [
    ("achizitie_necorporala", {"tip": "nu_exista", "data": "2026-10-01"},
     ["op-tip", "op-denumire", "op-valoare", "op-cota", "op-furnizor_cui", "op-numar"]),
    ("achizitie_taxare_inversa", {"data": "2026-10-01"}, ["op-categorie", "op-valoare", "op-cota", "op-furnizor_cui", "op-numar"]),
    ("achizitie_ic", {"data": "2026-10-01", "tip": "x"}, ["op-valoare", "op-cota", "op-cod_tva_furnizor", "op-numar", "op-tip"]),
    ("vanzare_ic", {"tip": "x"}, ["op-cod_tva_client", "op-tip", "op-valoare"]),
])
def test_b8_b13_b14_b15_achizitii_toate_erorile(monkeypatch, fn, corp, asteptat):
    """MUTAȚIE: `_er.refuza()` mutat după prima verificare -> o eroare -> pică."""
    uc = _fara_baza(monkeypatch)
    with pytest.raises(erori.DateInvalide) as ei:
        getattr(uc, fn)(1, corp, {"uid": 7})
    assert _campuri(ei.value.detaliu) == asteptat, ei.value.detaliu


# ── B16: plan de conturi ────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_b16_plan_conturi_simbol_si_denumire(monkeypatch):
    """Înainte: un singur mesaj pentru amândouă, fără câmp. MUTAȚIE: `er.refuza()` mutat după simbol -> pică."""
    uc = _fara_baza(monkeypatch)
    with pytest.raises(erori.DateInvalide) as ei:
        uc.tenant_plan_conturi_adauga(1, types.SimpleNamespace(simbol="ABC", denumire=""), {"uid": 7})
    assert _campuri(ei.value.detaliu) == ["pc-simbol", "pc-denumire"], ei.value.detaliu
