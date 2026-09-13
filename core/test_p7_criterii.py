# -*- coding: utf-8 -*-
"""GARDĂ: `P7_ACTION_REQUIRED = 0` nu are voie să fie citit ca „faza e închisă".

DE CE EXISTĂ (13.09.2026, la capătul valului D4). Cele trei detectoare au ajuns toate la zero —
`D1`=0 (V1+V2), `D2`=0 (valul D2), `D4`=0 (valul D4) — și odată cu ele `P7_ACTION_REQUIRED`=**0**.
Citită singură, cifra spune că nu mai e nimic de făcut. Măsurat în aceeași tură: **385 din 421 de
rute își deschid singure tranzacția**, adică stratul HTTP orchestrează în continuare, iar stratul
use-case — cel pe care textul canonic îl definește prin *„deține tranzacția (P4), orchestrează"* —
aproape că nu există (4 module declarate, 7 rute care deleagă).

*Zero pe toate detectoarele nu e zero pe fază — iar acum nu mai e o propoziție din predare, e o
gardă.* Clasa e aceeași cu `all([])` și cu brațul four-way care număra doar ce găsea: **o măsurătoare
care nu-și cunoaște domeniul afirmă despre „tot" ce a verificat despre „o parte".**

CE PĂZEȘTE, în amândouă direcțiile:
  · cele trei detectoare rămân zero (dacă unul urcă, valul lui s-a stricat);
  · criteriul care NU e satisfăcut rămâne măsurat, cu clichet — poate coborî, nu urca;
  · cât timp un criteriu canonic nu e satisfăcut, `PLAN_HARDENING.md` **nu** are voie să declare P7
    închisă. Doc↔cod, în sensul care contează: documentul nu poate raporta mai mult decât codul.
"""
import io
import os
import sys

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (RADACINA, os.path.join(RADACINA, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import p7_criterii as C  # noqa: E402

#: clichet: cifra de azi a criteriului nesatisfăcut. Poate SCĂDEA (valul use-case), niciodată urca.
CLICHET_RUTE_CU_TRANZACTIE = 385


def test_cele_trei_detectoare_sunt_ZERO_si_raman():
    n = C.numaratori()
    assert n["D1_SQL_IN_RUTA"] == 0
    assert n["D2_MOTOR_FISCAL_CU_DB"] == 0
    assert n["D4_STRAT_MIXT"] == 0


def test_criteriul_use_case_e_MASURAT_si_nu_creste():
    """Clichet pe singurul criteriu canonic rămas nesatisfăcut.

    Nu se cere să fie zero — asta ar face garda roșie din prima zi, adică un ceas cu alarmă, nu un
    clichet. Se cere să nu crească: o rută nouă care își deschide singură tranzacția o face roșie.
    """
    n = C.numaratori()
    assert n["RUTE_CARE_DESCHID_SINGURE_TRANZACTIA"] <= CLICHET_RUTE_CU_TRANZACTIE, (
        "au apărut rute care își deschid singure tranzacția: %d, clichetul e %d"
        % (n["RUTE_CARE_DESCHID_SINGURE_TRANZACTIA"], CLICHET_RUTE_CU_TRANZACTIE))
    assert n["RUTE_CARE_DESCHID_SINGURE_TRANZACTIA"] > 0, (
        "dacă a ajuns la zero, criteriul s-a satisfăcut — coboară clichetul și "
        "reia verificarea de închidere a lui P7")


def test_P7_nu_se_poate_INCHIDE_cat_timp_un_criteriu_canonic_nu_e_satisfacut():
    """Verdictul mecanic, plus doc↔cod: planul nu poate declara închis ce codul contrazice."""
    assert not C.se_poate_inchide(), (
        "toate criteriile canonice sunt satisfăcute — P7 se poate închide, iar garda asta trebuie "
        "rescrisă odată cu închiderea")
    nesatisfacute = [nume for nume, ok, _c, _t in C.criterii() if not ok]
    assert nesatisfacute == ["use-case-ul detine tranzactia, nu ruta"], nesatisfacute

    plan = io.open(os.path.join(RADACINA, "PLAN_HARDENING.md"), encoding="utf-8").read()
    assert plan.count("**P7 DESCHIS**") >= 1, (
        "`PLAN_HARDENING.md` nu mai declară P7 deschisă, deși un criteriu canonic nu e satisfăcut")
    assert plan.count("**P7 ÎNCHIS**") == 0, (
        "`PLAN_HARDENING.md` declară P7 închisă peste un criteriu canonic nesatisfăcut")


def test_fiecare_criteriu_isi_poarta_TEMEIUL():
    """O clasificare fără temei e o părere; criteriile citează linia din plan pe care se sprijină."""
    for nume, _ok, _cifra, temei in C.criterii():
        assert temei.startswith("PLAN_HARDENING.md:"), (nume, temei)
        assert len(nume) > 10


def test_ANTI_VACUUM_instrumentul_chiar_vede_rutele():
    n = C.numaratori()
    assert n["RUTE_TOTAL"] >= 400, "populația de rute s-a golit: %d" % n["RUTE_TOTAL"]
    assert n["MODULE_USE_CASE_DECLARATE"] >= 1
    _n, d = C.detaliu()
    assert len(d["detin_tranzactia"]) == n["RUTE_CARE_DESCHID_SINGURE_TRANZACTIA"]
    assert d["detin_tranzactia"] == sorted(set(d["detin_tranzactia"])), "rute numărate de două ori"


def test_o_ruta_care_deleaga_NU_e_numarata_ca_detinatoare(monkeypatch):
    """Calibrare pe forma, nu pe fișier: detectorul se uită la `get_conn`, nu la lungimea rutei.

    Se dau instrumentului două rute fabricate — una care deschide conexiunea, una care cheamă un
    use-case — și se cere să le deosebească. *Fără asta, cifra 385 ar putea fi „toate rutele", iar
    garda n-ar ști.*
    """
    import ast
    sursa = ("class app:\n    pass\n"
             "@app.post('/x')\n"
             "def ruta_care_detine():\n"
             "    with db.get_conn() as conn:\n        pass\n"
             "@app.post('/y')\n"
             "def ruta_care_deleaga():\n"
             "    return monitor_fiscal.ruleaza()\n")
    arb = ast.parse(sursa)
    monkeypatch.setattr(C, "_arbore", lambda cale: arb)
    rute = C.rute_din_main()
    assert [f.name for f in rute] == ["ruta_care_detine", "ruta_care_deleaga"]
    detin = [f.name for f in rute if C._cheama(f, "get_conn")]
    deleaga = [f.name for f in rute if C._cheama_use_case(f, {"monitor_fiscal"})]
    assert detin == ["ruta_care_detine"]
    assert deleaga == ["ruta_care_deleaga"]
