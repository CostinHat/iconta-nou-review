# -*- coding: utf-8 -*-
"""[lotul 17.5-X, auditul Pilot din 13.11.2026, 45 de poziții, pe versiunea 17.5-I] Logica de server (și data propusă a notei noi, în browser) a punctelor P3, P4, P5, P8.

P3 (739): numărul NIR propus = maximul numerelor NIR ale firmei + 1, comparate ca NUMERE; dublura rămâne refuzată; citirea nu scrie.
P4 (484): «Diferență neexplicată: X lei.» pe un singur rând, fără note în ciornă pe cont; D390 o singură dată, la «De urmărit», cu un singur motiv; luna comparată.
P5 (F089): verificarea stocurilor compară VALIDAT cu VALIDAT; ciornele de stoc apar separat, cu suma lor.
P8 (602.1, 781): Verificările numără notele ca Registrul jurnal (o notă o dată, în toate stările); data propusă la nota nouă într-o lună blocată (browser, ceas înghețat).
Schemă efemeră din tenant_template, ROLLBACK la final; browserul, ca în core/test_lot11_w4_ecrane.py (rute simulate, ceas fix)."""
import contextlib
import datetime
import os
from decimal import Decimal

import pytest

from core import control_fiscal_api as cf, control_incrucisat as ci, erori as _erori, stocuri_cv_api, uc_comun, uc_control_fiscal, uc_tenants
from core import db as _db, tenant_provisioning as _tp
from core.ceas_proba import DATA_REF
from core.test_lot11_w4_ecrane import FIRMA, _pagina, browser  # noqa: F401 — `browser` e fixtura modulului (server static + Chromium)

_SCHEMA = "test_pilot_17_5_x"
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@contextlib.contextmanager
def _firma():
    """Firmă efemeră (schemă din șablon); `core.db.get_conn` întoarce conexiunea ei cât tine blocul, ca funcțiile aplicației să vadă datele necomise."""
    c = _db.pool().getconn()
    with c.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
        cur.execute(_tp.parametrizeaza_template(open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), _SCHEMA))
        cur.execute("SET search_path TO %s, public" % _SCHEMA)
    try:
        yield c
    finally:
        c.rollback()
        with c.cursor() as cur:
            cur.execute("RESET search_path")
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
        c.commit()
        _db.pool().putconn(c)


@contextlib.contextmanager
def _aceeasi_conexiune(monkeypatch, c):
    @contextlib.contextmanager
    def get_conn(schema=None):
        yield c
    monkeypatch.setattr(_db, "get_conn", get_conn)
    yield


def _nir(cur, numar, data):
    cur.execute("INSERT INTO nir (numar, data, furnizor) VALUES (%s, %s, 'Furnizor SRL') RETURNING id", (numar, data))
    return cur.fetchone()[0]


def _nota(cur, data, status="validata", linii=1, debit="371", credit="401", suma=10):
    cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status) VALUES (%s,'N','t',%s) RETURNING id", (data, status))
    nid = cur.fetchone()[0]
    for _ in range(linii):
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)", (nid, debit, credit, suma))
    return nid


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


# ── P3 (739): numărul NIR propus ───────────────────────────────────────────────────────────────────────────────────────────────────────
def test_numarul_nir_propus_e_maximul_comparat_ca_numar_plus_unu():
    """«10» > «9» (ca text ar fi invers); numerele repetate (1, 1) și cele nenumerice nu strică; maximul e al firmei, peste ani și luni."""
    with _firma() as c:
        with c.cursor() as cur:
            for nr, d in (("1", "2025-12-30"), ("2", "2026-01-10"), ("1", "2026-02-03"), ("9", "2026-03-04"), ("10", "2026-05-06"), ("A-30", "2026-06-07"), ("7", "2026-07-08")):
                _nir(cur, nr, d)
        assert uc_tenants._numar_nir_propus(c, _SCHEMA, 2026) == 11


def test_numarul_nir_propus_fara_niciun_nir_e_unu():
    with _firma() as c:
        assert uc_tenants._numar_nir_propus(c, _SCHEMA, 2026) == 1


def test_numarul_nir_propus_nu_scrie_nimic_la_citire():
    with _firma() as c:
        with c.cursor() as cur:
            _nir(cur, "7", "2026-03-04")
            cur.execute("SELECT count(*) FROM nir")
            inainte = cur.fetchone()[0]
        assert uc_tenants._numar_nir_propus(c, _SCHEMA, 2026) == 8
        with c.cursor() as cur:
            cur.execute("SELECT count(*) FROM nir")
            assert cur.fetchone()[0] == inainte


def test_dublura_unui_numar_nir_ramane_refuzata_in_acelasi_an_si_numarul_propus_nu_e_dublura():
    with _firma() as c:
        with c.cursor() as cur:
            _nir(cur, "8", "2026-02-01")
            assert uc_tenants._nir_cu_numarul(cur, _SCHEMA, "8", "2026-05-01") is not None   # negativ: numărul 8 e deja dat în 2026
        propus = uc_tenants._numar_nir_propus(c, _SCHEMA, 2026)
        assert propus == 9
        with c.cursor() as cur:
            assert uc_tenants._nir_cu_numarul(cur, _SCHEMA, str(propus), "2026-05-01") is None   # numărul propus nu e o dublură


# ── P4 (484): mesajul unic, D390 o singură dată, luna comparată ────────────────────────────────────────────────────────────────────
def test_fara_note_in_ciorna_mesajul_e_diferenta_neexplicata_si_nimic_altceva_despre_ea():
    with _firma() as c:
        cs = [{"stare": "rosu", "cont": k, "diferenta": Decimal("1341.00")} for k in ("4423", "4424", "4427", "4426")]
        out = ci.ciorne_care_explica(c, _SCHEMA, "2099-10-01", "2099-11-01", cs)
    for x in out:
        assert x["explicatie_ciorne"].startswith("Diferență neexplicată: %s." % ci._lei(Decimal("1341.00"))), x["explicatie_ciorne"]
        assert "poate veni din" not in x["explicatie_ciorne"] and "nu vine din" not in x["explicatie_ciorne"]   # un singur mesaj, fără al doilea care îl contrazice


def test_cu_note_in_ciorna_textul_notelor_ramane():
    with _firma() as c:
        with c.cursor() as cur:
            _nota(cur, "2099-10-05", "ciorna", debit="4111", credit="4427", suma=100)
        cs = [{"stare": "rosu", "cont": "4427", "diferenta": Decimal("100")}]
        out = ci.ciorne_care_explica(c, _SCHEMA, "2099-10-01", "2099-11-01", cs)
    assert out[0]["explicatie_ciorne"].startswith("Note în ciornă pe contul 4427 în perioadă: 1, cu suma de %s." % ci._lei(Decimal("100")))
    assert out[0]["ciorne_explica"] is True


def test_d390_profil_fara_ic_dar_facturi_ic_apare_o_singura_data_cu_un_singur_motiv():
    v = {"platitor_tva": True, "tip_decont": "lunar", "operatiuni_ic": False, "regim_fiscal": "profit"}
    rez = cf.obligatii_datorate(v, are_salariati=False, azi=date_ref(), d390_fapt=lambda a, m: True)
    assert [n for n in rez["neclar"] if n["tip"] == "d390"] == []                       # nimic la «Nu se poate verifica»
    d390 = [d for d in rez["datorate"] if d["tip"] == "d390"]
    assert d390
    for d in d390:   # un singur motiv pe lună, cu textul impus
        assert d["fapt"] == ("operațiuni intracomunitare înregistrate în %s; profilul firmei spune fără operațiuni intracomunitare — corectează în Date firmă" % d["perioada"])


def test_d390_cu_profil_corect_ramane_cu_motivul_simplu():
    v = {"platitor_tva": True, "tip_decont": "lunar", "operatiuni_ic": True, "regim_fiscal": "profit"}
    rez = cf.obligatii_datorate(v, are_salariati=False, azi=date_ref(), d390_fapt=lambda a, m: True)
    for d in (x for x in rez["datorate"] if x["tip"] == "d390"):
        assert d["fapt"] == "operațiuni intracomunitare înregistrate în %s" % d["perioada"]


def date_ref():
    return datetime.date(2026, 7, 23)


def test_luna_comparata_implicit_ultima_incheiata_si_cererea_se_valideaza():
    azi = datetime.date(2026, 11, 15)
    assert uc_control_fiscal._luna_comparata(None, None, azi) == (2026, 10)
    assert uc_control_fiscal._luna_comparata(2026, 9, azi) == (2026, 9)
    assert uc_control_fiscal._luna_comparata(2026, 10, azi) == (2026, 10)
    assert uc_control_fiscal._luna_comparata(2025, 12, datetime.date(2026, 1, 20)) == (2025, 12)
    for an, luna in ((2026, 11), (2027, 1), (2026, 13), (2026, 0), (2026, None), (None, 5)):   # negativ: luna în curs, viitoare, inexistentă, incompletă
        with pytest.raises(_erori.DateInvalide):
            uc_control_fiscal._luna_comparata(an, luna, azi)


def test_selectorul_lunii_comparate_incepe_la_cea_mai_veche_luna_cu_note_si_pune_cele_noi_intai():
    with _firma() as c:
        with c.cursor() as cur:
            _nota(cur, "2026-03-05", "ciorna")
            _nota(cur, "2026-09-30")
        r = cf._luni_comparabile(c, _SCHEMA, (2026, 9), (2026, 10))
    assert [x["eticheta"] for x in r["luni_comparabile"]] == ["10/2026", "09/2026", "08/2026", "07/2026", "06/2026", "05/2026", "04/2026", "03/2026"]
    assert r["luni_comparabile"][0] == {"an": 2026, "luna": 10, "eticheta": "10/2026"}
    assert r["luna_comparata"] == {"an": 2026, "luna": 9, "eticheta": "09/2026"}


def test_selectorul_fara_nicio_nota_are_numai_luna_implicita():
    with _firma() as c:
        r = cf._luni_comparabile(c, _SCHEMA, (2026, 10), (2026, 10))
    assert [x["eticheta"] for x in r["luni_comparabile"]] == ["10/2026"]


# ── P5 (F089): validat contra validat, ciornele separat ────────────────────────────────────────────────────────────────────────────
def test_verificarea_stocurilor_compara_validat_cu_validat_si_arata_ciornele_separat(monkeypatch):
    recon = [{"cont": "371", "sold_contabil": "6272.38", "valoare_validata": "6272.38", "valoare_ciorna": "3251.90", "diferenta": "0.00", "ok": True,
              "necalculat": 0, "cauze": []}]
    monkeypatch.setattr(stocuri_cv_api, "reconciliere", lambda conn, schema, articole_lista=None: recon)
    monkeypatch.setattr(uc_tenants.auth_api, "schema_tenant", lambda conn, uid, tid: _SCHEMA)
    with _firma() as c, _aceeasi_conexiune(monkeypatch, c):
        r = uc_tenants.verificare_stocuri(1, {"uid": 1})
    assert r["ok"] is True                                              # ciornele nu produc „diferență”
    assert r["conturi"][0]["valoare_fise_cv"] == "6272.38"              # fișele VALIDATE, nu cu ciornele (9.524,28)
    assert r["conturi"][0]["valoare_ciorna"] == "3251.90" and r["ciorne"] == "3251.90"   # ciornele, pe linie separată, cu suma lor


def test_verificarea_stocurilor_pastreaza_diferenta_reala_dintre_validate(monkeypatch):
    recon = [{"cont": "371", "sold_contabil": "6272.38", "valoare_validata": "6000.00", "valoare_ciorna": "0.00", "diferenta": "272.38", "ok": False,
              "necalculat": 0, "cauze": []}]
    monkeypatch.setattr(stocuri_cv_api, "reconciliere", lambda conn, schema, articole_lista=None: recon)
    monkeypatch.setattr(uc_tenants.auth_api, "schema_tenant", lambda conn, uid, tid: _SCHEMA)
    with _firma() as c, _aceeasi_conexiune(monkeypatch, c):
        r = uc_tenants.verificare_stocuri(1, {"uid": 1})
    assert r["ok"] is False and r["conturi"][0]["diferenta"] == "272.38" and r["ciorne"] == "0.00"   # negativ: o diferență între validate rămâne diferență


# ── P8 (602.1, 781): numărătoarea ──────────────────────────────────────────────────────────────────────────────────────────────────────
def test_verificarile_numara_notele_lunii_ca_registrul_jurnal_o_nota_o_data_in_toate_starile(monkeypatch):
    with _firma() as c, _aceeasi_conexiune(monkeypatch, c):
        with c.cursor() as cur:
            _nota(cur, "2026-10-05", "validata", linii=3)     # o notă cu trei linii = o notă
            _nota(cur, "2026-10-31", "ciorna", linii=2)       # ciorna se numără
            _nota(cur, "2026-09-30", "validata")              # altă lună
            _nota(cur, "2026-11-01", "validata")              # altă lună
            _nota(cur, "2026-10-12", "validata")
        assert uc_comun._numar_note_luna(_SCHEMA, 2026, 10) == 3
        assert uc_comun._numar_note_luna(_SCHEMA, 2026, 8) == 0


# ── P8 (781): data propusă la o notă nouă într-o lună blocată (browser, ceas înghețat 03.11.2026) ─────────────────────────────────────
def _luni_blocate(*luni):
    return [{"an": a, "luna": m} for a, m in luni]


def _nota_noua(browser, blocate, an, luna):
    ruta = {"/jurnal": {"note": [], "total_debit": 0, "total_credit": 0, "ciorne": {"note": 0, "total": 0}}, "/centre-cost": {"centre": []},
            "/perioade-blocate": {"blocate": blocate, "controale": {"blocaje": [], "semnale": []}}}
    pg, erori = _pagina(browser, 1366, 768, ruta)
    try:
        pg.evaluate("""async ([an, luna]) => { const f = await import('/static/js/ecrane/firme.js');
          window._nav.deschide('Registru jurnal', (c, n) => f.ecranJurnal(c, n, %s, {an, luna}), {lat: 'tabel'}); }""" % FIRMA, [an, luna])
        pg.wait_for_selector("#j-nota-noua", timeout=15000)
        pg.click("#j-nota-noua")
        pg.wait_for_selector("#je-data", timeout=10000)
        pg.wait_for_timeout(300)
        data = pg.input_value("#je-data")
        motiv = pg.inner_text("#je-data-motiv") if pg.locator("#je-data-motiv").count() else ""
    finally:
        pg.close()
    assert not erori, erori
    return data, motiv


def test_nota_noua_pe_luna_blocata_propune_ultima_zi_a_ultimei_luni_deschise(browser):
    data, motiv = _nota_noua(browser, _luni_blocate((2026, 9)), 2026, 9)
    assert data == "2026-10-31"                                          # 10/2026 e încheiată și deschisă, înaintea lunii curente (noiembrie, ceasul ferestrei)
    assert motiv == "Luna 09/2026 e blocată: s-a propus 31.10.2026, ultima zi a ultimei luni deschise."


def test_nota_noua_cu_doua_luni_blocate_propune_ultima_zi_a_celei_mai_recente_luni_incheiate_neblocate(browser):
    data, motiv = _nota_noua(browser, _luni_blocate((2026, 9), (2026, 10)), 2026, 9)
    assert data == "2026-08-31"
    assert motiv == "Luna 09/2026 e blocată: s-a propus 31.08.2026, ultima zi a ultimei luni deschise."


def test_nota_noua_fara_nicio_luna_incheiata_neblocata_propune_ziua_ceasului(browser):
    blocate = _luni_blocate(*[((2016 + (i + 10) // 12), (i + 10) % 12 + 1) for i in range(-1, 121)])   # 10/2016 … 11/2026: nicio lună încheiată deschisă în cele 120 de luni căutate
    data, motiv = _nota_noua(browser, blocate, 2026, 10)
    assert data == DATA_REF.isoformat()
    assert motiv.startswith("Luna 10/2026 e blocată: s-a propus 03.11.2026, ziua de azi")


def test_nota_noua_pe_luna_deschisa_ramane_ca_pana_acum(browser):
    data, motiv = _nota_noua(browser, _luni_blocate((2026, 9)), 2026, 11)   # luna curentă a ceasului, deschisă: ziua de azi, fără motiv scris
    assert data == DATA_REF.isoformat() and motiv == ""
    data, motiv = _nota_noua(browser, _luni_blocate((2026, 9)), 2026, 10)   # o lună încheiată deschisă: câmpul rămâne gol (aplicația nu alege o zi în locul omului)
    assert data == "" and motiv == ""
