# -*- coding: utf-8 -*-
"""GARD S1 (retest Costin 07.10 seara, pct.1) — elementele variabile ale salariului: prime, sporuri, ore suplimentare.

Comanda: „Adaugă prime, sporuri și ore suplimentare, pe salariat și pe lună. Intră în brut și în bazele CAS / CASS / impozit și
apar distinct în fluturaș și în compoziția netului. Valori introduse de contabil, fără preselecție.”

Valorile 2026 (S1: salariul minim 4.050, facilitatea 300, plafonul 4.300) se citesc din `common` și se verifică aici o dată,
la sursă: OUG 89/2025 art.III alin.(1) („suma de 300 lei/lună … 1 ianuarie-30 iunie 2026”; lit.b „nu depășește nivelul de 4.300
lei inclusiv în perioada … 1 ianuarie 2026-30 iunie 2026”).
"""
import io
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tp
from core.common import Perioada

SCH = "efemer_s1_elemente"
IUN = __import__("datetime").date(2026, 6, 1)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


# ── calculul ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_valorile_2026_s1_sunt_cele_din_oug_89_2025():
    from core import common as c
    assert (c.salariu_minim_luna(IUN)[0], c.cota("facilitate_salariu_minim", IUN)[0],
            c.cota("plafon_facilitate_salariu_minim", IUN)[0]) == (4050, 300, 4300)   # OUG 89/2025 art.III alin.(1) + lit.b


@pytest.mark.parametrize("prorata", [None, 1.0])   # ambele ramuri ale facilității (forma clasică și cea din salariu_istoric)
def test_prima_intra_in_brut_in_baze_si_in_venitul_realizat_al_facilitatii(prorata):
    """CF art.76 alin.(1): „toate veniturile în bani … indiferent de … denumirea veniturilor” -> prima e venit din salarii.
    OUG 89/2025 art.III alin.(1) lit.b: venitul brut REALIZAT ≤ 4.300 -> la 4.050 + 500 = 4.550 facilitatea cade.
    MUTAȚIE: `sub_plafon` scos de pe ramura `facilitate_prorata` -> facilitatea 300 rămâne -> pică."""
    from core import salarizare as sz
    k = dict(la_data=IUN, venit_brut_total=4050, facilitate_prorata=prorata)
    fara = sz.calcul_salariu(4050, **k)
    cu = sz.calcul_salariu(4050, elemente_variabile=500, **k)
    sub = sz.calcul_salariu(4050, elemente_variabile=200, **k)
    assert fara["facilitate"] == Decimal("300.00")
    assert (cu["brut"], cu["elemente_variabile"], cu["facilitate"]) == (Decimal("4550.00"), Decimal("500.00"), Decimal("0.00"))
    assert cu["cas"] == Decimal("1138.00")             # 4.550 × 25% = 1.137,50 -> 1.138 (rotunjire aritmetică, D112)
    assert cu["cass"] == Decimal("455.00")             # 4.550 × 10%
    assert cu["net"] == Decimal("4550.00") - cu["cas"] - cu["cass"] - cu["impozit"]   # prima se plătește în bani
    assert (sub["brut"], sub["facilitate"]) == (Decimal("4250.00"), Decimal("300.00"))   # 4.250 ≤ 4.300: rămâne
    assert sub["cas"] == Decimal("988.00")             # (4.250 − 300) × 25% = 987,50 -> 988


def test_indemnizatia_cm_intra_in_venitul_realizat_al_facilitatii():
    """CF art.76 alin.(1): „… inclusiv indemnizațiile pentru incapacitate temporară de muncă” -> 3.000 lucrat + 1.400 CM =
    4.400 > 4.300: fără facilitate. MUTAȚIE: `venit_cm` scos din `venit_realizat` -> 300 -> pică."""
    from core import salarizare as sz
    r = sz.calcul_salariu(3000, la_data=IUN, venit_brut_total=4050, facilitate_prorata=1.0, venit_cm=1400)
    assert r["facilitate"] == Decimal("0.00")
    assert sz.calcul_salariu(3000, la_data=IUN, venit_brut_total=4050, facilitate_prorata=1.0, venit_cm=1000)["facilitate"] \
        == Decimal("300.00")


def test_elementul_se_cere_complet_fara_preselectie():
    """„Valori introduse de contabil, fără preselecție.” MUTAȚIE: tipul implicit „prima” -> pică."""
    from core import elemente_salariale as es
    _, er = es.valideaza({"denumire": "x", "suma": 10})
    assert [e["camp"] for e in er] == ["tip"]
    _, er = es.valideaza({"tip": "ore_suplimentare", "denumire": "ore", "suma": 10})
    assert [e["camp"] for e in er] == ["ore"]
    _, er = es.valideaza({"tip": "prima", "denumire": " ", "suma": 0, "ore": 3})
    assert sorted(e["camp"] for e in er) == ["denumire", "ore", "suma"]


# ── cap-coadă: statul, D112, nota ────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET search_path TO %s, public" % SCH)
            cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,regim_fiscal,platitor_tva,"
                        "tip_decont,declarant_nume,declarant_prenume,declarant_functie) VALUES (1,'PROBA S1 SRL','14399840',"
                        "'Str 1','Buc','B','6202','BCR','RO49RNCB0000000000000001','profit',true,'L','Pop','Ion','administrator')")
            cur.execute("WITH s AS (INSERT INTO salariati (cnp,nume,prenume,data_angajare,ore_zi,judet_casa,functie_baza,"
                        "scutit_contrib_minim) VALUES ('1900101410011','POP','ION','2024-01-01',8,'B',true,false) "
                        "RETURNING id, data_angajare), i AS (INSERT INTO salariu_istoric (salariat_id, valabil_din, "
                        "salariu_brut) SELECT id, data_angajare, 5000 FROM s) SELECT id FROM s")
        c.commit()
    try:
        with _db.get_conn(SCH) as c:
            try:
                yield c
            finally:
                c.rollback()
    finally:
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            c.commit()


def _asigurat_b1(xml):
    """Atributele elementului `asiguratB1` din D112 — citite din XML-ul parsat, nu căutate ca șir."""
    import xml.etree.ElementTree as ET
    noduri = [e for e in ET.fromstring(xml.encode("utf-8")).iter() if e.tag.split("}")[-1] == "asiguratB1"]
    assert len(noduri) == 1, len(noduri)
    return noduri[0].attrib


def _sid(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM salariati")
        return cur.fetchone()[0]


def test_prima_ajunge_in_stat_d112_si_nota_la_fel_si_d112_e_valid(conn):
    """Aceeași primă (500,50 — zecimale, ca rotunjirea să fie exercitată) în statul de plată, în D112 (B1_sal2 = venitul REALIZAT)
    și în nota de salarii (641 = 421), cu aceleași contribuții; D112 trece validatorul oficial. MUTAȚIE: `_venituri_adaugate`
    fără elementele variabile -> B1_sal2 rămâne 5.000 -> pică."""
    from core import elemente_salariale as es, stat_plata_api as sp, d112, salarii_contare as sc, duk
    sid = _sid(conn)
    assert es.adauga(conn, SCH, sid, 2026, 6, {"tip": "prima", "denumire": "prima de performanță", "suma": "500.50"})["ok"]
    assert es.adauga(conn, SCH, sid, 2026, 6, {"tip": "ore_suplimentare", "denumire": "ore lucrate sâmbătă", "ore": 10,
                                               "suma": 450})["ok"]
    rand = next(x for x in sp.stat_plata(conn, SCH, 2026, 6) if x["id"] == sid)
    assert (rand["brut"], rand["brut_baza_lucrat"], rand["elemente_variabile"]) == (5950.5, 5000.0, 950.5)
    assert [e["denumire"] for e in rand["elemente"]] == ["prima de performanță", "ore lucrate sâmbătă"]
    comp = [(c["eticheta"], c["valoare"]) for c in sp.compozitie_fluturas(rand) if c["fel"] == sp.FEL_DETALIU]
    assert comp == [("  din care salariul de bază (zilele lucrate)", 5000.0), ("  din care Primă — prima de performanță", 500.5),
                    ("  din care Ore suplimentare — ore lucrate sâmbătă (10 ore)", 450.0)]
    _p, sal = d112.pull(conn, SCH, Perioada(an=2026, luna=6))
    s = next(x for x in sal if x["id"] == sid)
    assert (float(s["cas"]), float(s["cass"]), float(s["impozit"])) == (rand["cas"], rand["cass"], rand["impozit"])
    xml, _r = d112.genereaza(conn, SCH, Perioada(an=2026, luna=6))
    b1 = _asigurat_b1(xml)
    assert (b1["B1_sal2"], b1["B1_sal1"]) == ("5951", "5000")       # realizat (cu prima) / contractual (fără)
    if duk.poate_valida("d112"):
        rez = duk.valideaza(xml, "d112", an=2026, luna=6)
        assert rez["stare"] == "valid", rez
    note = dict(((n[0], n[1]), n[2]) for n in sc.note_lunare(conn, SCH, 2026, 6, xml)[0])
    assert note[("641", "421")] == Decimal("5950.50")


def test_luna_cu_d112_depusa_nu_mai_primeste_elemente(conn):
    """Ca pontajul: după D112 depusă, corecția e prin rectificativă. Tenant SINTETIC, anul 2099, tranzacție anulată (tabel partajat).
    MUTAȚIE: verificarea `_d112_depusa` scoasă din `adauga` -> pică."""
    from core import elemente_salariale as es
    sid = _sid(conn)
    with conn.cursor() as cur:
        # fixtura-sintetica-ok: tenant_id sintetic (nu coliziune PK cu depunere reala)
        cur.execute("INSERT INTO public.declaratii_depuse (tenant_id,an,luna,tip,data_depunere,sursa,nr_depunere) "
                    "VALUES (99999,2099,8,'d112',now(),'test',1)")
    r = es.adauga(conn, SCH, sid, 2099, 8, {"tip": "spor", "denumire": "spor noapte", "suma": 100}, tenant_id=99999)
    assert (r["ok"], r["cod"]) == (False, "D112_DEPUSA")


def test_la_salariul_minim_prima_peste_plafon_anuleaza_facilitatea_pe_ambele_cai(conn):
    """4.050 (minimul) + 500 primă = 4.550 > 4.300: fără facilitate — generatorul (calcul_salariu) și calea a doua
    (`d112_reconciliere`, recalcul independent) trebuie să spună la fel, altfel D112 nu se generează. MUTAȚIE: lit.b scoasă
    din calea a doua (`baza = sm - fac_val`) -> divergență -> pică."""
    from core import elemente_salariale as es, d112
    sid = _sid(conn)
    with conn.cursor() as cur:
        cur.execute("UPDATE salariu_istoric SET salariu_brut = 4050 WHERE salariat_id = %s", (sid,))
    assert es.adauga(conn, SCH, sid, 2026, 6, {"tip": "prima", "denumire": "prima trimestrială", "suma": 500})["ok"]
    xml, _r = d112.genereaza(conn, SCH, Perioada(an=2026, luna=6))
    _p, sal = d112.pull(conn, SCH, Perioada(an=2026, luna=6))
    s = next(x for x in sal if x["id"] == sid)
    assert (float(s["facilitate"]), float(s["cas"])) == (0.0, 1138.0)     # (4.050 + 500) × 25% = 1.137,50 -> 1.138
    assert _asigurat_b1(xml)["B1_sal2"] == "4550"
