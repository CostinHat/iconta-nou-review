"""[719, comanda 14.3] O declarație datorată și nedepusă după termen apare ca restanță, prima, în „Datorate de firmă” și în Termene."""
import datetime as _dt

from core import termene_api as TA

AZI = _dt.date(2026, 10, 29)
VECTOR = {"regim_fiscal": "micro", "platitor_tva": True, "tip_decont": "lunar", "operatiuni_ic": False, "partida_simpla": False,
          "tva_data_inceput": _dt.date(2026, 1, 1), "inreg_art317": False}


def _fapt_d301(jos, zile):
    """D301 09/2026: termenul 26.10.2026 (trecut), nedepusă — ca la F3; `jos` None = fără limită jos (restanțe)."""
    d = {"tip": "d301", "an": 2026, "luna": 9, "perioada": "sep", "termen": "2026-10-26", "fapt": "achiziție intracomunitară"}
    return {"datorate": [d] if (jos is None or _dt.date.fromisoformat("2026-10-26") >= jos) else []}


def test_implicit_privire_inainte_fara_restante():
    t = TA.termene_firma(VECTOR, False, set(), AZI, declaratii_fapt=_fapt_d301)
    assert not [d for d in t if d["termen"] < "2026-10-29"], t


def test_cu_restante_d301_expirat_apare_marcat_si_primul():
    t = TA.termene_firma(VECTOR, False, set(), AZI, declaratii_fapt=_fapt_d301, restante=True)
    d301 = [d for d in t if (d["tip"], d["an"], d["luna"]) == ("d301", 2026, 9)]
    assert len(d301) == 1 and d301[0]["restanta"] is True and d301[0]["termen"] == "2026-10-26", d301
    assert all(d["restanta"] == (d["termen"] < "2026-10-29") for d in t)
    primele_viitoare = next(i for i, d in enumerate(t) if not d["restanta"])
    assert all(d["restanta"] for d in t[:primele_viitoare]) and not any(d["restanta"] for d in t[primele_viitoare:]), "restanțele întâi"


def test_depusa_nu_e_restanta():
    t = TA.termene_firma(VECTOR, False, {("d301", 2026, 9)}, AZI, declaratii_fapt=_fapt_d301, restante=True)
    assert ("d301", 2026, 9) not in {(d["tip"], d["an"], d["luna"]) for d in t}


def test_portofoliul_pune_restantele_in_cap_si_urmatoarea_e_de_azi_incolo():
    t = TA.termene_firma(VECTOR, False, set(), AZI, declaratii_fapt=_fapt_d301, restante=True)
    p = TA.portofoliu([{"tenant_id": 1, "nume": "F3", "termene": t}], AZI)
    assert p["grupuri"][0]["zile"] < 0 and p["restante"] >= 1
    assert p["urmatoarea"]["zile"] >= 0
