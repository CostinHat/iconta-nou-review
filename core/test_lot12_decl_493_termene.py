# -*- coding: utf-8 -*-
"""[lotul 12, deficiența 493] Termenele de depunere ale declarațiilor anuale, din textul actelor (core/scadente.py `_ANUALE`, TEMEI_TERMEN).

Până azi: 29 de tipuri din dispecer fără termen (`are_termen` -> False), iar D407 primea „25 a lunii următoare semestrului”, ghicit.
Citatele verbatim stau în `scadente.TEMEI_TERMEN` și sunt verificate în corpus de `core/test_temei_termene.py`; aici, data calculată.
"""
from datetime import date

import pytest

from core import scadente


@pytest.mark.parametrize("tip, an, nominala", [
    ("d101g", 2025, date(2026, 6, 25)),   # CF art.42^9 alin.(4) -> art.42 alin.(1): „până la data de 25 iunie inclusiv a anului următor”
    ("d107", 2025, date(2026, 6, 25)),    # CF art.42 alin.(3): „până la termenele prevăzute la alin. (1) și (2)”
    ("d177", 2025, date(2026, 6, 25)),    # CF art.42 alin.(4): „până la termenele de depunere a declarației anuale de impozit pe profit”
    ("d212", 2025, date(2026, 5, 25)),    # CF art.122 alin.(3): „până la data de 25 mai inclusiv a anului următor”
    ("d230", 2025, date(2026, 5, 25)),    # CF art.123^1 alin.(3): „până la termenul prevăzut la art. 122 alin. (3)”
    ("d204", 2025, date(2026, 2, 28)),    # CF art.125 alin.(4): „până în ultima zi a lunii februarie inclusiv a anului următor”
    ("d207", 2027, date(2028, 2, 29)),    # CF art.231 alin.(1): „până în ultima zi a lunii februarie inclusiv a anului curent pentru anul expirat”
    ("d402", 2025, date(2026, 2, 28)),    # CPF art.60 alin.(1): „până în ultima zi a lunii februarie a anului curent, pentru anul expirat”
    ("d108", 2026, date(2026, 2, 28)),    # CF art.237 alin.(1): „până în ultima zi a lunii februarie inclusiv a anului de impunere”
    ("d120", 2025, date(2026, 4, 30)),    # CF art.346 alin.(4): „până la data de 30 aprilie a anului următor celui de raportare”
    ("d318", 2025, date(2026, 9, 30)),    # HG 1/2016 pct.73 alin.(11): „până la data de 30 septembrie a anului calendaristic care urmează”
    ("d401", 2025, date(2026, 4, 10)),    # CPF art.60 alin.(4): „până la data de 10 aprilie a anului curent, pentru anul anterior”
])
def test_def_493_termenul_nominal_din_act(tip, an, nominala):
    assert scadente.are_termen(tip, an)
    assert scadente._data_nominala(tip, an) == nominala
    assert tip in scadente.TEMEI_TERMEN   # citatul verbatim, verificat în corpus de core/test_temei_termene.py


def test_def_493_termenul_legal_se_muta_la_zi_lucratoare():
    # 28.02.2026 e sâmbătă -> luni 02.03.2026; 10.04.2026 e Vinerea Mare, 13.04 a doua zi de Paște (Legea 220/2016) -> 14.04.2026
    assert scadente.scadenta("d207", 2025) == "02.03.2026"
    assert scadente.scadenta("d401", 2025) == "14.04.2026"


def test_def_493_d407_nu_primeste_un_termen_ghicit():
    # CPF art.61^2 alin.(2): „termenele-limită ale raportării se aprobă prin ordin comun” — ordin absent: nicio zi 25 ghicită
    assert not scadente.are_termen("d407", 2025, luna=6) and not scadente.are_termen("d407", 2025, luna=12)


def test_def_493_tipurile_ramase_in_datorie_sunt_cele_numite():
    from core.test_datorie import _FARA_TERMEN_07_10, _fara_termen
    assert _fara_termen() == _FARA_TERMEN_07_10   # 17 tipuri, fiecare cu motivul în xfail-ul din core/test_datorie.py


# ── datele existente: elementele din coadă cu „anul AAAA” (core/migrare_termene_anuale.py), pe baza de test, ROLLBACK ─────────────────
def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_493_vechi_elementele_din_coada_primesc_termenul():
    """Firmă și an SINTETICE (tenant 990493, anul 2098), în tranzacție anulată: un D207 activ cu „anul 2098” primește termenul din
    `scadente.scadenta` (CF art.231 alin.(1)); un al doilea, activ, care ar ciocni elementul activ deja pe termen, se sare și se numește;
    D106 (termen pe eveniment) rămâne cu „anul 2098”."""
    from core import db, migrare_termene_anuale as m
    db.init_pool()
    p = db.pool()
    c = p.getconn()
    try:
        with c.cursor() as cur:
            termen = scadente.scadenta("d207", 2098)
            ids = []
            for tenant, tip, per, stare in ((990493, "d207", "anul 2098", "la_senior"), (990494, "d207", "anul 2098", "la_senior"),
                                            (990494, "d207", termen, "aprobata"), (990493, "d106", "anul 2098", "la_senior")):
                # fixtura-sintetica-ok: tenanții 990493/990494 nu există, anul 2098 (termenul lui cade în 2099), ROLLBACK la capăt
                cur.execute("INSERT INTO public.declaratii_coada (cabinet_id, tenant_id, tip, perioada, stare) VALUES (1, %s, %s, %s, %s) "
                            "RETURNING id", (tenant, tip, per, stare))
                ids.append(cur.fetchone()[0])
            rez = m.aplica(c)
            cur.execute("SELECT id, perioada FROM public.declaratii_coada WHERE id = ANY(%s) ORDER BY id", (ids,))
            per = dict(cur.fetchall())
        assert per[ids[0]] == termen and termen.endswith(".2099"), per   # termenul legal (februarie 2099), nu „anul 2098”
        assert per[ids[1]] == "anul 2098" and any(s[0] == ids[1] for s in rez["sarite"]), (per, rez)   # ciocnirea: sărit și numit
        assert per[ids[3]] == "anul 2098"   # D106: termen pe eveniment (OPANAF 1292/2014), rămâne în datorie
        assert m.aplica(c)["actualizate"] == 0   # idempotentă
    finally:
        c.rollback()
        p.putconn(c)
