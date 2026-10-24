# -*- coding: utf-8 -*-
"""Lotul 12, pachetul datefirma — Date firmă: „Luna preluării” (147, 169) și forma juridică din ANAF (20).

147 (comanda Costin 12.1, verbatim): „«Luna preluării» editabilă, cu propunere și limită”; decizia Costin 08.10.2026 §6 pct.4 (verbatim în
DECIZII): „Luna preluării: editabilă în Date firmă, cu valoarea dedusă ca propunere, dar niciodată după luna primei note.”
Drumul găsit în lotul 12, neacoperit de garda de la salvare (`core/test_luna_preluare.py`): luna aleasă (08) și, DUPĂ alegere, o notă mai
veche (06) — luna efectivă rămânea 08, deci după prima notă, iar Control fiscal număra restanțele abia din 08. Acum luna efectivă e plafonată
la luna primei note (`luna_preluare.efectiva` / `de_unde` / `stare.plafonata`), la citire, pentru toți cititorii (Control fiscal, lista
termenelor, soldurile bilanțului, e-Factura SPV), fără să rescrie luna aleasă.

20 (comanda Costin 12.1, verbatim): „Forma juridică și capitalul verificate abia la final; forma neprecompletată din ANAF”. Partea de server
a precompletării: la adăugarea firmei, forma din răspunsul ANAF (`date_generale.forma_juridica`, valorile văzute pe un răspuns REAL — v.
`capital_social._FORMA_ANAF`), când ANAF și denumirea spun același lucru, se scrie în Date firmă — fără să suprascrie forma aleasă de
contabil. Până azi nicio gardă nu păzea scrierea (numai `forma_propusa`, funcția pură).

Temei: N/A — regulă de produs (decizia Costin 08.10.2026 §6 pct.4), nu fiscală; forma juridică: Legea 31/1990 art.74 alin.(3) (de ce se
cere — `capital_social.TEMEI`), nu se schimbă aici. Schemă efemeră din `tenant_template.sql`, în ROLLBACK; perioade sintetice (2099).
"""
import datetime as _dt
import io

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_lot12_datefirma"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def cur():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as c:
                c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                c.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
                c.execute("SET LOCAL search_path TO %s, public" % SCH)
                c.execute("INSERT INTO firma_profil (id, nume, cui) VALUES (1, 'PRELUARE PROBA SRL', '14399840') ON CONFLICT (id) DO NOTHING")
                yield c
        finally:
            conn.rollback()


def _nota(c, zi):
    c.execute("INSERT INTO inregistrari (data, descriere, sursa, status) VALUES (%s, 'notă mai veche', 'manual', 'ciorna')", (zi,))


# ── 147 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_147_luna_aleasa_dupa_o_nota_mai_veche_se_plafoneaza_la_prima_nota():
    """PUR. „niciodată după luna primei note” (decizia 08.10 §6 pct.4): luna aleasă 08/2099, prima notă 15.06.2099 (scrisă după alegere)
    -> luna efectivă 06/2099, cu motivul; luna aleasă dinaintea primei note rămâne cum e. MUTAȚIE: plafonarea scoasă din `efectiva`
    (`if plafonata(...)`) -> (2099, 8) -> pică."""
    from core import luna_preluare as lp
    aleasa, creat, prima = _dt.date(2099, 8, 1), _dt.date(2099, 9, 21), _dt.date(2099, 6, 15)
    assert lp.plafonata(aleasa, prima) is True
    assert lp.efectiva(aleasa, creat, None, prima) == (2099, 6)       # decizia 08.10 §6 pct.4: „niciodată după luna primei note”
    assert lp.de_unde(aleasa, creat, None, prima) == ("luna primei note din jurnal, 15.06.2099 (luna aleasă în Date firmă, 08/2099, e "
                                                       "după ea)")
    # luna aleasă dinaintea primei note (sau chiar luna ei): aleasă, neschimbată
    for ok in (_dt.date(2099, 5, 1), _dt.date(2099, 6, 1)):
        assert lp.plafonata(ok, prima) is False
        assert lp.efectiva(ok, creat, None, prima) == (ok.year, ok.month)
        assert lp.de_unde(ok, creat, None, prima) == "aleasă în Date firmă"
    # fără notă: nimic de plafonat
    assert lp.efectiva(aleasa, creat, None, None) == (2099, 8) and lp.plafonata(aleasa, None) is False
    assert lp.stare({"salvata": aleasa, "creat_la": creat, "data_solduri": None, "prima_nota": prima}) == {
        "salvata": "2099-08", "propunere": "2099-06", "efectiva": "2099-06", "prima_nota": "2099-06", "plafonata": True}


def test_def_147_nota_scrisa_dupa_alegere_muta_luna_efectiva_la_toti_cititorii(cur):
    """Pașii, pe drumul funcțiilor ecranului: Date firmă -> luna preluării 08/2099 -> „Salvează” (fără note: se salvează) -> se scrie o notă
    din 15.06.2099 -> Date firmă: luna efectivă 06/2099, plafonată (luna aleasă rămâne 08/2099 în bază, cum a scris-o omul); soldurile de
    preluare ale bilanțului sunt la 31.05.2099 (ziua dinaintea lunii efective), nu la 31.07. MUTAȚIE: `"plafonata": plafonata(s, p)` scos
    din `stare` -> cheia lipsește -> pică; plafonarea scoasă din `efectiva` -> 31.07.2099 -> pică."""
    from core import bilant_api as ba, firma_profil_api as fp
    r = fp.salveaza_date(cur.connection, {"luna_preluare": "2099-08"}, user_id=1)
    assert r.get("ok"), r
    _nota(cur, "2099-06-15")
    lp = fp.citeste_date(cur.connection)["profil"]["luna_preluare"]
    assert (lp["salvata"], lp["efectiva"], lp["prima_nota"], lp["plafonata"]) == ("2099-08", "2099-06", "2099-06", True), lp
    cur.execute("SELECT luna_preluare FROM firma_profil WHERE id = 1")
    assert cur.fetchone()[0] == _dt.date(2099, 8, 1)                  # luna aleasă nu se rescrie tacit
    from psycopg2.extras import RealDictCursor
    with cur.connection.cursor(cursor_factory=RealDictCursor) as dc:   # cititorul bilanțului lucrează pe cursor-dicționar
        assert ba.data_soldurilor(dc, SCH) == _dt.date(2099, 5, 31)    # bilant_api.data_soldurilor: ziua dinaintea lunii preluării


def test_def_147_salvarea_altui_camp_nu_e_refuzata_de_luna_plafonata(cur):
    """Ecranul nu trimite luna neschimbată (`date_firma.js`: `_lp.value !== _lp.dataset.initiala`), deci salvarea altui câmp (seria
    chitanțelor) trece, iar luna aleasă rămâne. Trimisă din nou (08/2099, după prima notă) e refuzată lângă câmp, ca la prima salvare.
    MUTAȚIE: verificarea `_lp.eroare` scoasă din `salveaza_date` -> 08/2099 se salvează peste nota din 06 -> pică."""
    from core import firma_profil_api as fp, luna_preluare as lp
    assert fp.salveaza_date(cur.connection, {"luna_preluare": "2099-08"}, user_id=1).get("ok")
    _nota(cur, "2099-06-15")
    r = fp.salveaza_date(cur.connection, {"serie_chitanta": "PRB"}, user_id=1)
    assert r.get("ok"), r
    r = fp.salveaza_date(cur.connection, {"luna_preluare": "2099-08"}, user_id=1)
    assert (r["ok"], r.get("camp")) == (False, "luna_preluare"), r
    assert r["mesaj"] == lp.eroare(_dt.date(2099, 8, 1), _dt.date(2099, 6, 15))


# ── 20 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_20_forma_juridica_se_precompleteaza_din_anaf_la_adaugarea_firmei(cur):
    """La adăugarea firmei (`precompleteaza_din_anaf`, sursa unică a tuturor drumurilor de creare): ANAF spune „SOCIETATE COMERCIALA CU
    RASPUNDERE LIMITATA” (valoare de pe un răspuns REAL v9, `capital_social._FORMA_ANAF`) și denumirea „… S.R.L.” -> forma SRL în Date firmă;
    o formă aleasă deja de contabil nu se suprascrie; ANAF și denumirea în dezacord -> nimic scris (nu se ghicește). MUTAȚIE: ramura
    `forma_juridica = COALESCE(forma_juridica, %s)` scoasă din `precompleteaza_din_anaf` -> forma rămâne goală -> pică."""
    d = {"denumire": "PRELUARE PROBA S.R.L.", "cod_caen": "6202", "adresa": "Str 1", "nr_reg_com": "J40/1/2099", "platitor_tva": False,
         "tva_la_incasare": False, "tva_data_inceput": None, "forma_juridica": "SOCIETATE COMERCIALA CU RASPUNDERE LIMITATA"}
    _tp.precompleteaza_din_anaf(cur.connection, SCH, d)
    cur.execute("SELECT forma_juridica FROM firma_profil WHERE id = 1")
    assert cur.fetchone()[0] == "SRL"
    cur.execute("UPDATE firma_profil SET forma_juridica = 'SNC' WHERE id = 1")   # aleasă de contabil
    _tp.precompleteaza_din_anaf(cur.connection, SCH, d)
    cur.execute("SELECT forma_juridica FROM firma_profil WHERE id = 1")
    assert cur.fetchone()[0] == "SNC"
    cur.execute("UPDATE firma_profil SET forma_juridica = NULL WHERE id = 1")
    _tp.precompleteaza_din_anaf(cur.connection, SCH, dict(d, denumire="PRELUARE PROBA SA"))   # ANAF: SRL, denumirea: SA
    cur.execute("SELECT forma_juridica FROM firma_profil WHERE id = 1")
    assert cur.fetchone()[0] is None
