# -*- coding: utf-8 -*-
"""D406 la firma NEplătitoare de TVA — deficiențele C1 și C2 (foste 225, 226), găsite pe 10.10.2026 de amprentele „înainte” ale registrului fiscal
(R2, `scripts/amprente_declaratii.py`): pe producție, F5 (neplătitoare, fereastra SAF-T T4/2026) primea D406 pe luni.

Temei: OPANAF 1783/2021 anexa 4 pct.3 — „Contribuabilii care nu sunt înregistraţi în scopuri de TVA transmit Declaraţia informativă
D406 trimestrial”; `d406_schema_anaf.xlsx` S.SC.5/S.SC.7 — „Prima / Ultima perioadă contabilă acoperită de SAF”, GL.10 `Period` —
„Perioada contabilă” (a tranzacției). Firma e nouă, a rulării; notele contabile sunt validate pe drumul aplicației (ruta jurnalului).
"""
import datetime as _dt
import re

import pytest

from conftest import alege_perioada, alege_tipul, firma_noua, sql
from e2e_bloc_d import PATRON, _date_firma, _deschide, _nota_validata

AZI = _dt.date.today()
_T_CURENT = (AZI.month - 1) // 3
AN_T, TRIM = (AZI.year, _T_CURENT) if _T_CURENT else (AZI.year - 1, 4)      # trimestrul trecut
LUNI = [3 * (TRIM - 1) + k for k in (1, 2, 3)]


@pytest.fixture(scope="module")
def firma_neplatitoare():
    """Firmă nouă, neplătitoare de TVA (vectorul fiscal pe drumul ecranului), cu Date firmă completate și câte o notă validată în fiecare
    lună a trimestrului trecut (581 = 5311, 100 / 200 / 300 lei), din numerarul adus înaintea trimestrului (5311 = 1012, 600 lei)."""
    from core import db, vector_fiscal_api as vf
    gen = firma_noua()
    f = next(gen)
    uid = sql("SELECT id FROM public.users WHERE email = %s", (PATRON,))[0][0]
    _date_firma(f)
    with db.get_conn(f["schema"]) as c:
        r = vf.salveaza(c, "micro", False, None, False, inreg_art317=False, user_id=uid)
        assert r.get("ok", True) is not False, r
        c.commit()
    assert sql('SELECT platitor_tva FROM "%s".firma_profil WHERE id = 1' % f["schema"]) == [(False,)]
    # [406] casa nu ajunge sub zero: numerarul depus există întâi în casă — aportul, în ziua dinaintea trimestrului (în afara D406-ului lui)
    _nota_validata(f, (_dt.date(AN_T, LUNI[0], 1) - _dt.timedelta(days=1)).isoformat(), "5311", "1012", 600, "Aport numerar D225")
    for k, luna in enumerate(LUNI, 1):
        _nota_validata(f, _dt.date(AN_T, luna, 10 + k).isoformat(), "581", "5311", 100 * k, "Depunere numerar D225 %d" % k)
    yield f
    try:
        next(gen)
    except StopIteration:
        pass


def _alege_d406(ecran, f):
    pg = ecran.pg
    ecran.firma(f["nume"])
    _deschide(ecran, "#fa-declaratii", "Pasul 1 din 3")
    alege_tipul(pg, "d406", zona=".fereastra:last-of-type ")
    alege_perioada(pg, AN_T, zona=".fereastra:last-of-type ")
    pg.wait_for_timeout(300)


def test_def_c2_neplatitorul_alege_d406_pe_trimestru(patron, firma_neplatitoare):
    """C2. Declarații, firmă neplătitoare: D406 se oferea pe LUNĂ, deși neplătitorul îl depune trimestrial (OPANAF 1783/2021 anexa 4
    pct.3) și fișierul generat acoperă oricum trimestrul.
    Pașii contabilului: firma neplătitoare -> Declarații -> D406: tipul se arată „D406 · trimestrial”, perioada se alege pe trimestru
    (nu pe lună) -> trimestrul trecut se poate genera."""
    pg = patron.pg
    _alege_d406(patron, firma_neplatitoare)
    eticheta = pg.evaluate("() => [...document.querySelectorAll('.fereastra:last-of-type #dec-tip option')]"
                           ".map((o) => o.innerText).find((t) => t.startsWith('D406'))")
    patron.captura("d406_neplatitor_selector")
    # [283] „De depus” vine întâi și numește perioada scadentă („D406 · T3/2026 · termen …”); în „Alte declarații” scrie „trimestrial”
    assert eticheta and re.search(r"trimestrial|· T[1-4]/\d{4}", eticheta), eticheta
    assert pg.locator(".fereastra:last-of-type #dec-trim").count() == 1, patron.fereastra()[:1500]
    assert pg.locator(".fereastra:last-of-type #dec-luna").count() == 0, "D406 se alege pe lună la neplătitor"


def test_def_c1_fiecare_tranzactie_in_luna_ei(patron, firma_neplatitoare):
    """C1. D406 trimestrial: fiecare tranzacție purta luna CERUTĂ ca perioadă contabilă (nota din 28.11 pe T4 declarată în perioada 12),
    deși antetul aceluiași fișier spune perioadele 10–12.
    Pașii contabilului: firma neplătitoare, câte o notă validată în fiecare lună a trimestrului trecut -> Declarații -> D406 pe trimestrul
    acela -> „Vezi XML-ul generat”: antetul acoperă lunile trimestrului, iar fiecare tranzacție are perioada lunii ei."""
    pg = patron.pg
    _alege_d406(patron, firma_neplatitoare)
    alege_perioada(pg, AN_T, trim=TRIM, zona=".fereastra:last-of-type ")
    pg.click(".fereastra:last-of-type #dec-continua")
    pg.wait_for_selector(".fereastra:last-of-type details.dec-xml summary:text('Vezi XML-ul generat')", timeout=90000)
    pg.click(".fereastra:last-of-type details.dec-xml summary:text('Vezi XML-ul generat')")
    xml = pg.locator(".fereastra:last-of-type details.dec-xml:has(summary:text('Vezi XML-ul generat')) pre").text_content()
    patron.captura("d406_neplatitor_xml")
    assert re.search(r"<PeriodStart>%d</PeriodStart>" % LUNI[0], xml) and re.search(r"<PeriodEnd>%d</PeriodEnd>" % LUNI[2], xml), xml[:3000]
    tranz = re.findall(r"<Transaction>\s*<TransactionID>[^<]*</TransactionID>\s*<Period>(\d+)</Period>\s*<PeriodYear>(\d+)</PeriodYear>"
                       r"\s*<TransactionDate>(\d{4})-(\d{2})-\d{2}</TransactionDate>", xml)
    assert len(tranz) == 3, tranz
    assert sorted(int(p) for p, _a, _y, _m in tranz) == LUNI, tranz
    assert all(int(p) == int(m) and a == y for p, a, y, m in tranz), tranz
