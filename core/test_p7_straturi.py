# -*- coding: utf-8 -*-
"""GARDA REGISTRULUI DE STRATURI (P7 · V3) — un modul relevant nu poate apărea fără strat declarat.

CE PĂZEȘTE, și de ce e nevoie de o gardă și nu doar de un fișier scris: registrul trebuie să fie
exhaustiv față de **univers**, nu față de ziua în care a fost scris. Universul se derivă din repo la
fiecare rulare; un modul nou care intră în el fără declarație pică poarta, iar un strat scris greșit
pică odată cu el.

Cele trei ținte ale contractului V3, fiecare cu proba ei:
  `NEW_RELEVANT_MODULE_WITHOUT_LAYER=FAIL` · `INVALID_LAYER=FAIL` · `DUPLICATE_LAYER_DECLARATION=FAIL`

Și cele șapte module care, până la registru, n-aveau răspuns — fiecare cu stratul lui și cu
verdictul D2 care decurge din el.
"""
from __future__ import annotations

import os
import sys

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RADACINA, "scripts"))
sys.path.insert(0, RADACINA)

from core import straturi as R  # noqa: E402
import p7_clasificare as CL  # noqa: E402
import scan_p7_straturi as S  # noqa: E402


# ============================================================
#  1. EXHAUSTIVITATE — față de UNIVERS, nu față de ce exista atunci
# ============================================================
def test_fiecare_modul_din_univers_are_un_strat_declarat():
    """`UNDECLARED_RELEVANT_MODULES=0`. Universul se derivă; registrul se scrie; diferența pică."""
    univers = S.univers_registru()
    declarate = {d.cale for d in R.REGISTRU}
    lipsa = sorted(univers - declarate)
    assert not lipsa, (
        "module relevante fără strat declarat (adaugă-le în `core/straturi.py`): %s" % lipsa)


def test_registrul_nu_declara_module_INEXISTENTE():
    """[V1, 13.09.2026] Proba s-a îngustat, deliberat, și merită citit de ce.

    Cerea ca tot ce e declarat să fie în universul derivat. Dar universul spune cine TREBUIE să aibă
    o declarație, nu cine ARE VOIE: un repository nou, curat — fără rute, fără valori fiscale — n-ar
    fi intrat în el, iar proba l-ar fi respins tocmai fiindcă e curat. Ce rămâne cerut e ce conta de
    fapt: o declarație să nu trimită la un fișier care nu există. Exhaustivitatea (univers ⊆
    declarate) e neatinsă, și e probată separat.
    """
    import os
    fantoma = sorted(d.cale for d in R.REGISTRU
                     if not os.path.exists(os.path.join(RADACINA, d.cale)))
    assert not fantoma, "declarații fără fișier: %s" % fantoma


def test_un_modul_NOU_in_univers_FARA_declaratie_pica():
    """Mutația gărzii de mai sus: dacă universul crește cu un modul nedeclarat, garda TREBUIE să-l
    vadă. Fără proba asta, `test_fiecare_modul...` ar putea fi verde fiindcă nu se uită nicăieri."""
    univers = set(S.univers_registru()) | {"core/zt_modul_nou_nedeclarat.py"}
    declarate = {d.cale for d in R.REGISTRU}
    assert univers - declarate == {"core/zt_modul_nou_nedeclarat.py"}


# ============================================================
#  2. UNICITATE, STRAT VALID, DECLARAȚIE COMPLETĂ
# ============================================================
def test_registrul_real_nu_are_nicio_declaratie_invalida():
    """`MULTI_LAYER_MODULES=0`, `UNKNOWN_LAYER_MODULES=0` pe registrul care chiar e în repo."""
    assert R.declaratii_invalide() == []
    n = R.numaratori()
    assert n["MULTI_LAYER_MODULES"] == 0 and n["UNKNOWN_LAYER_MODULES"] == 0


def test_un_strat_INVALID_pica():
    stricat = (R.D("core/x.py", "CONTROLER", None, "motiv", "regulă"),)
    assert {x.cod for x in R.declaratii_invalide(stricat)} == {R.STRAT_NECUNOSCUT}


def test_o_cale_declarata_de_DOUA_ORI_pica():
    stricat = (R.D("core/x.py", R.HTTP, None, "m", "r"),
               R.D("core/x.py", R.REPOSITORY, None, "m", "r"))
    assert {x.cod for x in R.declaratii_invalide(stricat)} == {R.DUBLURA}


def test_o_declaratie_FARA_motiv_sau_FARA_regula_pica():
    """O clasificare fără temei e o părere. Registrul nu primește păreri."""
    for stricat in ((R.D("core/x.py", R.HTTP, None, "", "r"),),
                    (R.D("core/x.py", R.HTTP, None, "m", ""),)):
        assert {x.cod for x in R.declaratii_invalide(stricat)} == {R.FARA_TEMEI}


def test_fiecare_modul_e_intr_UN_SINGUR_strat():
    """Bijectivitatea cerută: un modul, exact un strat. `mixt_cu` numește al doilea strat ATINS,
    nu o a doua declarație — și nu poate fi egal cu primul."""
    pe_cale = R.pe_cale()
    assert len(pe_cale) == len(R.REGISTRU), "o cale apare de mai multe ori"
    for d in R.REGISTRU:
        assert d.strat in R.STRATURI
        assert d.mixt_cu != d.strat


# ============================================================
#  3. CELE ȘAPTE care n-aveau răspuns până la registru
# ============================================================
CELE_SAPTE = {
    "core/curs_bnr.py": R.REPOSITORY,
    "core/efactura_send.py": R.FISCAL_ENGINE,
    "core/firma_rezumat.py": R.REPOSITORY,
    "core/monitor_fiscal.py": R.USE_CASE,
    "core/notificari_scadenta.py": R.USE_CASE,
    "core/stare_partajata.py": R.REPOSITORY,
    "core/stat_plata_emis.py": R.REPOSITORY,
}


def test_cele_sapte_foste_EVIDENCE_LIMITATION_au_fiecare_un_strat():
    """Fiecare dintre cele șapte are acum o clasă adevărată, nu o excludere.

    *Registrul n-a fost folosit ca să le facă pe toate să dispară*: șase ies din D2 fiindcă nu sunt
    motoare fiscale, dar `efactura_send` RĂMÂNE motor fiscal și importă `db` — deci e încălcare, și
    a devenit singurul item D2 al repo-ului.
    """
    pe_cale = R.pe_cale()
    for cale, strat_asteptat in CELE_SAPTE.items():
        assert cale in pe_cale, "unul dintre cele șapte a ieșit din registru: %s" % cale
        assert pe_cale[cale].strat == strat_asteptat, (
            "%s și-a schimbat stratul fără ca proba să fie actualizată: %s"
            % (cale, pe_cale[cale].strat))
    d2 = {i.fisier for i in S.d2_motor_fiscal_cu_db()}
    assert d2 & set(CELE_SAPTE) == {"core/efactura_send.py"}
    assert len([c for c, s in CELE_SAPTE.items() if s != R.FISCAL_ENGINE]) == 6


def test_niciunul_dintre_cele_sapte_nu_e_EVIDENCE_LIMITATION():
    """`D2_EVIDENCE_LIMITATIONS=0` — ținta obligatorie a lui V3."""
    n = CL.numaratori()
    assert n["P7_EVIDENCE_LIMITATIONS"] == 0
    clase = {CL.REGULI[cheie].clasa for _it, cheie in CL.itemi()}
    assert CL.EL not in clase


# ============================================================
#  4. D2, calibrat pe straturi
# ============================================================
def test_D2_vede_FISCAL_ENGINE_cu_db_si_NU_vede_celelalte_straturi():
    """Contractul, în ambele direcții: contează stratul DECLARAT, nu ce pare modulul.

    `main.py` importă `db` și are 295 de instrucțiuni SQL — dar e declarat `HTTP`, deci nu e item
    D2. `core/firma_rezumat.py` importă `db` de cinci ori — dar e `REPOSITORY`, iar stratul ăla are
    voie. Dacă D2 le-ar raporta, ar însemna că nu citește registrul.
    """
    d2 = {i.fisier for i in S.d2_motor_fiscal_cu_db()}
    for cale in ("main.py", "core/firma_rezumat.py", "core/stare_partajata.py",
                 "core/monitor_fiscal.py"):
        assert cale not in d2, "%s (strat %s) a ajuns item D2" % (cale, R.strat(cale))
        assert S._atinge_db(cale), "premisa: %s chiar atinge baza" % cale
    assert d2 >= {"core/efactura_send.py"}
    assert R.strat("core/efactura_send.py") == R.FISCAL_ENGINE


def test_un_motor_fiscal_FARA_db_nu_e_item():
    """Negativul: 96 de module declarate motor fiscal, unul singur atinge baza."""
    fiscale, _ = S.module_fiscale()
    fara_db = [m for m in fiscale if not S._atinge_db(m)]
    assert len(fara_db) == len(fiscale) - 1
    d2 = {i.fisier for i in S.d2_motor_fiscal_cu_db()}
    assert not (set(fara_db) & d2)


def test_ANTI_VACUUM_registrul_si_straturile_nu_sunt_goale():
    n = R.numaratori()
    assert n["MODULE_DECLARATE"] >= 100
    for s in R.STRATURI:
        assert n["pe_strat"].get(s, 0) > 0, "stratul %s n-are niciun modul — universul s-a rupt" % s
    assert len(S.univers_registru()) >= 100


# ============================================================
#  5. AMESTECUL, numit
# ============================================================
def test_modulele_mixte_sunt_ACTION_REQUIRED_nu_tolerate():
    """`MIXED_LAYER_MODULE=YES` nu e o excepție: e o poziție de lucru. Comanda V3 o cere clasificată
    `ACTION_REQUIRED`, iar aici se verifică exact asta."""
    mixte = R.mixte()
    assert mixte, "niciun modul mixt — dacă e adevărat, V1/V2 n-au ce separa"
    assert CL.REGULI["D4_STRAT_MIXT"].clasa == CL.AR
    itemi_d4 = {i.fisier for i in S.d4_strat_mixt()}
    assert itemi_d4 == {d.cale for d in mixte}


def test_contabilitatea_P7_se_inchide_dupa_V3():
    n = CL.numaratori()
    assert n["P7_CLASSIFIED_ITEMS"] == n["P7_RAW_ITEMS"]
    assert n["P7_UNCLASSIFIED_ITEMS"] == 0
    assert n["P7_UNEXPLAINED_EXCLUSIONS"] == 0
    assert n["P7_EVIDENCE_LIMITATIONS"] == 0
    assert n["pe_detector"]["D2"] == 1
    assert n["pe_detector"]["D4"] == len(R.mixte())
