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

import ast
import io
import re
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

    *Registrul n-a fost folosit ca să le facă pe toate să dispară*: șase au ieșit din D2 fiindcă nu
    sunt motoare fiscale, iar `efactura_send` a RĂMAS motor fiscal și a rămas încălcare — singurul
    item D2 al repo-ului, din 13.09.2026 (V3) până tot pe 13.09 (valul D2).

    **Ce s-a schimbat la valul D2, și de ce proba asta se uită acum la zero:** încălcarea s-a
    închis mutând codul, nu reclasificând modulul. `efactura_send` e tot `FISCAL_ENGINE` — verificat
    mai jos, pe stratul declarat —, dar nu mai importă `db`. *Dacă răspunsul ar fi venit dintr-o
    schimbare de strat, exact proba asta ar fi trecut degeaba.*
    """
    pe_cale = R.pe_cale()
    for cale, strat_asteptat in CELE_SAPTE.items():
        assert cale in pe_cale, "unul dintre cele șapte a ieșit din registru: %s" % cale
        assert pe_cale[cale].strat == strat_asteptat, (
            "%s și-a schimbat stratul fără ca proba să fie actualizată: %s"
            % (cale, pe_cale[cale].strat))
    d2 = {i.fisier for i in S.d2_motor_fiscal_cu_db()}
    assert d2 & set(CELE_SAPTE) == set()
    assert pe_cale["core/efactura_send.py"].strat == R.FISCAL_ENGINE, (
        "D2 s-a închis mutând stratul, nu codul — exact ce proba asta interzice")
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
    assert R.strat("core/efactura_send.py") == R.FISCAL_ENGINE


def test_un_motor_fiscal_FARA_db_nu_e_item():
    """Negativul: din 13.09.2026 (valul D2), NICIUN modul declarat motor fiscal nu atinge baza.

    Proba era `len(fiscale) - 1` — cel unu fiind `efactura_send`. Acum e egalitate, și ASTA e
    afirmația livrată: nu «detectorul n-a găsit nimic», ci «niciunul dintre cele 96 nu importă
    `db`», întrebat fișier cu fișier. Că detectorul se mai poate aprinde e altă probă, sintetică.
    """
    fiscale, _ = S.module_fiscale()
    fara_db = [m for m in fiscale if not S._atinge_db(m)]
    assert len(fara_db) == len(fiscale)
    d2 = {i.fisier for i in S.d2_motor_fiscal_cu_db()}
    assert not (set(fara_db) & d2)


def test_ANTI_VACUUM_registrul_si_straturile_nu_sunt_goale():
    n = R.numaratori()
    assert n["MODULE_DECLARATE"] >= 100
    for s in R.STRATURI:
        assert n["pe_strat"].get(s, 0) > 0, "stratul %s n-are niciun modul — universul s-a rupt" % s
    assert len(S.univers_registru()) >= 100


# ============================================================
#  4b. D2 DUPĂ ÎNCHIDERE — calibrarea care nu mai are voie să stea pe o încălcare reală
# ============================================================
def test_D2_SE_APRINDE_pe_un_univers_sintetic(monkeypatch):
    """Valul D2 a lăsat detectorul fără nicio instanță. Fără proba asta, `D2=0` ar fi ambiguu.

    **De ce e nevoie de ea, și de ce arată așa.** Până la valul D2, dovada că detectorul FUNCȚIONEAZĂ
    era chiar încălcarea pe care o raporta: `core/efactura_send.py`. Închizând-o, calibrarea pozitivă
    a dispărut odată cu ea — iar un detector care raportează zero fiindcă s-a stricat arată identic
    cu unul care raportează zero fiindcă n-are ce găsi (`METODA_VERIFICARE.md` §22).

    Proba nu fabrică un fișier: schimbă UNIVERSUL, nu lumea. Îi dă lui D2 un univers în care
    `main.py` — modul REAL, care chiar importă `db` — e declarat motor fiscal, și cere ca detectorul
    să-l numească. Așa rămâne exercitat drumul întreg: registru → citirea fișierului → AST → item.
    """
    monkeypatch.setattr(S, "module_fiscale", lambda: ({"main.py"}, "UNIVERS SINTETIC (probă)"))
    itemi = S.d2_motor_fiscal_cu_db()
    assert [i.fisier for i in itemi] == ["main.py"], (
        "D2 nu se mai aprinde nici pe un modul care CHIAR importă `db`: %s" % itemi)
    assert itemi[0].detector == "D2_MOTOR_FISCAL_CU_DB"
    assert itemi[0].linie > 0


def test_D2_vede_TOATE_cele_patru_forme_de_import(tmp_path):
    """Calibrare pe FORMĂ, nu pe fișier: cele patru feluri în care un modul poate lua `core.db`.

    Un detector care ar prinde numai `from core import db` ar raporta zero despre un modul care
    scrie `import core.db` — și ar face-o tăcut. Fiecare formă are aici propriul caz, iar al
    cincilea caz e cel negativ: un `db` care nu e al nostru (`from sqlite3 import db`) NU se numără.
    """
    FORME = {
        "from core import db": 1,
        "from core.db import get_conn": 1,
        "import core.db": 1,
        "import db": 1,
        "from sqlite3 import dbapi2": 0,
        "x = 1": 0,
    }
    for sursa, asteptat in FORME.items():
        f = tmp_path / "zt_forma.py"
        f.write_text(sursa + "\n", encoding="utf-8")
        rel = os.path.relpath(str(f), RADACINA)
        gasite = S._atinge_db(rel)
        assert len(gasite) == asteptat, (
            "forma %r: detectorul a găsit %d, se aștepta %d" % (sursa, len(gasite), asteptat))


def test_motorul_fiscal_efactura_send_NU_mai_atinge_baza():
    """Ce a livrat valul D2, afirmat pe structură: zero `db`, zero SQL, în modulul care era D2.

    Nu se afirmă prin numărătoarea globală (aia ar fi verde și dacă modulul ar fi dispărut din
    univers): se întreabă fișierul, pe AST, plus faptul că a rămas DECLARAT motor fiscal.
    """
    import ast as _ast
    import io as _io
    cale = "core/efactura_send.py"
    assert R.strat(cale) == R.FISCAL_ENGINE
    assert R.pe_cale()[cale].mixt_cu is None, "a rămas declarat mixt după ce s-a separat"
    assert S._atinge_db(cale) == [], "motorul fiscal a reînceput să importe `db`"
    arb = _ast.parse(_io.open(os.path.join(RADACINA, cale), encoding="utf-8").read())
    executii = [x for x in _ast.walk(arb)
                if isinstance(x, _ast.Call) and isinstance(x.func, _ast.Attribute)
                and x.func.attr in ("execute", "executemany")]
    assert executii == [], "motorul fiscal a reînceput să execute SQL"


def test_use_case_ul_trimiterii_detine_aceleasi_TREI_tranzactii():
    """Proprietatea tranzacției NU s-a mutat — lecția 27, verificată pe structură, nu pe promisiune.

    `trimite` deschidea trei `db.get_conn()` în motorul fiscal; le deschide tot el, în use-case.
    Dacă un val viitor le-ar contopi sau le-ar urca în rută, contractul P4 s-ar schimba în tăcere —
    și proba asta cade înainte.
    """
    import ast as _ast
    import io as _io
    arb = _ast.parse(_io.open(os.path.join(RADACINA, "core/efactura_trimitere.py"),
                              encoding="utf-8").read())
    fn = [x for x in arb.body if isinstance(x, _ast.FunctionDef) and x.name == "trimite"]
    assert len(fn) == 1, "`trimite` nu mai e în use-case"
    conexiuni = [x for x in _ast.walk(fn[0])
                 if isinstance(x, _ast.Call) and isinstance(x.func, _ast.Attribute)
                 and x.func.attr == "get_conn"]
    assert len(conexiuni) == 3, (
        "hotarele tranzacțiilor s-au schimbat: %d conexiuni, erau 3" % len(conexiuni))


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
    assert n["pe_detector"]["D2"] == 0, (
        "valul D2 a inchis singura incalcare; o instanta noua cere val nou, nu clichet")
    assert n["pe_detector"]["D4"] == len(R.mixte())


def test_cifra_din_motiv_nu_imbatraneste_tacut():
    """O declaratie care spune «N instructiuni SQL» se confrunta cu modulul, la fiecare rulare.

    De ce exista garda asta: pana la V2, `main.py` purta in registru cifra 295, scrisa la V3 si
    adevarata atunci. V1 si V2 au mutat 257 de instructiuni si nimic n-a intrebat registrul —
    `D4` a continuat sa dea cifra veche drept DOVADA. Un registru care isi tine singur cifrele
    la zi nu mai poate face asta.

    Metrica nu e aleasa azi ca sa iasa: din 28 de intrari care poarta o cifra, 27 coincideau deja
    cu numarul de apeluri `execute`/`executemany` din modul. Singurul dezacord era cel imbatranit.
    """
    import scan_p7_straturi as _S

    def _numar_executii(arb):
        return sum(1 for x in ast.walk(arb)
                   if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute)
                   and x.func.attr in ("execute", "executemany"))

    def _numar_rute(arb, rel):
        return len(_S.rute_din_arbore(arb, rel))

    # (tipar, cum se recalculeaza) — ambele cifre pe care le poarta un motiv
    MASURI = ((re.compile(r"(\d+) instructiuni SQL"), _numar_executii, 28),
              (re.compile(r"(\d+) rute montate in modul"), _numar_rute, 1))
    dezacorduri, vazute = [], []
    for tipar, masoara, _prag in MASURI:
        n = 0
        for d in R.REGISTRU:
            m = tipar.search(d.motiv)
            if not m:
                continue
            n += 1
            cale = os.path.join(RADACINA, d.cale)
            if not os.path.exists(cale):
                dezacorduri.append((d.cale, tipar.pattern, int(m.group(1)), None))
                continue
            try:
                arb = ast.parse(io.open(cale, encoding="utf-8").read())
            except SyntaxError:
                continue
            real = masoara(arb) if masoara is _numar_executii else masoara(arb, d.cale)
            if real != int(m.group(1)):
                dezacorduri.append((d.cale, tipar.pattern, int(m.group(1)), real))
        vazute.append(n)
    assert vazute >= [p for _t, _m, p in MASURI], (
        "ANTI-VACUUM: garda nu mai vede cifrele din registru: %s" % vazute)
    assert dezacorduri == [], (
        "registrul poarta cifre care nu mai sunt adevarate "
        "(cale, masura, scris, real): %s" % dezacorduri)
