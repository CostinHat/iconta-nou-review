# -*- coding: utf-8 -*-
"""GARD — brutul se proratează pe prezența în contract: angajare/încetare în lună, CFP/suspendare, schimbare de salariu
(lot 19 pct.4c, 02.10.2026).

Defectul: statul de plată și D112 proratau brutul NUMAI la concediu medical. O angajare pe 16 primea toată luna
(B1_sal2, B2_5, contribuții, impozit), o încetare pe 12 la fel, CFP-ul nu se putea înregistra deloc, iar o mărire de
salariu pe 16 se aplica pe toată luna. Proratarea exista doar la facilitate și la pragul part-time.

Temei (Codul muncii, corpus `anaf_surse/legea_53_2003_codul_muncii.html`):
  · art.159 alin.(1): „Salariul reprezintă contraprestația muncii depuse de salariat în baza contractului individual de
    muncă.” — zilele dinaintea angajării / de după încetare nu se plătesc;
  · art.160 alin.(2): salariul de bază remunerează munca prestată „pe parcursul unei luni calendaristice” — o zi
    lucrătoare = salariul lunii / zilele lucrătoare ale lunii (INTERPRETARE CU TEMEI, v. salariu_istoric.brut_cuvenit);
  · art.49 alin.(2): „suspendarea contractului individual de muncă are ca efect suspendarea prestării muncii de către
    salariat și a plății drepturilor de natură salarială de către angajator”; art.54: CFP = suspendare prin acord.
D112 (structura, `anaf_surse/d112_struct_anaf.txt`): 29a B1_sal1 „Salariul de bază lunar brut prevăzut în contractul
individual de muncă”; 29b B1_sal2 „Venitul brut din salarii … realizat”; 35 B1_7 „Ore suspendate/ libere în luna”;
39 B1_15 „Total zile lucrate”.

Iunie 2026: 21 de zile lucrătoare (1 iunie = Rusalii + Ziua Copilului). Salarii de 6000 (peste minim: fără facilitate,
ca proratarea să se vadă curat).
"""
import xml.etree.ElementTree as ET
from decimal import Decimal

import pytest

from core import db as _db, tenant_provisioning as _tp
from core import d112, stat_plata_api, salariu_istoric as _si

_SCHEMA = "test_salariu_proratare"
# CNP-uri de test cu cifra de control VERIFICATĂ (algoritmul din CLAUDE.md), nu inventate.
_S = {  # cheie: (cnp, data_angajare, data_incetare)
    "angajat_16": ("1900101410011", "2026-06-16", None),
    "incetat_12": ("2900202410026", "2024-01-01", "2026-06-12"),
    "cfp_8_12": ("1850303410033", "2024-01-01", None),
    "marire_16": ("1960404410042", "2024-01-01", None),
    "luna_intreaga": ("2880505410059", "2024-01-01", None),
}


_IDS = {}   # id-urile salariaților din fixtură (conexiunea psycopg2 nu acceptă atribute noi)


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
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,regim_fiscal,"
                            "platitor_tva,tip_decont,declarant_nume,declarant_prenume,declarant_functie) VALUES "
                            "(1,'PRORATA SRL','14399840','Str 1','Buc','B','6202','BCR','RO49RNCB0000000000000001',"
                            "'profit',true,'L','Pop','Ion','administrator')")
                ids = {}
                for k, (cnp, da, di) in _S.items():
                    cur.execute("INSERT INTO salariati (cnp,nume,prenume,data_angajare,data_incetare,salariu_brut,ore_zi,"
                                "judet_casa) VALUES (%s,%s,'I',%s,%s,6000,8,'B') RETURNING id", (cnp, k.upper(), da, di))
                    ids[k] = cur.fetchone()[0]
                cur.execute("INSERT INTO salariu_istoric (salariat_id, valabil_din, salariu_brut) VALUES "
                            "(%s,'2024-01-01',6000),(%s,'2026-06-16',7000)", (ids["marire_16"], ids["marire_16"]))
                cur.execute("INSERT INTO suspendari_contract (salariat_id, data_inceput, data_sfarsit, tip) "
                            "VALUES (%s,'2026-06-08','2026-06-12','cfp')", (ids["cfp_8_12"],))
            _IDS.clear(); _IDS.update(ids)
            yield c
        finally:
            c.rollback()


def _asigurati(xml):
    """{cnp: {atribut: valoare}} din asiguratB1/B2, citit STRUCTURAL (nu „șir in xml”)."""
    out = {}
    for el in ET.fromstring(xml).iter():
        if el.tag.split("}")[-1] == "asigurat":
            d = {}
            for sub in el:
                if sub.tag.split("}")[-1] in ("asiguratB1", "asiguratB2"):
                    d.update(sub.attrib)
            out[el.get("cnpAsig")] = d
    return out


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_brut_cuvenit_pe_prezenta_in_contract(conn):
    cur = conn.cursor()
    i = _IDS

    def bc(k):
        _cnp, da, di = _S[k]
        susp = _si.suspendari_luna(cur, _SCHEMA, i[k], 2026, 6)
        return _si.brut_cuvenit(cur, _SCHEMA, i[k], 2026, 6, da, di, susp)
    # Codul muncii art.159 alin.(1) + art.160 alin.(2): 11 zile din 21 în contract (16-30 iunie) -> 6000 x 11/21
    assert bc("angajat_16") == Decimal("3142.86")
    # art.159 alin.(1): contract până pe 12 iunie -> 9 zile lucrătoare (2-5, 8-12) -> 6000 x 9/21
    assert bc("incetat_12") == Decimal("2571.43")
    # art.49 alin.(2) + art.54: CFP 8-12 iunie (5 zile lucrătoare) -> 6000 x 16/21
    assert bc("cfp_8_12") == Decimal("4571.43")
    # art.160 alin.(2), fiecare zi cu salariul ei: 10 zile la 6000 + 11 zile la 7000, din 21
    assert bc("marire_16") == Decimal("6523.81")
    # control: lună întreagă, fără schimbare -> exact salariul (nimic nu se mișcă pe cazul obișnuit)
    assert bc("luna_intreaga") == Decimal("6000.00")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_statul_de_plata_declara_brutul_proratat(conn):
    stat = {r["cnp"]: r for r in stat_plata_api.stat_plata(conn, _SCHEMA, 2026, 6)}
    br = {k: stat[_S[k][0]]["brut"] for k in _S}
    assert br == {"angajat_16": 3142.86, "incetat_12": 2571.43, "cfp_8_12": 4571.43,
                  "marire_16": 6523.81, "luna_intreaga": 6000.0}
    # transparența pe rând: salariul din contract rămâne cel din contract
    assert stat[_S["angajat_16"][0]]["brut_contractual"] == 6000.0 and stat[_S["angajat_16"][0]]["zile_active"] == 11
    # CAS 25% pe brutul realizat (CF art.138 lit.a)), nu pe salariul întreg: 3142,86 x 25% = 785,72 (785,7150)
    assert stat[_S["angajat_16"][0]]["cas"] == pytest.approx(785.72, abs=0.01)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d112_sal1_contractual_sal2_realizat_zile_si_ore_suspendate(conn):
    xml, _av = d112.genereaza(conn, _SCHEMA, 2026, 6)
    a = _asigurati(xml)
    c = {k: a[_S[k][0]] for k in _S}
    # 29a B1_sal1 = salariul din contract (la 30 iunie: 7000 pentru cel mărit); 29b B1_sal2 = brutul realizat
    assert {k: (int(c[k]["B1_sal1"]), int(c[k]["B1_sal2"])) for k in _S} == {
        "angajat_16": (6000, 3143), "incetat_12": (6000, 2571), "cfp_8_12": (6000, 4571),
        "marire_16": (7000, 6524), "luna_intreaga": (6000, 6000)}
    # 39 B1_15 „Total zile lucrate” = zilele din contract, nesuspendate; B2_2 aceeași valoare
    assert {k: int(c[k]["B1_15"]) for k in _S} == {"angajat_16": 11, "incetat_12": 9, "cfp_8_12": 16,
                                                   "marire_16": 21, "luna_intreaga": 21}
    assert all(c[k]["B2_2"] == c[k]["B1_15"] for k in _S)
    # 35 B1_7 „Ore suspendate/ libere în luna”: doar CFP-ul, 5 zile x 8 ore; ceilalți nu-l poartă
    assert c["cfp_8_12"].get("B1_7") == "40" and all("B1_7" not in c[k] for k in _S if k != "cfp_8_12")
    # B2_5 (baza CAS a lunii) = brutul realizat, nu salariul întreg
    assert int(c["angajat_16"]["B2_5"]) == 3143


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d112_proratat_e_valid_la_duk(conn):
    from core import duk
    if not duk.poate_valida("d112"):
        pytest.skip("DUK d112 indisponibil")
    xml, _av = d112.genereaza(conn, _SCHEMA, 2026, 6)
    r = duk.valideaza(xml, "d112", an=2026, luna=6)
    assert r["stare"] == "valid", r.get("erori")


def test_zile_active_si_suspendate_pe_calendar():
    from datetime import date
    # iunie 2026: 21 de zile lucrătoare; CFP 8-12 = 5 zile lucrătoare, excluse
    assert len(_si.zile_active(2026, 6)) == 21
    susp = [(date(2026, 6, 8), date(2026, 6, 12), "cfp")]
    assert len(_si.zile_active(2026, 6, "2024-01-01", None, susp)) == 16
    assert _si.zile_suspendate(2026, 6, "2024-01-01", None, susp) == 5
    # suspendarea dinaintea angajării nu se numără de două ori (zilele fără contract nu sunt „suspendate”)
    assert _si.zile_suspendate(2026, 6, "2026-06-16", None, susp) == 0


# ── înregistrarea suspendărilor, pe drumul REAL al rutei PUT /salariati/{id} (use-case-ul ei) ─────────────────────

class _FaraCommit:
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


@pytest.fixture
def ruta(conn, monkeypatch):
    import contextlib
    from core import uc_tenants, uc_comun
    proxy = _FaraCommit(conn)
    monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(proxy))
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda *a, **k: _SCHEMA)

    def put(cheie, suspendari):
        from main import SalariatEdit
        return uc_tenants.salariat_actualizeaza(1, _IDS[cheie], SalariatEdit(suspendari=suspendari), {"uid": 1})
    return put


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_ruta_inregistreaza_cfp_si_statul_il_aplica(conn, ruta):
    ruta("luna_intreaga", [{"data_inceput": "2026-06-08", "data_sfarsit": "2026-06-12", "tip": "cfp", "temei": "cerere 12/2026"}])
    stat = {r["cnp"]: r for r in stat_plata_api.stat_plata(conn, _SCHEMA, 2026, 6)}
    r = stat[_S["luna_intreaga"][0]]
    # Codul muncii art.49 alin.(2) + art.54: 5 zile de CFP din 21 -> 6000 x 16/21
    assert r["brut"] == 4571.43 and r["zile_active"] == 16
    assert r["suspendari"] == [{"data_inceput": "2026-06-08", "data_sfarsit": "2026-06-12", "tip": "cfp", "temei": "cerere 12/2026"}]
    ruta("luna_intreaga", [])          # ștergerea întregii liste readuce luna întreagă
    stat = {r["cnp"]: r for r in stat_plata_api.stat_plata(conn, _SCHEMA, 2026, 6)}
    assert stat[_S["luna_intreaga"][0]]["brut"] == 6000.0


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
@pytest.mark.parametrize("cheie,lista,cod", [
    ("luna_intreaga", [{"data_inceput": "2026-06-08", "data_sfarsit": "2026-06-12", "tip": "concediu"}], "tip_necunoscut"),
    ("luna_intreaga", [{"data_inceput": "2026-06-12", "data_sfarsit": "2026-06-08", "tip": "cfp"}], "interval_inversat"),
    ("luna_intreaga", [{"data_inceput": "2026-06-08", "data_sfarsit": "2026-06-12", "tip": "cfp"},
                       {"data_inceput": "2026-06-10", "data_sfarsit": "2026-06-15", "tip": "suspendare"}], "suprapunere"),
    # Codul muncii art.49: se suspendă un contract EXISTENT — nu înainte de angajare / după încetare
    ("angajat_16", [{"data_inceput": "2026-06-10", "data_sfarsit": "2026-06-18", "tip": "cfp"}], "inainte_de_angajare"),
    ("incetat_12", [{"data_inceput": "2026-06-10", "data_sfarsit": "2026-06-20", "tip": "cfp"}], "dupa_incetare"),
    ("luna_intreaga", [{"data_inceput": "", "data_sfarsit": "2026-06-12", "tip": "cfp"}], "data_lipsa"),
])
def test_ruta_refuza_suspendari_invalide_cu_motiv(conn, ruta, cheie, lista, cod):
    from core import erori, salariati_api
    # motivul, ca dată (`cod`), pe validarea pe care o cheamă ruta
    with pytest.raises(ValueError) as e:
        salariati_api.valideaza_suspendari(conn, _IDS[cheie], lista)
    assert e.value.cod == cod and e.value.erori_campuri[0]["camp"] == "suspendari"
    # ruta: același refuz, tradus în eroare de domeniu, și NIMIC scris
    with pytest.raises(erori.DateInvalide):
        ruta(cheie, lista)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM suspendari_contract WHERE salariat_id=%s", (_IDS[cheie],))
        assert cur.fetchone()[0] == (1 if cheie == "cfp_8_12" else 0), "un refuz nu scrie nimic"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_ruta_refuza_cfp_in_luna_inchisa(conn, ruta):
    from core import erori
    with conn.cursor() as cur:
        cur.execute("INSERT INTO perioade_blocate (an, luna, blocat_de) VALUES (2026, 6, 1)")
    with pytest.raises(erori.EroareDeDomeniu):
        ruta("luna_intreaga", [{"data_inceput": "2026-06-08", "data_sfarsit": "2026-06-12", "tip": "cfp"}])


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_ruta_refuza_cfp_suprapus_pe_concediu_medical(conn, ruta):
    """Aceeași zi nu poate fi și CM (plătit din FNUASS/angajator), și CFP — ar scădea de două ori din brut."""
    from core import erori
    with conn.cursor() as cur:
        cur.execute("INSERT INTO concedii_medicale (salariat_id, an, luna, zile, data_inceput, data_sfarsit) "
                    "VALUES (%s, 2026, 6, 3, '2026-06-10', '2026-06-12')", (_IDS["luna_intreaga"],))
    from core import salariati_api
    with pytest.raises(ValueError) as e:
        salariati_api.valideaza_suspendari(conn, _IDS["luna_intreaga"],
                                           [{"data_inceput": "2026-06-08", "data_sfarsit": "2026-06-12", "tip": "cfp"}])
    assert e.value.cod == "suprapunere_cm"
    with pytest.raises(erori.DateInvalide):
        ruta("luna_intreaga", [{"data_inceput": "2026-06-08", "data_sfarsit": "2026-06-12", "tip": "cfp"}])
