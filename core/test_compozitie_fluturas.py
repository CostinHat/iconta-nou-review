# -*- coding: utf-8 -*-
"""GARD — compoziția netului ajunge CHIAR la om, și e o singură sursă pentru hârtie și pentru ecran.

DE CE EXISTĂ (30.08.2026, prima poziție ieftină din lista 5). Componentele netului se compuneau
înăuntrul lui `fluturas_pdf`, deci se vedeau numai dacă omul descărca PDF-ul. Pe ecran, statul arăta
cifra fără compoziție: ruta trimitea **12 câmpuri** pe care nu le randa nimeni (clasa R97, „ruta
livrează, ecranul tace"). Reparația se putea face a doua oară în JS — și atunci ar fi existat DOUĂ
liste ale aceluiași lucru, exact clasa pe care `rand_fluturas` o descrie: *două calcule ale aceluiași
lucru nu rămân egale*. Compoziția s-a mutat într-un singur loc, `compozitie_fluturas`.

CE FACE IMPOSIBIL:
  1. ca un câmp declarat în `CAMPURI_COMPUSE` să nu ajungă de fapt la om;
  2. ca un câmp scos din compoziție să rămână declarat acolo — adică lista să mintă;
  3. ca motivul scris pentru un câmp **neafișat** (`CAMPURI_NEAFISATE_MOTIVATE`) să fie fals;
  4. ca fluturașul să-și recompună singur rândurile, despicând iar hârtia de ecran.

CALIBRAREA E PE EFECT, NU PE NUME. Un gard care ar căuta numele câmpului în corpul funcției ar trece
și pentru un câmp citit și aruncat. Aici fiecare câmp se **mută** — i se schimbă valoarea — și se
cere ca ieșirea să se schimbe. Ce se verifică e că omul vede altceva, nu că numele apare undeva.

ȘI ÎN CEALALTĂ DIRECȚIE (METODA §22): dacă mutația ar schimba ieșirea *întotdeauna*, aserțiunea de
mai sus ar trece degeaba. De-aia există și proba inversă — câmpuri care NU intră în compoziție și pe
care mutația trebuie să le lase fără efect.

CE NU VERIFICĂ, declarat: dacă cifrele sunt CORECTE pe datele unei firme (aia e probă, nu gard) și
dacă randarea în JS chiar desenează ce primește — aia se măsoară viu, cu
`scripts/scan_r97_livrat_tacut.py`.
"""
import ast
import io
import os

import pytest

from core import stat_plata_api as sp

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SURSA = os.path.join(RAD, "core", "stat_plata_api.py")

# Câmpuri ale statului care NU intră în compoziție prin construcție — martorii probei inverse.
# Dacă mutația unuia dintre ele ar schimba ieșirea, proba pozitivă n-ar mai dovedi nimic.
MARTORI_NEUTRI = ("nume_ed", "prenume_ed", "cnp", "iban", "cor", "salariu_baza", "tip_norma")


def _rand():
    """Un rând de stat SINTETIC: fiecare câmp cu valoare distinctă, toate porțile deschise.

    Valorile sunt distincte ca două câmpuri să nu se acopere din întâmplare, și strict pozitive ca
    fiecare ramură condiționată a compoziției (tichete de masă / vacanță / cadou / culturale / creșă,
    concediu medical, suprataxă) să fie parcursă.
    """
    r = {n: 100.0 + 7.0 * i for i, n in enumerate(sp.CAMPURI_COMPUSE)}
    r["cm_zile"] = 5
    r["tichete_zile"] = 12
    r["tichet_masa_valoare"] = 40.0
    r["nume"] = "Test Testescu"
    for n in sp.CAMPURI_NEAFISATE_MOTIVATE:
        r[n] = 999.0
    for n in MARTORI_NEUTRI:
        r[n] = "neatins"
    return r


def _semnatura(r):
    """Tot ce ajunge la om, ca tuplu comparabil — etichetă, sumă și fel, în ordine."""
    return tuple((c["eticheta"], c["valoare"], c["fel"]) for c in sp.compozitie_fluturas(r))


def _mutat(r, camp):
    m = dict(r)
    v = r.get(camp)
    m[camp] = (v + 3) if isinstance(v, int) else ((v + 1234.5) if isinstance(v, float) else "MUTAT")
    return m


@pytest.mark.parametrize("camp", sp.CAMPURI_COMPUSE)
def test_fiecare_camp_declarat_schimba_ce_vede_omul(camp):
    """POZITIV, pe efect: schimb valoarea câmpului -> se schimbă ce ajunge pe hârtie și pe ecran."""
    baza = _rand()
    assert _semnatura(baza) != _semnatura(_mutat(baza, camp)), (
        "`%s` e declarat în CAMPURI_COMPUSE, dar mutarea lui nu schimbă nimic din ce vede omul — "
        "ori câmpul a ieșit din compoziție și declarația a rămas, ori n-a intrat niciodată." % camp)


@pytest.mark.parametrize("camp", MARTORI_NEUTRI)
def test_mutatia_nu_schimba_orice(camp):
    """NEGATIV: fără proba asta, aserțiunea de mai sus ar putea trece pentru orice câmp."""
    baza = _rand()
    assert _semnatura(baza) == _semnatura(_mutat(baza, camp)), (
        "`%s` nu are ce căuta în compoziție, dar mutarea lui schimbă ieșirea — proba pozitivă nu mai "
        "dovedește nimic despre câmpurile declarate." % camp)


@pytest.mark.parametrize("camp", sorted(sp.CAMPURI_NEAFISATE_MOTIVATE))
def test_campul_declarat_neafisat_chiar_nu_ajunge(camp):
    """Motivul scris lângă un câmp neafișat e o AFIRMAȚIE — se verifică, nu se crede pe cuvânt."""
    baza = _rand()
    assert _semnatura(baza) == _semnatura(_mutat(baza, camp)), (
        "`%s` e trecut ca neafișat, cu motiv scris, dar de fapt ajunge la om: motivul e fals." % camp)
    assert sp.CAMPURI_NEAFISATE_MOTIVATE[camp].strip(), "motivul lui `%s` e gol" % camp


def _chei_din_stat_plata():
    """Cheile pe care `stat_plata()` le CONSTRUIEȘTE, citite din AST — nu căutate ca șir.

    Un nume căutat ca text s-ar putea potrivi într-un comentariu sau într-un docstring; nodurile
    `Dict` ale funcției conțin exact cheile care ies pe rută.
    """
    arbore = ast.parse(io.open(SURSA, encoding="utf-8").read())
    fn = next(n for n in ast.walk(arbore)
              if isinstance(n, ast.FunctionDef) and n.name == "stat_plata")
    return {k.value for nod in ast.walk(fn) if isinstance(nod, ast.Dict)
            for k in nod.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)}


def test_numele_declarate_sunt_chiar_campuri_ale_statului():
    """O listă care numește câmpuri inexistente păzește o lume pe care n-o vede."""
    chei = _chei_din_stat_plata()
    assert len(chei) > 30, "ANTI-VACUU: doar %d chei citite din `stat_plata`" % len(chei)
    assert set(sp.CAMPURI_COMPUSE) <= chei, (
        "declarate compuse, dar `stat_plata` nu le trimite: %s"
        % sorted(set(sp.CAMPURI_COMPUSE) - chei))
    assert set(sp.CAMPURI_NEAFISATE_MOTIVATE) <= chei, (
        "declarate neafișate, dar `stat_plata` nu le trimite deloc: %s"
        % sorted(set(sp.CAMPURI_NEAFISATE_MOTIVATE) - chei))
    assert not (set(sp.CAMPURI_COMPUSE) & set(sp.CAMPURI_NEAFISATE_MOTIVATE)), (
        "un câmp nu poate fi și compus, și declarat neafișat")


def test_fluturasul_nu_isi_mai_compune_randurile():
    """Sursa unică se apără STRUCTURAL: `fluturas_pdf` cheamă compoziția și nu mai clădește rânduri."""
    arbore = ast.parse(io.open(SURSA, encoding="utf-8").read())
    fn = next(n for n in ast.walk(arbore)
              if isinstance(n, ast.FunctionDef) and n.name == "fluturas_pdf")
    chemate = {n.func.id for n in ast.walk(fn)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    # operator de MULȚIME, nu `in`: pe un șir crapă, în loc să treacă ca sub-șir
    assert chemate >= {"compozitie_fluturas"}, "fluturașul nu mai citește din sursa unică"
    assert not (chemate & {"randuri_deducere"}), (
        "fluturașul cheamă din nou `randuri_deducere` — semn că își recompune singur rândurile")


def test_compozitia_are_cele_patru_feluri_si_ambele_totaluri():
    """Anti-vacuu pe compoziția însăși: un `[]` ar trece toate probele de mai sus fără să spună nimic."""
    c = sp.compozitie_fluturas(_rand())
    assert len(c) >= 15, "compoziție prea săracă: %d rânduri" % len(c)
    assert {x["fel"] for x in c} == {sp.FEL_LINIE, sp.FEL_TOTAL, sp.FEL_MENTIUNE, sp.FEL_NOTA}
    totaluri = [x["eticheta"] for x in c if x["fel"] == sp.FEL_TOTAL]
    assert len(totaluri) == 2, "un fluturaș are DOUĂ totaluri (net, disponibil), nu %d" % len(totaluri)


def test_salariat_doar_cu_tichete_culturale_isi_vede_tichetele():
    """DIVERGENȚA găsită la scrierea compoziției, 30.08.2026 — regresie, nu ipoteză.

    `fluturas_pdf` deschidea secțiunea de tichete doar pe `masa or vacanta or cadou`, iar totalul
    disponibil îl recalcula ca `net + nominal + vacanta + cadou`. Ruta trimitea altceva:
    `total_disponibil` cu încă doi termeni — culturale și creșă. Deci un salariat cu tichete
    CULTURALE nu le vedea deloc pe hârtie, iar unul cu creșă vedea pe ecran alt total decât pe
    fluturaș. Compoziția unică le închide pe amândouă; testul le ține închise.
    """
    r = {n: 0.0 for n in sp.CAMPURI_COMPUSE}
    r["net"] = 3000.0
    r["tichete_cultural"] = 150.0
    r["valoare_tichete"] = 150.0
    r["total_disponibil"] = 3150.0
    comp = sp.compozitie_fluturas(r)
    # Pe VALOARE, nu pe eticheta: un gard care ar căuta „cultural" într-un text ar păzi formularea,
    # nu comportamentul — se poate rescrie eticheta fără ca nimic să cadă (METODA §23, clichetul 50).
    assert 150.0 in [c["valoare"] for c in comp], (
        "un salariat care are NUMAI tichete culturale nu-și vede tichetele: %s" % comp)
    disponibil = [c["valoare"] for c in comp if c["fel"] == sp.FEL_TOTAL]
    assert 3150.0 in disponibil, (
        "totalul disponibil nu-l ia pe cel al rutei, ci îl recalculează: %s" % disponibil)


def test_exemplar_inghetat_fara_campurile_noi_nu_arata_zero():
    """Un exemplar emis ÎNAINTE de câmpurile noi nu le are — și n-are voie să arate 0 acolo unde
    arăta o sumă. Aceeași grijă ca la `randuri_deducere`, verificată, nu presupusă."""
    vechi = {"brut": 5000.0, "net": 3000.0, "tichete_nominal": 480.0, "cass_tichete": 48.0,
             "impozit_tichete": 48.0, "tichete_zile": 12, "tichet_masa_valoare": 40.0,
             "deducere": 800.0}
    totaluri = [c["valoare"] for c in sp.compozitie_fluturas(vechi) if c["fel"] == sp.FEL_TOTAL]
    assert 3480.0 in totaluri, (
        "exemplar vechi, fără `total_disponibil`: totalul trebuie refăcut din componente, nu 0 — %s"
        % totaluri)
