# -*- coding: utf-8 -*-
"""D112 — ziua de diminuare a certificatului inițial de concediu medical (lotul 07.10, decizia Costin „DA”, 06.10.2026).

Fost: datoria strictă `test_datorie_d112_salariul_realizat_cu_ziua_de_diminuare` (06.10.2026). `d112.pull` proratea salariul
REALIZAT pe zilele PLĂTITE ale certificatului (`zile_ang + zile_fnuass`), nu pe zilele lui (`zile`). Pe certificatul INIȚIAL
ziua de diminuare e zi de concediu fără indemnizație — și fără salariu —, dar D112 o declara lucrată: salariu și contribuții cu o
zi în plus față de statul de plată, iar 421 rămânea nesoldat cu netul ei.

Ce se probează aici, pe schemă efemeră din `tenant_template.sql`, prin aceleași funcții pe care le cheamă aplicația
(`salariati_api.salveaza_concediu`, `stat_plata_api.stat_plata`, `d112.pull`, `d112.genereaza`):
  1. salariul realizat din D112 = cel din statul de plată, pe certificatul inițial cu diminuare (cazul datoriei);
  2. zilele lucrate declarate (B1_15 / B2_2 / B4_1) = zilele active minus zilele CERTIFICATULUI, iar zilele plătite (D_14+D_15)
     = zilele certificatului minus ziua de diminuare; DUK valid;
  3. pe certificatul fără diminuare (program național, exceptat) zilele plătite = zilele certificatului — nicio schimbare.
"""
import io

import pytest

from core import db
from core.common import Perioada


def _db_ok():
    try:
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")

SCH = "efemer_d112_diminuare"


@pytest.fixture
def firma():
    from core import tenant_provisioning as _tp
    with db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute('SET search_path TO "%s", public' % SCH)
            cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,platitor_tva,tip_decont,declarant_nume,"
                        "declarant_prenume,declarant_functie,patron_nume) VALUES (1,'ZT CM SRL','14399840','Str 1','Buc',"
                        "'B','6202',true,'L','Pop','Ion','administrator','Pop Ion')")
            cur.execute("WITH s AS (INSERT INTO salariati (cnp,nume,prenume,data_angajare,ore_zi,judet_casa,cor,data_nastere,"
                        "tip_asigurat,functie_baza) VALUES ('1800101410013','IONESCU','X','2024-01-01',8,'B','251401',"
                        "'1980-01-01','1',true) RETURNING id, data_angajare) INSERT INTO salariu_istoric (salariat_id, "
                        "valabil_din, salariu_brut) SELECT id, data_angajare, 6000 FROM s RETURNING salariat_id")
            sid = cur.fetchone()[0]
        c.commit()
    try:
        yield sid
    finally:
        with db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            c.commit()


def _cm(c, sid, **k):
    from core import salariati_api
    corp = {"cod": "01", "zile_cm": 5, "venituri_6_luni": 36000, "zile_6_luni": 126, "serie": "CMZT", "numar": "1",
            "data_acordare": "2026-10-06", "data_inceput": "2026-10-06", "data_sfarsit": "2026-10-12", "an": 2026, "luna": 10}
    corp.update(k)
    return salariati_api.salveaza_concediu(c, sid, corp)


def _atribute(xml, element):
    import re
    m = re.search(r"<%s ([^>]*)/>" % element, xml)
    assert m, "lipsește <%s> din D112" % element
    return {a: v for a, v in re.findall(r'(\w+)="([^"]*)"', m.group(1))}


def test_salariul_realizat_d112_egal_statul_pe_certificatul_initial_cu_diminuare(firma):
    """Cazul datoriei: certificat INIȚIAL de 5 zile, acordat 06.10.2026 -> 1 zi de diminuare, 4 plătite."""
    from core import d112, stat_plata_api
    with db.get_conn(SCH) as c:
        _cm(c, firma)
        rand = next(r for r in stat_plata_api.stat_plata(c, SCH, 2026, 10) if r["id"] == firma)
        _p, sal = d112.pull(c, SCH, Perioada(an=2026, luna=10))
        s = next(x for x in sal if x["id"] == firma)
        c.rollback()
    # OUG 91/2025 art.II alin.(1): indemnizația „se calculează și se plătesc prin diminuarea cu o zi”; ziua diminuată rămâne zi
    # de concediu medical (Ordinul 506/1030/2026) — salariul ei nu e realizat, deci D112 și statul proratează pe aceleași zile.
    assert round(float(s["brut_lucrat"]), 2) == round(rand["brut"], 2), (s["brut_lucrat"], rand["brut"])
    # zilele de concediu medical numărate de D112 = zilele certificatului (5), ca `cm_zile` din statul de plată
    assert s["zile_cm"] == rand["cm_zile"] == 5


def test_d112_zile_lucrate_fara_ziua_de_diminuare_si_duk_valid(firma):
    from core import d112, duk
    with db.get_conn(SCH) as c:
        _cm(c, firma)
        xml, _res = d112.genereaza(c, SCH, Perioada(an=2026, luna=10))
        _p, sal = d112.pull(c, SCH, Perioada(an=2026, luna=10))
        s = next(x for x in sal if x["id"] == firma)
        c.rollback()
    b1, b2, b4, dd = (_atribute(xml, e) for e in ("asiguratB1", "asiguratB2", "asiguratB4", "asiguratD"))
    # B1_15 / B2_2 / B4_1 = zilele lucrate în contract: zilele active minus TOATE zilele certificatului (5), nu doar cele plătite
    assert int(b1["B1_15"]) == int(b2["B2_2"]) == int(b4["B4_1"]) == s["zile_active"] - 5
    # structura D112 0726: „la D_14/D_15 (zile suportate de angajator/FNUASS) se va scădea 1 zi (prima zi)” -> 5 - 1 = 4
    assert int(dd["D_14"]) + int(dd["D_15"]) == int(dd["D_16"]) == 4
    rez = duk.valideaza(xml, "d112", an=2026, luna=10)
    assert rez.get("stare") == "valid", rez


def test_fara_diminuare_zilele_platite_egale_cu_ale_certificatului(firma):
    """Program național de sănătate: exceptat de la diminuare (Ordinul 506/1030/2026 art.78^4 alin.(2^1)) -> nimic de scăzut."""
    from core import d112
    with db.get_conn(SCH) as c:
        _cm(c, firma, program_national=True)
        xml, _res = d112.genereaza(c, SCH, Perioada(an=2026, luna=10))
        _p, sal = d112.pull(c, SCH, Perioada(an=2026, luna=10))
        s = next(x for x in sal if x["id"] == firma)
        c.rollback()
    dd = _atribute(xml, "asiguratD")
    assert int(dd["D_16"]) == 5   # toate cele 5 zile ale certificatului sunt plătite
    assert int(_atribute(xml, "asiguratB1")["B1_15"]) == s["zile_active"] - 5   # zilele lucrate: aceeași regulă
