# -*- coding: utf-8 -*-
"""GARD [02.09.2026]: perimetrul portii SCURTE se DERIVA, si stie cand nu poate.

**Regula pazita** (`PLAN_LUCRU.md`, regula 4 de conducere a lucrului, Costin 02.09.2026):
*„se ruleaza constructia atinsa si tot ce depinde de ea, derivat din dependentele reale din cod,
nu ales de la caz la caz. … Daca derivarea nu poate stabili cu certitudine perimetrul, se ruleaza
tot si se spune de ce."*

**CELE DOUA DIRECTII, fiindca una singura n-ar dovedi nimic** (METODA §22):
  1. pe un modul cu dependenti CUNOSCUTI, perimetrul ii CONTINE — altfel instrumentul ar putea
     intoarce mereu lista vida si ar parea ca „a scurtat" perfect;
  2. pe clasele pe care graful de import NU le vede (registru `.md`, `main.py`, `conftest.py`),
     instrumentul REFUZA sa scurteze si spune de ce — altfel ar da verde despre ce n-a rulat.

**Ce NU pazeste, declarat:** ca perimetrul e MINIM. Un perimetru prea larg costa minute; unul prea
ingust costa o regresie nevazuta. Gardul apara doar directia care doare.
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from scripts import perimetru as P  # noqa: E402


def test_perimetrul_contine_dependentii_REALI_ai_modulului_atins():
    """`core/d100.py` e importat de `core/declaratii_api.py` si de `core/d100_reconciliere.py`;
    amandoua au teste proprii. Un perimetru care nu le contine ar fi o poarta care sare peste
    exact ce s-a atins."""
    teste, incerte = P.perimetru(["core/d100.py"])
    assert not incerte, "derivarea a raportat incertitudini pe un modul curat: %s" % incerte
    # Operatorul de MULTIME, nu `in`: `>=` **crapa** daca `teste` devine vreodata un sir, in loc
    # sa treaca ca sub-sir. Forma recomandata in chiar antetul lui `core/scan_garzi_pe_text.py`.
    ceruti = {"core/test_d100.py", "core/test_d100_reconciliere.py",
              "core/test_declaratii_componente.py", "core/test_supervizor.py"}
    assert set(teste) >= ceruti, (
        "depind tranzitiv de core/d100.py si NU sunt in perimetru: %s — o schimbare de camp ar "
        "trece poarta scurta fara sa fie probata acolo unde se citeste" % sorted(ceruti - set(teste)))


def test_un_modul_fara_niciun_dependent_nu_umfla_perimetrul():
    """Directia opusa: daca perimetrul ar fi mereu «tot», regula n-ar scurta nimic si gardul de
    sus ar trece degeaba."""
    teste_d100, _ = P.perimetru(["core/d100.py"])
    toate = [f for f in P._fisiere_py() if os.path.basename(f).startswith("test_")]
    assert len(teste_d100) < len(toate), (
        "perimetrul lui core/d100.py (%d) nu e mai mic decat suita intreaga (%d) — atunci "
        "instrumentul nu deriva nimic, doar returneaza tot" % (len(teste_d100), len(toate)))


def test_ce_s_a_modificat_fata_de_HEAD_nu_include_fisierele_NEURMARITE():
    """*„Se stabileste din ce s-a MODIFICAT fata de HEAD"* — adica `git diff HEAD`, care acopera
    fisierele urmarite schimbate SI adaugirile puse in index. Un fisier neurmarit si nestagiat nu
    face parte din ce se publica: pytest nu-l culege (probele se numesc `proba_*`), iar un test nou
    intra aici de indata ce e stagiat.

    **DE CE E UN GARD, nu o preferinta.** Forma dinainte adauga si neurmaritele, iar arborele asta
    poarta permanent ~299 — deci instrumentul REFUZA sa scurteze la fiecare tura, si regula 5 devenea
    inaplicabila. *Iar cand un instrument refuza mereu, tentatia e sa-l ocolesti — s-a si intamplat,
    o data, si Costin a oprit-o: „nu-l suprascrie cu judecata ta."* Gardul asta face ca refuzul sa
    ramana informativ."""
    atinse = set(P.atinse_din_git())
    nt = set(P.netracked())
    assert not (atinse & nt), (
        "`atinse_din_git` socoteste ca modificate fisiere NEURMARITE: %s" % sorted(atinse & nt)[:5])
    # anti-vacuu: daca n-ar exista niciun fisier neurmarit, aserttiunea de sus n-ar dovedi nimic
    assert nt, ("[anti-vacuu] nu exista niciun fisier neurmarit in arbore, deci nu se poate proba "
                "ca sunt tinute afara din perimetru")


# ── regula 5: o tura fara executabile ruleaza doar garzile de registre si documente ────────────
def test_o_tura_DOAR_DE_DOCUMENTE_deriva_garzile_de_registre():
    """Regula 5 (Costin, 03.09.2026): *„o tura care nu atinge niciun fisier executabil (.py, .js)
    ruleaza doar garzile de registre si documente, nu suita completa. Se stabileste din ce s-a
    modificat fata de HEAD, nu prin judecata."*

    Perimetrul se DERIVA — un test intra daca numeste el insusi un document urmarit de git, sau
    daca importa un scaner din `scripts/` care il numeste. Aici se cere ca derivarea sa prinda
    garzile de registru pe care le-am platit una cate una."""
    teste, incerte = P.perimetru(["PREDARE_LANT.md", "CONFORMITATE.md"])
    assert not incerte, "o tura doar de documente n-ar trebui sa lase perimetrul deschis: %s" % incerte
    ceruti = {"core/test_conformitate.py", "core/test_predare_cifre.py",
              "core/test_predare_proaspata.py", "core/test_clichete_generate.py",
              "core/test_capturi_numite.py", "core/test_trasee.py",
              "core/test_garzi_inventar.py", "core/test_agenda.py",
              "core/test_lista3.py"}
    assert set(teste) >= ceruti, (
        "garzi de registru care NU intra in perimetrul de documente: %s" % sorted(ceruti - set(teste)))


def test_perimetrul_de_documente_e_mai_mic_decat_suita():
    """Directia opusa. O derivare prea generoasa n-ar scurta nimic — doar ar imbraca «ruleaza tot»
    in alt nume. *Prima forma propaga tranzitiv prin tot graful si intorcea 357 din 578; masurat,
    nu banuit.*"""
    teste, _ = P.perimetru(["PREDARE_LANT.md"])
    toate = [f for f in P._fisiere_py() if os.path.basename(f).startswith("test_")]
    assert len(teste) < len(toate) // 2, (
        "perimetrul de documente are %d din %d teste — peste jumatate de suita nu mai e o derivare"
        % (len(teste), len(toate)))


def test_UN_SINGUR_executabil_atins_readuce_poarta_de_azi():
    """*„Daca s-a atins macar un fisier executabil, poarta ramane cum e azi."* Se stabileste din
    EXTENSIE, nu prin judecata: un `.md` alaturi de un `.py` NU mai da perimetrul de documente."""
    assert P.executabile_atinse(["PREDARE_LANT.md", "GARZI.md"]) == []
    assert P.executabile_atinse(["PREDARE_LANT.md", "core/d100.py"]) == ["core/d100.py"]
    assert P.executabile_atinse(["static/js/versiune.js"]) == ["static/js/versiune.js"]

    doar_doc, _ = P.perimetru(["PREDARE_LANT.md"])
    mixt, incerte = P.perimetru(["PREDARE_LANT.md", "core/d100.py"])
    assert incerte, (
        "un `.md` atins ALATURI de cod trebuie sa lase perimetrul deschis — graful de import nu "
        "vede cine citeste registrul, iar acolo alternativa e poarta completa")
    assert set(mixt) != set(doar_doc), "cazul mixt a intors acelasi perimetru ca cel de documente"


def test_ce_graful_de_import_NU_vede_cere_poarta_COMPLETA():
    """Pe clasele pe care graful de import nu le vede, derivarea trebuie sa REFUZE, nu sa intoarca
    un perimetru mic si linistitor.

    **[03.09.2026] Cazul `.md` SINGUR a iesit de aici, prin regula 5 a lui Costin** — o tura care nu
    atinge niciun executabil are un perimetru care se poate inchide: garzile de documente. Ce ramane
    nederivabil e cazul **MIXT** (un registru atins alaturi de cod: graful nu spune ce cod mai
    depinde de registru) si fisierele care schimba rularea intregii suite. *Gardul s-a mutat pe
    regula noua, nu s-a slabit: acum cere refuz exact acolo unde intrebarea chiar ramane deschisa.*
    """
    for atins in (["PLAN_LUCRU.md", "core/d100.py"], ["main.py"], ["conftest.py"]):
        _teste, incerte = P.perimetru(atins)
        assert incerte, (
            "%s a produs un perimetru DERIVAT, fara nicio incertitudine — dar graful de import "
            "nu vede cine il citeste, deci verdele ar fi despre ce n-a rulat" % atins)
        assert any(any(a in m for a in atins) for m in incerte), (
            "incertitudinea nu numeste fisierul care a produs-o: %s" % incerte)


def test_motivul_incertitudinii_e_SCRIS_nu_doar_semnalat():
    """«se ruleaza tot SI SE SPUNE DE CE». Un refuz fara motiv scris devine, la a treia oara, o
    superstitie: se ruleaza tot fiindca «asa face instrumentul»."""
    # Cazul MIXT: registru + cod. `.md` singur are perimetru inchis din 03.09 (regula 5).
    _teste, incerte = P.perimetru(["CONFORMITATE.md", "core/d100.py"])
    assert incerte and all(" — " in m and len(m.split(" — ")[1].strip()) > 20 for m in incerte), (
        "incertitudinile n-au motiv scris: %s" % incerte)


def test_importurile_se_citesc_cu_AST_nu_din_text():
    """Clichetul 50 / METODA §23, aplicat instrumentului insusi: un `import` scris intr-un
    comentariu sau intr-un sir NU e o dependenta. Un scaner pe text nu deosebeste codul de proza —
    lectia 3 din predarea de pe 02.09, intoarsa aici ca gard."""
    import ast
    sursa = open(os.path.join(_RAD, "scripts", "perimetru.py"), encoding="utf-8").read()
    arbore = ast.parse(sursa)
    fn = next(n for n in ast.walk(arbore)
              if isinstance(n, ast.FunctionDef) and n.name == "importurile")
    apeluri = {n.func.attr for n in ast.walk(fn)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert apeluri >= {"parse", "walk"}, (
        "`importurile` nu mai foloseste `ast` — daca a trecut pe expresii regulate, un import "
        "citat intr-un comentariu devine o dependenta, iar perimetrul creste pe proza")
