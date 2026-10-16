# -*- coding: utf-8 -*-
"""288 — Povestea lunii (comanda Costin 16.10.2026, a doua completare la lotul 6, verbatim în DECIZII): (a) „Povestea folosește termenii
corect (venituri ≠ încasări, profit/pierdere) și se verifică automat înainte de aprobare.” (b) „Lămurești dacă sunt cifrele lunii sau
cumulate și o spui explicit în pachet și în text.” (c) „Informațiile despre restanțele cabinetului nu intră în povestea trimisă clientului
fără decizia expresă a contabilului.” Temei: N/A — produs (textul către client)."""
import pytest

from core import pachete_api as pa

RZ = {"venituri": 1000.0, "cheltuieli": 14713.0, "rezultat": -13713.0, "tip": "pierdere", "luna_nume": "septembrie"}


def test_288a_termenii_si_perioada_se_verifica():
    """MUTAȚIE: verificarea lunii scoasă din `abateri_termeni` -> textul fără lună trece -> pică."""
    assert pa.abateri_termeni("În septembrie firma a avut venituri de 1.000,00 lei.", RZ) == []
    assert pa.abateri_termeni("În septembrie firma a avut încasări de 1.000,00 lei.", RZ).count("termen: încasări") == 1
    assert any(a.startswith("perioadă: textul nu spune luna") for a in pa.abateri_termeni("Firma a avut venituri de 1.000,00 lei.", RZ))
    assert any(a.startswith("perioadă: cifrele pachetului sunt ale lunii")
               for a in pa.abateri_termeni("În septembrie, cumulat de la începutul anului, veniturile sunt 1.000,00 lei.", RZ))
    assert pa.perioada_cifrelor(2026, 9) == "luna septembrie 2026 (numai luna, nu cumulat de la 1 ianuarie)"


def test_288_aprobarea_verifica_textul_si_cere_decizia_pentru_restante(monkeypatch):
    """MUTAȚIE: verificarea scoasă din `pachet_poveste_aproba` -> „încasări” se aprobă -> pică."""
    import contextlib
    from core import uc_pachete as up, erori
    monkeypatch.setattr(up._uc_comun, "_cere_perioada", lambda an, luna: None)
    monkeypatch.setattr(up._uc_comun, "_pachet_schema", lambda ctx, tid: "x")
    monkeypatch.setattr(up.db, "get_conn", lambda schema=None: contextlib.nullcontext(None))
    monkeypatch.setattr(up._pachete, "rezumat_luna", lambda cs, cp, tid, an, luna: dict(RZ))
    aprobate = []
    monkeypatch.setattr(up, "pachet_poveste_set", lambda *a, **k: aprobate.append(a[3].text) or {"ok": True})
    D = lambda t, cr=False: type("D", (), {"text": t, "cu_restante": cr})()   # noqa: E731
    with pytest.raises(erori.DateInvalide) as e:
        up.pachet_poveste_aproba(1, 2026, 9, D("În septembrie firma a avut încasări de 1.000,00 lei."), {})
    assert e.value.detaliu["cod"] == up.COD_POVESTE_ABATERI and e.value.detaliu["abateri"].count("termen: încasări") == 1
    cu_restante = "În septembrie firma a avut venituri de 1.000,00 lei. Are declarații nedepuse, cu termenele depășite."
    with pytest.raises(erori.DateInvalide) as e:
        up.pachet_poveste_aproba(1, 2026, 9, D(cu_restante), {})
    assert e.value.detaliu["cod"] == up.COD_POVESTE_RESTANTE
    up.pachet_poveste_aproba(1, 2026, 9, D(cu_restante, True), {})   # decizia expresă a contabilului
    up.pachet_poveste_aproba(1, 2026, 9, D("În septembrie firma a avut venituri de 1.000,00 lei."), {})
    assert len(aprobate) == 2


def test_288b_inchiderea_in_121_nu_e_operatiune_a_lunii():
    """Generalizare: rezultatul lunii exclude închiderea 7xx = 121 / 121 = 6xx (altfel o lună închisă ar arăta venituri 0).
    MUTAȚIE: excluderea 121 scoasă din `_note_lunii` -> venituri 0 -> pică."""
    from core import db as _db, motor
    from core.test_295_rezumat_d100 import _db_ok, _tp
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS efemer_288 CASCADE")
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), "efemer_288"))
                cur.execute("SET search_path TO efemer_288, public")
                for deb, cre, s_ in (("4111", "707", 1000), ("628", "401", 300), ("707", "121", 1000), ("121", "628", 300)):
                    cur.execute("INSERT INTO inregistrari (data, descriere, status) VALUES ('2026-09-30','n','validata') RETURNING id")
                    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)",
                                (cur.fetchone()[0], deb, cre, s_))
            r = motor.rezultat(pa._note_lunii(c, 2026, 9))
            assert (float(r["venituri"]), float(r["cheltuieli"])) == (1000.0, 300.0), r
        finally:
            c.rollback()
