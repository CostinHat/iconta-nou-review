# -*- coding: utf-8 -*-
"""[lotul 11, C89] Indemnizația de concediu medical se rotunjește la leu O DATĂ, la sursă (`salarizare.calcul_cm` / `calcul_cm_cod10`):
fluturașul (statul citește `concedii_medicale`) și D112 (D_20 / D_21, B3_7) poartă aceeași cifră.

SURSA. Normele de aplicare a OUG 158/2005 (Ordinul MS 15/2018 / CNAS 1.311/2017, `anaf_surse/oms_15_2018_norme.txt`): art.62 Exemplul
„Ci = Mzbci x.... % x NZLCM = 122, 95 lei x 75% x 22 = 2.028,68 lei, rotunjit la 2.029 lei conform legii”; art.63 (cod 10, reducerea
timpului de muncă) Exemplul nr.1: „Bmax = 2.499,59 lei x 25% = 624,89 lei, rotunjit la 625 lei conform legii; Ci = 2.499,59 lei -
1.875 lei = 624,59 lei, rotunjit la 625 lei conform legii”. Ordinul 506/1030/2026 (exemplul diminuării): „200,82 lei x 55% x 4 = 441,80
lei, rotunjit la 442 lei conform legii”. Modul (aritmetic, >= 0,50 -> +1): structura D112, antet — „Campurile calculate cu ajutorul
parametrilor vor avea valori intregi, pozitive obtinute prin rotunjire matematica” (exemplele normelor sunt toate peste 0,50: nu
transează jumătatea -> INTERPRETARE CU TEMEI, ca 453).

Până la 22.10.2026 indemnizația de cod 10 se întorcea cu bani (624,59), se stoca așa și ajungea pe fluturaș cu bani, iar D112 o
rotunjea (`_d112int`) -> 625 în declarație, 624,59 pe fluturaș.
"""
from decimal import Decimal

import pytest

from core import d112, db as _db, salarizare
from core.common import Perioada
from core.test_lot11_s9_deducere_plafon import _int, _setup, structura

_SCHEMA = "test_lot11_s9_cm"


def test_c89_cod10_exemplul_din_norme_rotunjit_la_leu():
    """Normele OUG 158/2005 art.63 Exemplul nr.1: Bcli 2.499,59, S 1.875 -> Ci = 624,59 -> 625; Bmax = 624,89 -> 625. ROȘU pe codul
    vechi: 624.59."""
    # „Ci = 2.499,59 lei - 1.875 lei = 624,59 lei, rotunjit la 625 lei conform legii”
    assert salarizare.calcul_cm_cod10(Decimal("2499.59"), Decimal("1875")) == Decimal("625.00")
    # plafonul (25% din bază) se aplică și el rotunjit: 2.499,59 × 25% = 624,89 -> 625; Ci 1.000 > Bmax -> 625
    assert salarizare.calcul_cm_cod10(Decimal("2499.59"), Decimal("1499.59")) == Decimal("625.00")
    # sub jumătate de leu se neglijează (rotunjire matematică, structura D112): 2.400,40 − 2.000 = 400,40 -> 400
    assert salarizare.calcul_cm_cod10(Decimal("2400.40"), Decimal("2000")) == Decimal("400.00")


def test_c89_cm_obisnuit_exemplul_din_norme():
    """Normele OUG 158/2005 art.62 Exemplul: Mzbci = 15.000 / 122 = 122,95, 75%, 22 de zile -> 2.028,68 -> 2.029 (și partea
    angajatorului rotunjită; FNUASS = diferența, întreagă)."""
    r = salarizare.calcul_cm(15000, 122, 22, cod="01", zile_episod=22, la_data=__import__("datetime").date(2025, 6, 1))
    assert r["brut"] == Decimal("2029.00"), r          # „2.028,68 lei, rotunjit la 2.029 lei conform legii”
    assert r["brut_ang"] == r["brut_ang"].to_integral_value() and r["brut_fnuass"] == r["brut"] - r["brut_ang"], r


def test_c89_garda_indemnizatia_intoarsa_e_intreaga():
    """Garda: orice indemnizație întoarsă de `calcul_cm` / `calcul_cm_cod10` e în lei întregi (brut, brut_ang, brut_fnuass) — pică dacă o
    cale nouă întoarce bani."""
    import datetime
    for ven, zile, zcm, cod in ((15000, 122, 22, "01"), (24300, 121, 5, "01"), (13125, 107, 7, "06"), (27000, 129, 10, "08"),
                                (31234.57, 125, 3, "01"), (19999.99, 123, 13, "09")):
        r = salarizare.calcul_cm(ven, zile, zcm, cod=cod, zile_episod=zcm, la_data=datetime.date(2026, 10, 1))
        for k in ("brut", "brut_ang", "brut_fnuass"):
            assert r[k] == r[k].to_integral_value(), (ven, zile, zcm, cod, k, r[k])
    for baza, venit in ((Decimal("2499.59"), Decimal("1875")), (Decimal("3333.33"), Decimal("2500.01")), (Decimal("1000.5"), 0)):
        v = salarizare.calcul_cm_cod10(baza, venit)
        assert v == v.to_integral_value(), (baza, venit, v)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            yield c
        finally:
            c.rollback()
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            c.commit()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c89_d112_recalculul_din_medie_ca_la_sursa(conn):
    """Certificat stocat fără sumă (brut_ang = brut_fnuass = 0): D112 completează suma din medie ca `calcul_cm` — totalul rotunjit O
    DATĂ, FNUASS = total − partea angajatorului. Brut 6.004, 06/2026: media 300,20 lei/zi, 55%, 3 zile angajator + 2 FNUASS -> total
    825,55 -> 826, angajator 495,33 -> 495, FNUASS 331 (B3_7 = D_20 + D_21 = 826). ROȘU pe codul vechi: 495 + 330 = 825 (două
    rotunjiri), cu un leu sub indemnizația pe care `calcul_cm` o dă pentru aceleași zile."""
    with conn.cursor() as cur:
        _setup(cur, [{"cnp": "1800101410013", "nume": "CM", "dn": "1980-06-01", "brut": 6004}], schema=_SCHEMA)
        cur.execute("INSERT INTO concedii_medicale (salariat_id,an,luna,cod,zile,zile_ang,zile_fnuass,brut_ang,brut_fnuass,baza,"
                    "media_zilnica,serie,numar,data_acordare,data_inceput,data_sfarsit,loc_prescriere) "
                    "SELECT id,2026,6,'01',5,3,2,0,0,6004,0,'AB','1','2026-06-01','2026-06-01','2026-06-05',1 FROM salariati")
    conn.commit()
    xml = d112.genereaza(conn, _SCHEMA, Perioada(an=2026, luna=6))[0]
    a = structura(xml)["1800101410013"]
    (d20, d21), (b37,) = _int(a, "asiguratD", "D_20", "D_21"), _int(a, "asiguratB3", "B3_7")
    # normele OUG 158/2005 art.62: Ci = Mzbci × % × NZLCM, „rotunjit … conform legii” — rotunjirea e a indemnizației (totalul)
    assert (d20, d21, b37) == (495, 331, 826), (d20, d21, b37)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c89_cod10_fluturas_si_d112_aceeasi_indemnizatie(conn):
    """Drumul contabilului: certificat cod 10 salvat (`salariati_api.salveaza_concediu`) — media 240,00 lei/zi × 10 zile = baza 2.400,
    venitul realizat 1.900,41 -> Ci = 499,59 -> 500 (Bmax 600). Statul / fluturașul (`cm_brut`) și D112 (D_21, B3_7) poartă 500. ROȘU pe
    codul vechi: stocat 499,59 -> fluturașul 499,59, D112 500."""
    from core import salariati_api, stat_plata_api
    with conn.cursor() as cur:
        _setup(cur, [{"cnp": "1800101410013", "nume": "COD10", "dn": "1980-06-01", "brut": 5000}], schema=_SCHEMA)
        cur.execute("SELECT id FROM salariati")
        sid = cur.fetchone()[0]
    # [lotul 12, C102.1] 01–15.06.2026 = 10 zile lucrătoare (1 iunie e sărbătoare legală, Rusalii și Ziua Copilului, Legea 53/2003
    # art.139 alin.(1)); până la 24.10.2026 fixtura scria 10 zile pe 01–12.06 (9 zile lucrătoare), pe care serverul o salva tăcut
    r = salariati_api.salveaza_concediu(conn, sid, {
        "serie": "AB", "numar": "77", "cod": "10", "data_acordare": "2026-06-01", "data_inceput": "2026-06-01",
        "data_sfarsit": "2026-06-15", "loc_prescriere": 1, "zile_cm": 10, "venituri_6_luni": 30000, "zile_6_luni": 125,
        "venit_realizat": "1900.41", "an": 2026, "luna": 6,
        # numărul avizului medicului expert (D112 D_13, „D_13#null pentru D_9 = 10”, DUK regula S102) — pe același câmp ca `d112`
        "cod_urgenta": 4321})
    # Normele OUG 158/2005 art.63 (cod 10): „Ci = Bcli - S … rotunjit … conform legii”
    assert Decimal(str(r["calcul"]["brut"])) == Decimal("500"), r["calcul"]
    conn.commit()
    with conn.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
    st = stat_plata_api.stat_plata(conn, _SCHEMA, 2026, 6)
    xml = d112.genereaza(conn, _SCHEMA, Perioada(an=2026, luna=6))[0]
    (d21,) = _int(structura(xml)["1800101410013"], "asiguratD", "D_21")
    assert st[0]["cm_brut"] == 500.0 == d21, (st[0]["cm_brut"], d21)
    from core import duk
    if not duk.poate_valida("d112"):
        pytest.skip("DUK d112 indisponibil")
    rez = duk.valideaza(xml, "d112", an=2026, luna=6)
    assert rez["stare"] == "valid", rez
