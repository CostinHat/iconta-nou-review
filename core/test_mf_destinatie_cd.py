# -*- coding: utf-8 -*-
"""GARD — amortizarea accelerată a aparaturii de cercetare-dezvoltare din orice cont (lot 19, defectul 11, 03.10.2026).

CF art.20 alin.(1) lit.b): „aplicarea metodei de amortizare accelerată și în cazul aparaturii și echipamentelor destinate
activităților de cercetare-dezvoltare”; art.20^1 alin.(8): se aplică și la opțiunea pentru creditul fiscal. Înainte,
accelerata se permitea doar pe 2131; un echipament C&D pe 2132/2133/214 era refuzat. Decizia lui Costin: coloana
`mijloace_fixe.destinatie_cd` + bifă (registru, plus la inventar, import).
"""
import io
import os
import re
from datetime import date

import pytest

from core import d406_active as m
from core.mijloace_fixe_import_api import extrage

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _mf(cont, cd, metoda="accelerata"):
    return {"cod": "MF1", "valoare": 60000, "rezidual": 0, "dnf_luni": 60, "data_pif": date(2025, 3, 10),
            "metoda": metoda, "cont_imobilizare": cont, "destinatie_cd": cd}


def test_aparatura_cd_pe_2132_poate_fi_accelerata():
    # CF art.20 alin.(1) lit.b): accelerata „și în cazul aparaturii și echipamentelor destinate activităților de C&D”
    acc = m.amortizare_luna(_mf("2132", True), 2025, 4)
    lin = m.amortizare_luna(_mf("2132", True, "liniara"), 2025, 4)
    assert acc > lin


def test_fara_bifa_accelerata_ramane_refuzata_pe_2132():
    # CF art.28 alin.(5) lit.c): „oricărui altui mijloc fix amortizabil” — liniară sau degresivă
    with pytest.raises(ValueError, match="nu e permisă de lege"):
        m.amortizare_luna(_mf("2132", False), 2025, 4)


@pytest.mark.parametrize("cont", ["212", "2134", "211"])
def test_bifa_nu_deschide_constructii_animale_terenuri(cont):
    # art.20 alin.(1) lit.b) vorbește de „aparatură și echipamente”, nu de construcții, animale/plantații sau terenuri
    with pytest.raises(ValueError):
        m.amortizare_luna(_mf(cont, True), 2025, 4)


def test_cititorii_registrului_aduc_bifa():
    """Orice SELECT care aduce `metoda` din mijloace_fixe aduce și `destinatie_cd` — altfel motorul ar refuza accelerata
    într-un loc (nota lunară, D406, casare, reevaluare) și ar permite-o în altul."""
    rele = []
    for rad, _d, fis in os.walk(os.path.join(RAD, "core")):
        for f in fis:
            if not f.endswith(".py") or f.startswith("test_"):
                continue
            t = io.open(os.path.join(rad, f), encoding="utf-8").read()
            for q in re.findall(r"SELECT(?:(?!SELECT).){0,700}?FROM\s+\S*mijloace_fixe", t, re.S):
                if re.search(r"\bmetoda\b", q) and "destinatie_cd" not in q:
                    rele.append("%s: %s" % (f, " ".join(q.split())[:120]))
    assert rele == [], rele


def test_template_si_migrarea_au_coloana():
    """Pe BAZĂ, nu pe text: o schemă din template are coloana (boolean, NOT NULL, implicit false), iar migrarea e
    idempotentă pe ea."""
    from core import db as _db, tenant_provisioning as _tp, migrare_destinatie_cd as mig
    try:
        _db.init_pool()
    except Exception:
        pytest.skip("DB indisponibil")
    sch = "test_mf_destinatie_cd"
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % sch)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"),
                                                                encoding="utf-8").read(), sch))
                mig.aplica(c, sch)                          # idempotent: a doua oară nu strică nimic
                cur.execute("SELECT data_type, is_nullable, column_default FROM information_schema.columns "
                            "WHERE table_schema=%s AND table_name='mijloace_fixe' AND column_name='destinatie_cd'", (sch,))
                assert cur.fetchone() == ("boolean", "NO", "false")
        finally:
            c.rollback()


def test_importul_citeste_coloana_cd():
    r = extrage(b"cod;denumire;valoare;durata;pif;metoda;cont imobilizare;cercetare\n"
                b"MF1;Spectrometru;60000;60;2025-03-10;accelerata;2132;da\n"
                b"MF2;Laptop;6000;36;2025-03-10;liniara;2132;poate\n", "m.csv")
    assert r[0]["destinatie_cd"] is True and r[0]["amortizat"] is not None   # accelerata calculata, nu refuzata
    assert r[1]["destinatie_cd"] is False and any("C&D" in a for a in r[1]["avertismente"])
