# -*- coding: utf-8 -*-
"""Lotul 10, comanda 10.2 pct.8d — mesajele motorului de stoc, în cuvintele contabilului.

Comanda, verbatim: „La ieșirea peste stoc mesajul e «iesire 1000 peste stocul 139.000»: fără diacritice, iar «139.000» se citește 139
de mii. Corect: «Ieșire de 1.000 buc peste stocul de 139 buc».” Clasa: toate mesajele motorului de stoc care ajung la contabil, cu
cantitatea formatată românește (`pdf_util.cantitate`, oglinda lui `cantitate()` din api.js) și cu unitatea de măsură — fișa de magazie
(`stocuri_cv.fisa_magazie`), ieșirea nouă (`valoare_iesire`), ieșirea pe articol (`stocuri_cv_api.iesire`), consumul pe rețetă
(`retete_api.descarca`), transferul între locații (`stocuri_cv_api.transfer`).

Gardul de clasă (`test_motorul_de_stoc_nu_mai_are_mesaje_fara_diacritice_sau_cu_cantitatea_bruta`) citește sursa motorului: un
`ValueError` cu o cantitate pusă direct în f-string (`{c}`, `{cant}`) sau cu „iesire” fără diacritice pică.
"""
import io
import re
from decimal import Decimal
from pathlib import Path

import pytest

from core import db as _db
from core import stocuri_cv as m
from core import tenant_provisioning as _tp

RAD = Path(__file__).resolve().parent.parent


def I(c, p, d="2099-10-01"):
    return {"tip": "intrare", "cantitate": c, "pret_unitar": p, "data": d}


def E(c, d="2099-10-20"):
    return {"tip": "iesire", "cantitate": c, "data": d}


def test_def_zstoc_iesirea_noua_peste_stoc_cu_cantitate_romaneasca_si_um():
    """MUTAȚIE: `_c` întoarce `str(x)` (fără `pdf_util.cantitate`) -> „1000 peste stocul de 139.000” -> pică."""
    with pytest.raises(ValueError) as e:
        m.valoare_iesire([I(Decimal("139.000"), 2)], None, 1000, "buc")
    # textul cerut de comandă, verbatim: „Ieșire de 1.000 buc peste stocul de 139 buc”
    assert str(e.value) == "Ieșire de 1.000 buc peste stocul de 139 buc"


def test_def_zstoc_fisa_peste_stoc_numeste_si_data():
    with pytest.raises(ValueError) as e:
        m.fisa_magazie([I(Decimal("1.500"), 4), E(Decimal("2.250"))], None, "kg")
    assert str(e.value) == "Ieșire de 2,25 kg peste stocul de 1,5 kg la 20.10.2099"   # DS cap.4: data dd.mm.yyyy


def test_def_zstoc_celelalte_refuzuri_ale_motorului_in_cuvintele_contabilului():
    with pytest.raises(ValueError) as e:                                   # cantitate zero la o intrare
        m.fisa_magazie([I(0, 5)], None, "buc")
    assert str(e.value) == "Cantitatea mișcării de stoc trebuie să fie mai mare ca zero (are 0 buc la 01.10.2099)"
    with pytest.raises(ValueError) as e:                                   # stornarea unei intrări a cărei marfă a ieșit
        m.fisa_magazie([dict(I(10, 1), id=1), E(8), {"tip": "intrare", "cantitate": -10, "valoare": "-10", "anuleaza_id": 1,
                                                     "data": "2099-10-21"}], None, "buc")
    assert str(e.value) == "Stornarea intrării de 10 buc peste stocul de 2 buc la 21.10.2099"
    with pytest.raises(ValueError) as e:
        m.valoare_iesire([I(3, 1)], None, 0, "buc")
    assert str(e.value) == "Cantitatea ieșirii trebuie să fie mai mare ca zero (are 0 buc)"
    with pytest.raises(ValueError) as e:
        m.fisa_magazie([{"tip": "ajustare", "cantitate": 0, "valoare": 5, "data": "2099-10-02"}], None, "buc")
    assert str(e.value) == "Ajustarea de valoare nu are pe ce stoc să se aplice: stocul e zero la 02.10.2099"


def test_motorul_de_stoc_nu_mai_are_mesaje_fara_diacritice_sau_cu_cantitatea_bruta():
    """GARD de clasă: în sursa motorului și a apelanților lui care refuză (ieșire, rețetă, transfer), niciun refuz nu pune o cantitate
    direct în text (`{c}`, `{cant}`, `{disp}`) și niciunul nu scrie „iesire”/„reteta” fără diacritice. MUTAȚIE: mesajul vechi
    `f"iesire {c} peste stocul {cant}"` pus înapoi în `stocuri_cv.py` -> pică."""
    rau = []
    for f in ("core/stocuri_cv.py", "core/stocuri_cv_api.py", "core/retete_api.py"):
        for nr, linie in enumerate((RAD / f).read_text(encoding="utf-8").splitlines(), 1):
            if not re.search(r'(raise ValueError|"eroare":)', linie):
                continue
            if re.search(r"\{(c|cant|disp|-c|cantitate)\}", linie) or re.search(r'["\'](iesire|reteta|stoc insuficient)\b', linie):
                rau.append("%s:%d %s" % (f, nr, linie.strip()))
    assert not rau, "refuzuri ale motorului de stoc cu cantitatea brută sau fără diacritice:\n" + "\n".join(rau)


# ── pe drumul aplicației (bază de test, schemă efemeră, ROLLBACK) ─────────────────────────────────────────────────────────
SCH = "efemer_lot10b_stoc"


@pytest.fixture()
def tx():
    try:
        _db.init_pool()
        p = _db.pool()
        conn = p.getconn()
    except Exception:
        pytest.skip("DB indisponibil")
    cur = conn.cursor()
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
    cur.execute(_tp.parametrizeaza_template(io.open(RAD / "tenant_template.sql", encoding="utf-8").read(), SCH))
    cur.execute("INSERT INTO %s.firma_profil (id, nume, cui, metoda_stoc) VALUES (1, 'STOC LOT10 SRL', '14399840', 'cantitativ_valoric')"
                % SCH)
    cur.execute('SET LOCAL search_path TO "%s", public' % SCH)
    try:
        yield conn, cur
    finally:
        conn.rollback()  # SET LOCAL de mai sus moare odată cu tranzacția: conexiunea se întoarce în pool fără search_path
        p.putconn(conn)


def test_def_zstoc_iesirea_pe_articol_refuza_cu_unitatea_articolului(tx):
    """Pe drumul aplicației (`stocuri_cv_api.iesire`, chemat de „Ieșire pe articol” de pe ecranul Raport Z). MUTAȚIE: `a["um"]` scos
    din apelul `valoare_iesire` -> „Ieșire de 1.000 peste stocul de 139” -> pică."""
    from core import stocuri_cv_api as cva
    conn, cur = tx
    r = cva.intrare(conn, SCH, {"denumire": "Marfa A", "um": "buc", "data": "2099-10-01", "cantitate": 139, "pret_unitar": 2,
                                "document": "Inventar inițial probă"})
    out = cva.iesire(conn, SCH, {"articol_id": r["articol_id"], "data": "2099-10-20", "cantitate": 1000})
    assert out == {"eroare": "Ieșire de 1.000 buc peste stocul de 139 buc"}, out
    t = cva.transfer(conn, SCH, {"articol_id": r["articol_id"], "din_locatie": None, "in_locatie": "Depozit 2", "cantitate": 1000,
                                 "data": "2099-10-20"})
    assert t == {"eroare": "Transfer de 1.000 buc peste stocul de 139 buc din locația sursă"}, t


def test_def_zstoc_reteta_refuza_cu_articolul_si_unitatea(tx):
    from core import retete_api as ra, stocuri_cv_api as cva
    conn, cur = tx
    r = cva.intrare(conn, SCH, {"denumire": "Faina", "um": "kg", "data": "2099-10-01", "cantitate": 1, "pret_unitar": 3,
                                "document": "Inventar inițial probă"})
    cur.execute("INSERT INTO retete (denumire) VALUES ('Clatite') RETURNING id")
    rid = cur.fetchone()[0]
    cur.execute("INSERT INTO retete_linii (reteta_id, articol_id, cantitate) VALUES (%s, %s, 0.5)", (rid, r["articol_id"]))
    with pytest.raises(ValueError) as e:
        ra.descarca(conn, SCH, {"reteta_id": rid, "portii": 3, "data": "2099-10-20"})
    assert str(e.value) == "Stoc insuficient la Faina. Ieșire de 1,5 kg peste stocul de 1 kg la 20.10.2099", e.value
