# -*- coding: utf-8 -*-
"""GARDA părții 3 din comanda Costin 06.10.2026 — salarii F5 SRL Salariati, octombrie 2026.

  11. „Netul de pe fluturaș nu se potrivește cu nota și cu D112: fluturașul folosește CAS/CASS/impozit nerotunjite (net
      6.810,24), iar nota/D112 sumele rotunjite la leu pe salariat (421 rămâne cu 6.809,45); CAM 259,77 pe cartele vs 260
      în notă. Netul și costul angajatorului de pe fluturaș trebuie să iasă din aceleași sume care merg în D112. Mesajul
      «coincide în limita de toleranță» nu are voie să acopere o diferență care lasă 421 nesoldat.”
  13. „Confirmă temeiul legal al rotunjirii bazei impozitului (Elena: 4.254,54 → 4.255 → 425,50).”

CNP-urile de test sunt verificate cu cifra de control (CLAUDE.md, algoritmul oficial).
"""
import datetime
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_lot0610_p3"
OCT = datetime.date(2026, 10, 1)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


# ── pct.13: temeiul rotunjirii bazei impozitului ─────────────────────────────────────────────────────────────────────────
def test_baza_impozitului_se_rotunjeste_la_leu_dupa_norme():
    """HG 1/2016 Norme Titlul IV pct.4 (aplicarea CF art.64): „bazele de calcul al impozitului vor fi stabilite prin
    rotunjire la un leu, prin neglijarea fracțiunilor de până la 50 de bani inclusiv sau prin majorarea la leu a
    fracțiunilor ce depășesc 50 de bani”. Elena (F5, 10/2026): 6.545,45 - 1.636,36 - 654,55 = 4.254,54 -> 4.255 -> 425,50.
    MUTAȚIE: baza rotunjită ROUND_HALF_UP -> fracțiunea de exact 0,50 urcă -> pică pe cazul de 0,50."""
    from core import salarizare as sz
    c = sz.calcul_salariu(6545.45, la_data=OCT)
    assert c["baza_impozabila"] == Decimal("4255.00")                       # HG 1/2016 Norme tit.IV pct.4: 0,54 > 0,50 -> +1
    # 0,50 exact se NEGLIJEAZĂ („până la 50 de bani inclusiv”): 10.010 - 2.502,50 - 1.001 = 6.506,50 -> 6.506
    c3 = sz.calcul_salariu(Decimal("10010.00"), la_data=OCT)
    assert c3["deducere"]["total"] == 0
    assert c3["baza_impozabila"] == Decimal("6506.00"), c3["baza_impozabila"]


# ── pct.11: aceleași sume ca D112 ───────────────────────────────────────────────────────────────────────────────────────
def test_retinerile_de_pe_fluturas_sunt_cele_declarate_in_d112():
    """Structura D112 (anaf_surse/structura_D112_0726_030826.txt): „Contributiile se rotunjesc aritmetic”. Rotunjirea se
    face o singură dată, pe valoarea nerotunjită, DUPĂ baza impozitului (care rămâne pe contribuțiile nerotunjite).
    MUTAȚIE: rotunjirea scoasă din calcul_salariu -> net 3.829,04 -> pică."""
    from core import salarizare as sz
    c = sz.calcul_salariu(6545.45, la_data=OCT)
    assert (c["cas"], c["cass"], c["impozit"]) == (Decimal("1636.00"), Decimal("655.00"), Decimal("426.00"))  # 1636,36 / 654,55 / 425,50
    assert c["net"] == Decimal("3828.45")                                    # 6545,45 - 1636 - 655 - 426
    assert c["cost_angajator"] == Decimal("6545.45") + c["cam"]


def test_statul_si_d112_rotunjesc_cu_aceeasi_regula():
    """`numere.leu_aritmetic` (statul) și `d112._d112int` (declarația) sunt două funcții — d112.py nu se atinge în lotul ăsta
    (condiția D1, decizia Costin 04.10.2026). Echivalența lor e garda ca regula să nu diveargă.
    MUTAȚIE: `leu_aritmetic` cu ROUND_HALF_EVEN -> 312,50 dă 312 la stat și 313 în D112 -> pică."""
    from core import d112
    from core.numere import leu_aritmetic
    for x in ("312.50", "312.49", "425.50", "0.50", "1636.36", "654.55", "1031.25", "937.5", "-2.5", "785.715"):
        assert int(leu_aritmetic(Decimal(x))) == d112._d112int(x), x


def test_cam_nu_se_datoreaza_pe_suma_neimpozabila_de_la_salariul_minim():
    """OUG 89/2025 art.III alin.(1): „Prin derogare de la … art. 220^4 alin. (1) … pentru suma de … 200 lei/lună … nu se
    datorează … contribuții sociale obligatorii” — baza CAM e baza contributivă, ca în D112 (`sum_bazac`).
    MUTAȚIE: cam = brut x cota (forma veche) -> 4.050 x 2,25% -> pică."""
    from core import salarizare as sz, common as c
    sm = Decimal(str(c.salariu_minim_luna(OCT)[0]))
    r = sz.calcul_salariu(sm, la_data=OCT, venit_brut_total=float(sm))
    assert r["facilitate"] > 0
    assert r["cam"] == ((sm - r["facilitate"]) * Decimal(str(c.cota("cam", OCT)[0]))).quantize(Decimal("0.01"))


def test_cam_declarat_se_imparte_pe_cartele_fara_rest():
    """D112 declară CAM pe TOTAL (cod 480 = ROUND(Σ bazac x 2,25%)); cartelele îl împart prin resturile cele mai mari.
    F5 10/2026: bazac 5.000 / 6.545 -> 112,50 / 147,2625 -> total 260 -> 113 / 147 (nu 259,77).
    MUTAȚIE: împărțirea scoasă (CAM cu bani pe salariat) -> Σ 259,77 -> pică."""
    from core import stat_plata_api as sp
    rand = lambda b: {"_bazac": b, "cam": 0.0, "cost": float(b)}
    stat = [rand(5000), rand(6545)]
    sp._imparte_cam(stat, OCT)
    assert [r["cam"] for r in stat] == [113.0, 147.0]
    assert [r["cost"] for r in stat] == [5113.0, 6692.0]
    stat = [rand(4000), rand(4000), rand(4000)]          # 90 x 3 = 270, fără rest
    sp._imparte_cam(stat, OCT)
    assert sum(r["cam"] for r in stat) == 270.0 and all("_bazac" not in r for r in stat)


def test_421_se_compara_la_ban_fara_toleranta():
    """„Mesajul «coincide în limita de toleranță» nu are voie să acopere o diferență care lasă 421 nesoldat.”
    MUTAȚIE: control_421 cu toleranța lui D112 (0,5 lei/salariat) -> diferența de 0,79 trece -> pică."""
    from core import salarii_contare as sc
    D = Decimal
    note = [("641", "421", D("11545.45")), ("421", "4315", D("2886")), ("421", "4316", D("1155")), ("421", "444", D("695"))]
    assert sc.sold_421(note) == D("6809.45")
    assert sc.control_421(note, D("6809.45")) is None
    d = sc.control_421(note, D("6810.24"))           # netul vechi de pe fluturaș
    assert d and d["cont"] == "421" and d["diferenta"] == 0.79 and d["toleranta"] == 0.0 and d["fata_de"] == "netul fluturașilor"


# ── cap-coadă pe schemă efemeră ─────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET search_path TO %s, public" % SCH)
            cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,platitor_tva,tip_decont,declarant_nume,"
                        "declarant_prenume,declarant_functie,patron_nume) VALUES (1,'ZT Salarii SRL','14399840','Str 1','Buc',"
                        "'B','6202',true,'L','Pop','Ion','administrator','Pop Ion')")
            for cnp, nume, brut in (("1800101410013", "IONESCU", 5000), ("2850101410016", "POPESCU", Decimal("6545.45"))):
                cur.execute("WITH s AS (INSERT INTO salariati (cnp,nume,prenume,data_angajare,ore_zi,judet_casa,cor,data_nastere,"
                            "tip_asigurat,functie_baza) VALUES (%s,%s,'X','2024-01-01',8,'B','251401','1980-01-01','1',true) "
                            "RETURNING id, data_angajare) INSERT INTO salariu_istoric (salariat_id, valabil_din, salariu_brut) "
                            "SELECT id, data_angajare, %s FROM s", (cnp, nume, brut))
        c.commit()
    with _db.get_conn(SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def test_fluturasul_nota_si_d112_dau_aceleasi_sume(conn):
    """Cap-coadă: Σ netul fluturașilor = soldul 421 după notă (la ban), Σ CAM de pe cartele = codul 480, propunerea fără
    divergențe. MUTAȚIE: rotunjirea scoasă din calcul_salariu -> propunerea arată divergența pe 421 -> pică."""
    from core import d112, salarii_contare as sc, stat_plata_api as sp
    st = sp.stat_plata(conn, SCH, 2026, 10)
    p = sc.propunere(conn, SCH, 2026, 10)
    obl = d112.obligatii(conn, SCH, 2026, 10)
    note = [(n["debit"], n["credit"], Decimal(str(n["suma"]))) for n in p["note"]]
    assert sc.sold_421(note) == Decimal(str(p["net_fluturasi"])) == sum(Decimal(str(r["net"])) for r in st)
    assert sum(r["cam"] for r in st) == obl["480"]
    assert p["divergente"] == [], p["divergente"]
    pop = next(r for r in st if r["nume"].startswith("POPESCU"))
    assert (pop["cas"], pop["cass"], pop["impozit"], pop["net"]) == (1636.0, 655.0, 426.0, 3828.45)
