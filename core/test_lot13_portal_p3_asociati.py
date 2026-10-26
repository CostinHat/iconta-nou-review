# -*- coding: utf-8 -*-
"""[lotul 13, comanda 13.1] Deficiența 526 — Date firmă → Asociați: mesajul de total al cotelor.

Comanda 13.1, verbatim: „Cu CNP invalid pe rânduri (verificarea CNP corectă), lângă buton scrie «Total cote: 100%», iar mesajul roșu spune
«cotele însumează 0%, nu 100%». Mesajul de total nu apare când singura problemă e CNP-ul.”

Logica: `asociati_api.erori_ecran` (refuzul de total judecat pe rândurile scrise, ca „Total cote” de pe ecran), chemată de
`uc_asociati._verifica`. CNP-urile: cifra de control calculată cu algoritmul din CLAUDE.md, apoi stricată intenționat (ultima cifră + 1).
MUTAȚIA: în `uc_asociati._verifica`, `_as.erori_ecran(randuri, …)` scos (verificarea comună directă) -> refuzul „însumează 0%” revine ->
`test_526_cnp_invalid_cu_cote_de_100_fara_mesaj_de_total` ROȘU.

Temei: N/A — regulă de interfață (CLAUDE.md §9: mesajele spun același lucru cu ecranul); suma 100% e invariantul aritmetic din antetul
`asociati_api` (Legea 31/1990 art.11 alin.(1), INTERPRETARE CU TEMEI deja consemnată acolo).
"""
import pytest

from core import asociati_api as _as
from core import erori as _erori
from core import uc_asociati as _uc


def _cnp(baza12):
    ch = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    c = sum(int(baza12[i]) * ch[i] for i in range(12)) % 11
    return baza12 + str(1 if c == 10 else c)


def _stricat(cnp):
    """Același CNP cu cifra de control greșită (verificarea CNP îl refuză pe bună dreptate)."""
    return cnp[:-1] + str((int(cnp[-1]) + 1) % 10)


CNP_A, CNP_B = _cnp("180010141001"), _cnp("285020241002")


def _refuz(randuri):
    with pytest.raises(_erori.DateInvalide) as ex:
        _uc._verifica(_as.randuri_din_corp(randuri))
    d = ex.value.args[0] if ex.value.args else {}
    d = d if isinstance(d, dict) else {"mesaj": str(d), "erori_campuri": []}
    return d["mesaj"], [(e["camp"], e["mesaj"]) for e in d["erori_campuri"]]


def test_526_cnp_invalid_cu_cote_de_100_fara_mesaj_de_total():
    """Doi asociați cu CNP greșit, 60% + 40%: refuzul numește CNP-urile, lângă rândurile lor, și NU spune „cotele însumează 0%”
    (pe ecran „Total cote: 100%”). ROȘU înainte: „cotele asociaților care intră însumează 0%, nu 100%”."""
    mesaj, campuri = _refuz([{"nume": "Ion Popescu", "cnp": _stricat(CNP_A), "cota": "60"},
                             {"nume": "Ana Pop", "cnp": _stricat(CNP_B), "cota": "40"}])
    assert "însumează" not in mesaj, mesaj
    assert [c for c, _m in campuri] == ["as-1-cnp", "as-2-cnp"], campuri
    assert all("CNP invalid" in m for _c, m in campuri), campuri


def test_526_cnp_invalid_si_cote_de_90_spune_totalul_de_pe_ecran():
    """Un CNP greșit și cotele scrise 60% + 30%: refuzul de total rămâne, dar spune suma rândurilor scrise (90%, cât arată „Total
    cote”), nu numai a celor care ar intra (60%)."""
    mesaj, campuri = _refuz([{"nume": "Ion Popescu", "cnp": CNP_A, "cota": "60"},
                             {"nume": "Ana Pop", "cnp": _stricat(CNP_B), "cota": "30"}])
    assert ("as-total", "cotele asociaților însumează 90%, nu 100%") in campuri, campuri
    assert "60%, nu 100%" not in mesaj, mesaj


def test_526_cote_cu_zecimale_care_dau_100_nu_se_refuza_pe_total():
    """33,33 + 33,33 + 33,34 = 100 exact (adunare în Decimal, fără zgomot de virgulă mobilă), cu un CNP greșit: niciun refuz de total."""
    cnp_c = _cnp("190030341003")
    mesaj, campuri = _refuz([{"nume": "A", "cnp": CNP_A, "cota": "33,33"}, {"nume": "B", "cnp": CNP_B, "cota": "33,33"},
                             {"nume": "C", "cnp": _stricat(cnp_c), "cota": "33,34"}])
    assert "însumează" not in mesaj and [c for c, _m in campuri] == ["as-3-cnp"], (mesaj, campuri)


def test_526_fara_alt_refuz_totalul_gresit_se_spune_ca_inainte():
    """Anti-vacuu: CNP-uri corecte, 60% + 30% -> refuzul de total, lângă „Total cote”."""
    _mesaj, campuri = _refuz([{"nume": "Ion Popescu", "cnp": CNP_A, "cota": "60"}, {"nume": "Ana Pop", "cnp": CNP_B, "cota": "30"}])
    assert campuri == [("as-total", "cotele asociaților însumează 90%, nu 100%")], campuri
