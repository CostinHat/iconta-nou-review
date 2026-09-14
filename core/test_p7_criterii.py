# -*- coding: utf-8 -*-
"""GARDĂ: cele patru criterii canonice ale lui P7, măsurate — și niciunul nu are voie să scadă.

DE CE EXISTĂ (13.09.2026, la capătul valului D4). Cele trei detectoare au ajuns toate la zero —
`D1`=0 (V1+V2), `D2`=0 (valul D2), `D4`=0 (valul D4) — și odată cu ele `P7_ACTION_REQUIRED`=**0**.
Citită singură, cifra spune că nu mai e nimic de făcut. Măsurat în aceeași tură: **385 din 421 de
rute își deschid singure tranzacția**, adică stratul HTTP orchestrează în continuare, iar stratul
use-case — cel pe care textul canonic îl definește prin *„deține tranzacția (P4), orchestrează"* —
aproape că nu există (4 module declarate, 7 rute care deleagă).

*Zero pe toate detectoarele nu e zero pe fază — iar asta n-a fost o propoziție din predare, a fost
o gardă.* Clasa e aceeași cu `all([])` și cu brațul four-way care număra doar ce găsea: **o
măsurătoare care nu-și cunoaște domeniul afirmă despre „tot" ce a verificat despre „o parte".**

**CE S-A ÎNTÂMPLAT ÎNTRE TIMP (13.09.2026, valul use-case).** Cele **385 de corpuri de rută** au
plecat în stratul `USE_CASE` — 27 de module `core/uc_*.py` —, împreună cu **58 de helperi** și
**12 nume de modul** pe care le cereau. `main.py` a scăzut de la **11714** la **6546** de linii, iar
fiecare rută a rămas cu decoratorul, semnătura și docstringul ei, plus o delegare. Contractul HTTP
nu s-a atins, iar asta nu e o afirmație: `core/test_p7_uc.py` confruntă, funcție cu funcție, cu
`main.py` de la commitul dinainte de val, perechile `(cod, mesaj)` — cu o singură abatere declarată,
cu motivul ei.

CE PĂZEȘTE, în amândouă direcțiile:
  · cele trei detectoare rămân zero (dacă unul urcă, valul lui s-a stricat);
  · **al patrulea criteriu e ZERO și rămâne zero** — nu mai e clichet, fiindcă n-are unde coborî:
    o rută nouă care își deschide singură tranzacția face garda roșie din prima zi;
  · `PLAN_HARDENING.md` nu poate declara P7 deschisă peste patru criterii satisfăcute, nici închisă
    peste unul nesatisfăcut. Doc↔cod în amândouă sensurile: documentul nu poate raporta nici mai
    mult, nici mai puțin decât codul.
"""
import io
import os
import sys

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (RADACINA, os.path.join(RADACINA, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import p7_criterii as C  # noqa: E402

#: zero, și rămâne zero. A fost clichet la **385** cât a durat valul use-case; de când criteriul
#: e satisfăcut, singura cifră care trece e cea care nu mai lasă loc de întors.
RUTE_CU_TRANZACTIE_ADMISE = 0


def test_cele_trei_detectoare_sunt_ZERO_si_raman():
    n = C.numaratori()
    assert n["D1_SQL_IN_RUTA"] == 0
    assert n["D2_MOTOR_FISCAL_CU_DB"] == 0
    assert n["D4_STRAT_MIXT"] == 0


def test_use_case_ul_DETINE_tranzactia_si_asa_ramane():
    """Criteriul care a ținut faza deschisă, acum satisfăcut — și păzit ca zero.

    Cât a durat valul, cifra a fost un clichet: 385 care puteau doar să scadă. De când e zero,
    clichetul n-ar mai păzi nimic — orice rută nouă care își deschide singură tranzacția ar încăpea
    sub el. Se cere deci egalitatea, iar delegările se numără ca anti-vacuum: o rută care nu mai
    deschide nimic fiindcă a fost ștearsă nu e același lucru cu una care deleagă.
    """
    n = C.numaratori()
    assert n["RUTE_CARE_DESCHID_SINGURE_TRANZACTIA"] == RUTE_CU_TRANZACTIE_ADMISE, (
        "%d rute își deschid singure tranzacția, iar stratul HTTP n-are voie s-o dețină: %s"
        % (n["RUTE_CARE_DESCHID_SINGURE_TRANZACTIA"], C.detaliu()[1]["detin_tranzactia"][:8]))
    assert n["RUTE_CARE_CHEAMA_UN_USE_CASE"] >= 380, (
        "doar %d rute deleagă către un use-case — stratul s-a golit, nu s-a curățat"
        % n["RUTE_CARE_CHEAMA_UN_USE_CASE"])


def test_P7_e_INCHISA_si_planul_o_spune():
    """Verdictul mecanic, plus doc↔cod în amândouă sensurile.

    Regula n-a fost „planul să zică deschis", ci **planul nu poate raporta altceva decât codul**.
    Cât timp un criteriu nu era satisfăcut, planul n-avea voie să declare închis; acum, cu toate
    patru satisfăcute, n-are voie să mai declare deschis."""
    nesatisfacute = [nume for nume, ok, _c, _t in C.criterii() if not ok]
    assert not nesatisfacute, nesatisfacute
    assert C.se_poate_inchide()

    plan = io.open(os.path.join(RADACINA, "PLAN_HARDENING.md"), encoding="utf-8").read()
    assert plan.count("**P7 ÎNCHIS**") >= 1, (
        "toate criteriile canonice sunt satisfăcute, dar `PLAN_HARDENING.md` nu declară P7 închisă")
    assert plan.count("**P7 DESCHIS**") == 0, (
        "`PLAN_HARDENING.md` încă declară P7 deschisă peste patru criterii satisfăcute")


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
