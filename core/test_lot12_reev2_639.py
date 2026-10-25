# -*- coding: utf-8 -*-
"""[lotul 12, comanda 12.2 pct.18, deficiența 639] D390 pentru 11/2026 avea termen 21.12.2026.

Cauza: `scadente.termen_legal` aplica excepția CPF art.155 alin.(2) („Creanțele fiscale administrate de organul fiscal central pentru care […]
scadența și/sau termenul de declarare se împlinesc la 25 decembrie, sunt scadente și/sau se declară până la data de 21 decembrie”) oricărei
declarații. O declarație informativă (CPF art.1 pct.19) nu declară o creanță, deci 25.12 se mută DUPĂ: CPF art.75 -> Legea 134/2010 art.181
alin.(2) („Când ultima zi a unui termen cade într-o zi nelucrătoare, termenul se prelungește până în prima zi lucrătoare care urmează.”).

Toate ecranele (Control fiscal, Termene, coada, notificările) citesc termenul din `scadente.scadenta_data` — aici se probează sursa unică și
datele existente din coadă (`core/migrare_termen_informative_decembrie.py`).
"""
from datetime import date

import pytest

from core import scadente


def test_def_639_creantele_raman_pe_21_informativele_trec_dupa():
    for tip in ("d300", "d301", "d112", "d100", "d710"):
        # CPF art.155 alin.(2): „sunt scadente și/sau se declară până la data de 21 decembrie”
        assert scadente.scadenta_data(tip, 2026, luna=11) == date(2026, 12, 21), tip
    for tip in ("d390", "d208"):
        # Legea 134/2010 art.181 alin.(2): 25.12.2026 vineri, 26 sâmbătă (sărbători), 27 duminică -> luni 28.12.2026
        assert scadente.scadenta_data(tip, 2026, luna=11) == date(2026, 12, 28), tip


def test_def_639_control_fiscal_si_termene_citesc_aceeasi_sursa():
    """Control fiscal și Termene (termene_api refolosește scadentarul din control_fiscal_api) cheamă `_termen(an, luna, tip)`."""
    from core import control_fiscal_api as cf
    assert cf._termen(2026, 11, tip="d390") == date(2026, 12, 28)
    assert cf._termen(2026, 11) == date(2026, 12, 21)   # D300 implicit, creanță


def test_def_639_mutarea_e_dupa_niciodata_inainte_pentru_informative():
    """Pe toți anii calendarului: termenul unei declarații informative nu e niciodată înaintea zilei nominale (25 / 30 / ultima zi)."""
    for an in range(2024, 2098):
        for tip in sorted(scadente.TEMEI_FARA_CREANTA):
            if not scadente.are_termen(tip, an, luna=11):
                continue
            nominala = scadente._data_nominala(tip, an, luna=11)
            t = scadente.scadenta_data(tip, an, luna=11)
            assert t >= nominala and scadente.e_zi_lucratoare(t), (tip, an, nominala, t)


# ── datele existente: elementele din coadă cu termenul mutat înapoi, pe baza de test, ROLLBACK ─────────────────────────────────────────
def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_639_vechi_elementele_din_coada_primesc_termenul_corect():
    """Firme și an SINTETICE (tenant 990639/990640, noiembrie 2098), în tranzacție anulată: un D390 activ cu termenul vechi (excepția aplicată)
    primește termenul de după 25.12.2098; un al doilea, care ar ciocni un element activ deja pe termenul corect, se sare și se numește; un
    D300 (creanță) cu 21.12 rămâne neatins; un D390 cu altă valoare decât termenul vechi rămâne neatins."""
    from core import db, migrare_termen_informative_decembrie as m
    from core.pdf_util import data_ro
    nominala = scadente._data_nominala("d390", 2098, luna=11)
    vechi = data_ro(scadente.termen_legal(nominala, creanta=True))
    corect = scadente.scadenta("d390", 2098, luna=11)
    assert vechi != corect and scadente.scadenta_data("d390", 2098, luna=11) >= nominala
    db.init_pool()
    p = db.pool()
    c = p.getconn()
    try:
        with c.cursor() as cur:
            ids = []
            plt = '{"_an": 2098, "_luna": 11, "_trim": null}'
            for tenant, tip, per, stare in ((990639, "d390", vechi, "la_senior"), (990640, "d390", vechi, "la_senior"),
                                            (990640, "d390", corect, "aprobata"), (990639, "d300", vechi, "la_senior"),
                                            (990641, "d390", "anul 2098", "la_senior")):
                # fixtura-sintetica-ok: tenanții 990639-990641 nu există, noiembrie 2098, ROLLBACK la capăt
                cur.execute("INSERT INTO public.declaratii_coada (cabinet_id, tenant_id, tip, perioada, stare, payload) "
                            "VALUES (1, %s, %s, %s, %s, %s::jsonb) RETURNING id", (tenant, tip, per, stare, plt))
                ids.append(cur.fetchone()[0])
            rez = m.aplica(c)
            cur.execute("SELECT id, perioada FROM public.declaratii_coada WHERE id = ANY(%s) ORDER BY id", (ids,))
            per = dict(cur.fetchall())
        assert per[ids[0]] == corect, per                                                   # D390 vechi -> termenul de după
        assert per[ids[1]] == vechi and [s[0] for s in rez["sarite"]] == [ids[1]], (per, rez)   # ciocnirea: sărit și numit
        assert per[ids[3]] == vechi                                                          # D300: creanță, 21.12 rămâne
        assert per[ids[4]] == "anul 2098"                                                    # altă valoare: neatinsă
        assert m.aplica(c)["actualizate"] == 0                                               # idempotentă
    finally:
        c.rollback()
        p.putconn(c)
