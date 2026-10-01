# -*- coding: utf-8 -*-
"""GARZI [Pachet FiscalOS §3]: defecte de cod verificate la sursa (Legea 70/2015, CF art.18^1).
Proba pe PORTOFOLIU: date invalide apoi valide. Fiecare gard cu proba de mutatie scrisa.
Aserteaza pe COMPORTAMENT (iesirea verifica_plafon / impozit) + re.search pe temei — fara `"sir" in X`.
"""
from datetime import date

from core import casa, common, d101

_LA = date(2026, 6, 1)   # o data cu plafoanele in vigoare 2026


def _are_cod(probleme, cod):
    return any(p["cod"] == cod for p in probleme)


# ===== §3.1: avansul spre decontare intra in plafonul total zilnic (L.70/2015 art.3 alin.4) =====
def test_s3_avans_intra_in_plafonul_total():
    # INVALID: plata PJ 6000 (A) + avans 5000 (B) = 11000 > 10000 -> PLAFON_PLATA_PJ_TOTAL.
    # MUTATIE: revert `plata_pj_total += suma` din ramura avans -> 11000 trece fara avertisment (verde fals).
    invalid = [
        {"data": "2026-06-10", "tip": "plata", "suma": 6000, "partener": "A", "partener_tip": "pj"},
        {"data": "2026-06-10", "tip": "plata", "suma": 5000, "partener": "B", "scop": "avans"},
    ]
    assert _are_cod(casa.verifica_plafon(invalid, la_data=_LA), "PLAFON_PLATA_PJ_TOTAL"), \
        "avansul trebuie sa intre in plafonul total zilnic (L.70/2015 art.3 alin.4)"
    # VALID: fara avans -> 6000 total, sub plafon -> fara avertisment
    valid = [{"data": "2026-06-10", "tip": "plata", "suma": 6000, "partener": "A", "partener_tip": "pj"}]
    assert not _are_cod(casa.verifica_plafon(valid, la_data=_LA), "PLAFON_PLATA_PJ_TOTAL")


# ===== §3.2: plata catre cash&carry = plafon total 10000, FARA limita 5000/persoana (art.3 alin.1 lit.d) =====
def test_s3_cash_and_carry_fara_limita_per_persoana():
    # VALID: 6000 catre cash&carry -> NU da PLAFON_PLATA_PJ (nu exista limita per-persoana la lit.d).
    # MUTATIE: revert ramura `elif op.get("cash_and_carry")` -> 6000 cc trateaza ca plata PJ -> fals PLAFON_PLATA_PJ.
    cc_mic = [{"data": "2026-06-10", "tip": "plata", "suma": 6000, "partener": "Metro",
               "partener_tip": "pj", "cash_and_carry": True}]
    pr = casa.verifica_plafon(cc_mic, la_data=_LA)
    assert not _are_cod(pr, "PLAFON_PLATA_PJ"), "plata la cash&carry nu are limita de 5000/persoana (lit.d)"
    assert not _are_cod(pr, "PLAFON_PLATA_CC_TOTAL"), "6000 < 10000 total -> fara avertisment"
    # INVALID: 12000 catre cash&carry > 10000 total -> PLAFON_PLATA_CC_TOTAL
    cc_mare = [{"data": "2026-06-10", "tip": "plata", "suma": 12000, "partener": "Metro",
                "partener_tip": "pj", "cash_and_carry": True}]
    assert _are_cod(casa.verifica_plafon(cc_mare, la_data=_LA), "PLAFON_PLATA_CC_TOTAL")


# ===== §3.3: IMCA inceteaza dupa 31.12.2026 (CF art.18^1 alin.16 cota, alin.17 incetare) =====
def test_s3_imca_inceteaza_dupa_2026():
    # 2026: IMCA = 0,5% x baza > 0; 2027: INCETEAZA (0). Proba pe ambele parti ale datei.
    # MUTATIE: scoate intrarea ("2027-01-01", 0, alin.17) -> 2027 preia 0,5% -> IMCA > 0.
    assert d101.impozit_minim_cifra_afaceri(60_000_000, 0, 0, 0, 2026) > 0, "2026: IMCA se aplica (0,5%)"
    assert d101.impozit_minim_cifra_afaceri(60_000_000, 0, 0, 0, 2027) == 0, \
        "2027: IMCA inceteaza (CF art.18^1 alin.17), nu continua implicit"


# ===== §3.4: mesajul PLAFON_PF citeaza art.4 alin.(1), nu art.3 =====
def test_s3_plafon_pf_citeaza_art4():
    import re as _re
    p = common.problema("PLAFON_PF", nivel=common.AVERTISMENT, partener="X", gasit=12000, asteptat=10000)
    assert _re.search(r"art\.\s*4", p["temei"]), "PLAFON_PF trebuie sa citeze L.70/2015 art.4 alin.(1), nu art.3"
