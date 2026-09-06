# -*- coding: utf-8 -*-
"""GARD: registrul de evidenta fiscala — si mai ales ca nu devine un AL DOILEA calcul al aceluiasi an.

**Defectul central, si de ce e altul decat la celelalte doua registre.** Registrul asta exista ca sa
JUSTIFICE o declaratie: norma cere sa cuprinda *„orice informatie cuprinsa in declaratia fiscala,
obtinuta in urma unor prelucrari ale datelor furnizate de inregistrarile contabile"*. Daca si-ar
calcula singur cifrele, ar putea sa nu coincida cu D101-ul depus — si atunci documentul care ar
trebui sa sustina declaratia ar fi proba impotriva ei. De-aia compunerea pleaca din campurile `P`
ale D101, si de-aia se pazeste ca nu apare o a doua aritmetica.

**Al doilea lucru pazit**: cele sapte categorii sunt ENUMERATE in norma. Nu sunt o grupare aleasa de
mine, deci nu se pot rearanja sau contopi fara ca registrul sa nu mai fie cel cerut.

**Al treilea**: totalizarea pe trimestru NU se fabrica. Norma o admite, dar formulele D101 sunt
anuale; rulate pe trei luni ar da o cifra gresita. Refuzul e explicit si poarta motivul — un registru
lipsa se vede, unul gresit nu.
"""
import ast
import io
import os

import pytest

from core import registru_evidenta_fiscala as _ref

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── 1. CELE SAPTE CATEGORII SUNT ALE NORMEI, NU ALE MELE ─────────────────────────────────────

def test_categoriile_sunt_cele_ENUMERATE_de_norma():
    """HG 1/2016 pct. 8 le numeste, in ordine. A opta („orice informatie cuprinsa in declaratia
    fiscala") e teza finala a aceluiasi punct, si de-aia sta separat, cu temeiul ei."""
    coduri = [c for c, _e, _t, _p in _ref.CATEGORII_PROFIT]
    assert coduri == ["venituri_contabile", "cheltuieli_contabile", "venituri_neimpozabile",
                      "deduceri_fiscale", "elemente_similare_venituri",
                      "elemente_similare_cheltuieli", "cheltuieli_nedeductibile",
                      "informatii_din_declaratie"]


def test_fiecare_categorie_isi_poarta_temeiul_si_campurile():
    for cod, eticheta, temei, campuri in _ref.CATEGORII_PROFIT:
        assert eticheta and temei, "%s fara eticheta sau temei" % cod
        assert campuri, "%s nu se compune din niciun camp D101 — ar iesi mereu zero" % cod
        assert all(c.startswith("P") for c in campuri), "%s: campuri care nu-s din D101" % cod


def test_cele_doua_variante_au_temeiuri_DIFERITE():
    """Erau doua registre, nu unul — chiar greseala de la care a pornit constructia. Un singur temei
    ar ascunde ca sunt doua acte, pentru doi contribuabili diferiti."""
    assert set(_ref.VARIANTE) == {"profit", "venituri_pf"}
    assert set(_ref.TEMEI) == set(_ref.VARIANTE)
    assert _ref.TEMEI["profit"].tip == "HG" and _ref.TEMEI["profit"].nr == 1
    # [R171] Varianta B are ȘASE citări, una per articol — nu una pe intervalul „1-6". Se cere
    # și numărul, și că articolele sunt exact 1..6: o listă scurtată ar trece pe „toate sunt OMFP".
    pf = _ref.TEMEI["venituri_pf"]
    assert [t.art for t in pf] == ["1", "2", "3", "4", "5", "6"], [t.art for t in pf]
    assert all(t.tip == "OMFP" and t.nr == 3254 for t in pf)
    # citarea din proza refuzurilor se DERIVA din ele, nu se scrie a doua oara
    assert _ref.TEMEI_PF_CITARE == "OMFP 3254/2017 art.1-6"


def test_elidarea_modelului_din_anexa1_e_CONSEMNATA_nu_ascunsa():
    """Lista de randuri a modelului variantei B lipseste din corpus — portalul pune `...`. Constatarea
    sta in modul ca DATE. Fara ea, cineva ar citi continutul construit din articolele 3-5 ca pe o
    transcriere a modelului oficial."""
    c = _ref.MODEL_ANEXA1_ELIDAT
    assert set(c) >= {"act", "unde", "ce_lipseste", "fisiere_verificate",
                      "aparitii_in_fisier", "de_unde_vine_continutul"}, (
        "constatarea nu mai e un obiect cu campuri — cine o citeste ar trebui sa extraga din proza")
    assert c["aparitii_in_fisier"] == 1, (
        "daca actul apare de mai multe ori in fisier, a doua aparitie trebuie CITITA inainte de a-l "
        "declara partial — chiar regula din METODA §30, prima instanta")
    assert len(c["fisiere_verificate"]) >= 2, (
        "elidarea s-a confruntat pe un singur fisier; se verifica si .txt si .html")


# ── 2. NICIUN AL DOILEA MOTOR ────────────────────────────────────────────────────────────────

def _e_formatare(n):
    """`"...%s" % x` e formatare de sir, nu aritmetica.

    Prins la PRIMA rulare a gardului, pe un `raise ValueError("... %s" % ...)` — deci in directia
    proasta: instrumentul tipa unde n-avea de ce. Se decide pe STRUCTURA, nu pe text: operandul
    stang e un sir literal, o concatenare de siruri literale, sau un f-string.
    """
    st = n.left
    while isinstance(st, ast.BinOp) and isinstance(st.op, ast.Add):
        st = st.left
    return (isinstance(st, ast.Constant) and isinstance(st.value, str)) or isinstance(st, ast.JoinedStr)


def _aritmetica(fn):
    """Liniile pe care se face aritmetica INTRE CIFRE. `sum(...)` nu intra: norma cere totalizarea."""
    out = []
    for n in ast.walk(fn):
        if not isinstance(n, ast.BinOp):
            continue
        if isinstance(n.op, ast.Mod) and _e_formatare(n):
            continue
        if isinstance(n.op, (ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Pow, ast.Mod)):
            out.append(getattr(n, "lineno", "?"))
    return out


def test_compunerea_nu_face_ARITMETICA_proprie_peste_campurile_D101():
    """Proba pe AST (METODA §23): in `compune_profit` nu exista nicio operatie aritmetica intre
    campuri, in afara de `sum` peste randurile unei categorii.

    Adica registrul ADUNA ce e in aceeasi categorie — ceea ce norma chiar cere („totalizarea") — dar
    nu scade, nu inmulteste si nu recombina. Orice `-`, `*` sau `/` aici ar fi inceputul unui al
    doilea calcul al aceluiasi an.
    """
    arb = ast.parse(io.open(_ref.__file__, encoding="utf-8").read())
    fn = next(f for f in ast.walk(arb)
              if isinstance(f, ast.FunctionDef) and f.name == "compune_profit")
    rele = _aritmetica(fn)
    assert not rele, (
        "`compune_profit` face aritmetica proprie (liniile %s). Registrul ar putea sa nu mai "
        "coincida cu declaratia pe care exista ca s-o justifice." % rele)


def test_calibrare_proba_aritmeticii_VEDE_o_recombinare():
    """CALIBRARE pe modul propriu de esec, pe cod sintetic."""
    def _rele(sursa):
        fn = next(f for f in ast.walk(ast.parse(sursa)) if isinstance(f, ast.FunctionDef))
        return _aritmetica(fn)

    assert _rele("def f(P):\n    return P['P10'] - P['P16']\n"), "nu vede o scadere"
    assert _rele("def f(P):\n    return P['P40'] * 16 / 100\n"), "nu vede o inmultire"
    assert _rele("def f(P):\n    return P['P40'] % P['P1']\n"), \
        "nu mai vede un MODULO real intre cifre — albirea formatarii a devenit prea lata"
    assert not _rele("def f(P):\n    return sum(P[k] for k in ('P1', 'P4'))\n"), \
        "da fals-pozitiv pe totalizarea pe care norma o CERE"
    assert not _rele("def f(x):\n    raise ValueError('nu merge %s' % x)\n"), \
        "da fals-pozitiv pe formatarea unui sir — instanta care l-a prins la prima rulare"
    assert not _rele("def f(x):\n    return ('a %s' 'b %s') % (x, x)\n"), \
        "da fals-pozitiv pe formatare cu siruri concatenate"


def test_campurile_folosite_exista_toate_in_D101():
    """Anti-vacuu pe maparea categoriilor: un `P` scris gresit ar da tacut zero, iar categoria ar
    iesi goala fara ca nimic sa tipe. Se confrunta cu multimea din `d101`, nu cu o lista scrisa aici."""
    from core import d101 as _d
    toate = set(_d._P_INTRARI) | set(_d._P_MAIN) | {"P40a", "P38a", "P39a", "P411", "P412"}
    folosite = {c for _cod, _e, _t, campuri in _ref.CATEGORII_PROFIT for c in campuri}
    lipsa = sorted(folosite - toate)
    assert not lipsa, (
        "campuri D101 inexistente in maparea categoriilor: %s — categoria lor ar iesi zero, tacut"
        % lipsa)


def test_compunerea_totalizeaza_pe_categorie():
    P = {"P1": 100, "P4": 20, "P2": 60, "P5": 5}
    c = _ref.compune_profit(P, "an", perioada="2026")
    s = {x["cod"]: x for x in c["sectiuni"]}
    assert s["venituri_contabile"]["total"] == 120
    assert s["cheltuieli_contabile"]["total"] == 65
    assert s["venituri_neimpozabile"]["total"] == 0, "categoriile fara valori ies zero, nu lipsesc"
    assert len(c["sectiuni"]) == 8, "o categorie a disparut din compunere"


def test_un_camp_lipsa_din_P_iese_zero_NU_arunca():
    """Registrul nu poate cadea fiindca o ajustare fiscala n-a fost facuta: zero e raspunsul corect
    pentru „nu s-a declarat nimic la randul asta"."""
    c = _ref.compune_profit({}, "an")
    assert all(x["total"] == 0 for x in c["sectiuni"])


# ── 3. TRIMESTRUL NU SE FABRICA ──────────────────────────────────────────────────────────────

def test_totalizarile_admise_sunt_cele_din_norma():
    assert set(_ref.TOTALIZARI) == {"trimestru", "an"}


def test_o_totalizare_inventata_e_refuzata():
    with pytest.raises(ValueError):
        _ref.compune_profit({}, "luna")


def test_trimestrul_NU_se_poate_totaliza_si_spune_de_ce():
    """Comportament, nu forma. Proba de dinainte cerea doar ca functia sa contina un `raise` —
    RED-proof-ul a aratat ca trecea verde si cand refuzul disparea, fiindca mai era unul acolo."""
    da, motiv = _ref.poate_totaliza("trimestru")
    assert da is False, "trimestrul se produce, desi formulele D101 sunt anuale"
    assert motiv and len(motiv) > 60, "refuzul nu spune DE CE"


def test_anul_se_poate_totaliza():
    """Anti-vacuu: fara asta, un `poate_totaliza` care refuza mereu ar trece proba de mai sus."""
    assert _ref.poate_totaliza("an") == (True, None)


def test_o_totalizare_din_afara_normei_e_refuzata_ALTFEL():
    """`ValueError` (nomenclator gresit) e alt lucru decat «nu se poate construi». Daca s-ar
    confunda, un an scris gresit ar arata ca o limita a aplicatiei."""
    with pytest.raises(ValueError):
        _ref.poate_totaliza("luna")


# ── 3b. REGULILE DE COMPLETARE ALE VARIANTEI PF (art. 1 alin. (1)-(3)) ───────────────────────
#
# N-aveau nicio proba pana cand RED-proof-ul a scos-o la iveala: mutatia care facea cheltuielile
# obligatorii si la norma de venit trecea VERDE, fiindca nimic nu le intreba.

def test_la_norma_de_venit_cheltuielile_NU_se_inscriu():
    """Art. 1 alin. (2): cine e pe norma de venit completeaza numai partea de venituri."""
    assert _ref.cheltuielile_se_inscriu(3, 1) == "nu"
    assert _ref.cheltuielile_se_inscriu(3, 7) == "nu"


def test_la_drepturi_de_proprietate_intelectuala_cheltuielile_sunt_OPTIONALE():
    """Art. 1 alin. (3): «pot completa numai partea referitoare la venituri» — deci nici obligatorii,
    nici interzise. A treia valoare, care s-ar pierde intr-un `bool`."""
    assert _ref.cheltuielile_se_inscriu(1, 3) == "optional"


def test_in_sistem_real_cheltuielile_SE_INSCRIU():
    assert _ref.cheltuielile_se_inscriu(1, 1) == "da"
    assert _ref.cheltuielile_se_inscriu(2, 2) == "da"


_PF = {"categorie": 1, "sursa_venit": "cabinet", "mod_venit_net": 1, "venit_brut": "120000.00"}


def test_in_sistem_real_cheltuielile_LIPSA_sunt_refuzate_dar_ZERO_trece():
    """Zero inseamna «nu s-au avut cheltuieli»; gol inseamna «nu s-a stabilit inca». Intr-un registru
    din care iese venitul net, cele doua duc la aceeasi cifra si la doua adevaruri diferite."""
    with pytest.raises(_ref.InregistrareIncompletaPF) as ex:
        _ref.valideaza_pf(dict(_PF))
    assert ex.value.camp == "cheltuieli_deductibile"
    assert ex.value.temei
    assert _ref.valideaza_pf(dict(_PF, cheltuieli_deductibile=0)) == "da"


def test_la_norma_de_venit_o_cheltuiala_data_e_REFUZATA():
    """Perechea inversa: nu doar ca nu se cere, dar nici nu se accepta — altfel registrul ar contine
    ceva ce norma spune ca nu se inscrie in el."""
    with pytest.raises(_ref.InregistrareIncompletaPF) as ex:
        _ref.valideaza_pf(dict(_PF, mod_venit_net=3, cheltuieli_deductibile="500"))
    assert ex.value.camp == "cheltuieli_deductibile"
    assert _ref.valideaza_pf(dict(_PF, mod_venit_net=3)) == "nu"


def test_categoria_si_modul_sunt_din_nomenclatoarele_D220():
    """Aceleasi ca in declaratie. Un nomenclator propriu ar clasifica altfel decat documentul pe care
    registrul il justifica."""
    assert set(_ref.CATEGORII_VENIT_PF) == {1, 2, 3, 4, 5, 6, 7}
    assert set(_ref.MOD_VENIT_NET) == {1, 2, 3}
    for rea, camp in ((dict(_PF, categorie=9), "categorie"),
                      (dict(_PF, mod_venit_net=4), "mod_venit_net")):
        with pytest.raises(_ref.InregistrareIncompletaPF) as ex:
            _ref.valideaza_pf(rea)
        assert ex.value.camp == camp


def test_venitul_net_poate_fi_NEGATIV():
    """«Pierdere neta anuala» e chiar termenul ordinului. Taiat la zero, ar sterge o informatie pe
    care declaratia o cere."""
    from decimal import Decimal
    assert _ref.venit_net("100", "130") == Decimal("-30")
    assert _ref.venit_net("100", None) == Decimal("100")


def test_trimestrul_se_REFUZA_cu_motiv_scris_nu_se_calculeaza_cu_formule_anuale():
    """Norma admite trimestrul; noi nu-l putem produce corect inca. Refuzul poarta motivul ca DATE,
    ca sa nu ajunga „nu se poate" fara de ce — iar `RegistruNeconstruibil` e alt lucru decat un
    registru gol."""
    assert _ref.TRIMESTRU_NECONSTRUIT
    src = io.open(_ref.__file__, encoding="utf-8").read()
    arb = ast.parse(src)
    fn = next(f for f in ast.walk(arb)
              if isinstance(f, ast.FunctionDef) and f.name == "registru_profit")
    ridica = [n for n in ast.walk(fn) if isinstance(n, ast.Raise)]
    assert ridica, "`registru_profit` nu refuza nimic — trimestrul ar iesi calculat cu formule anuale"


def test_neconstruibil_e_ALTCEVA_decat_gol():
    e = _ref.RegistruNeconstruibil("x", motiv="trimestru_neconstruit", temei="t")
    assert e.motiv and e.temei
    assert issubclass(_ref.RegistruNeconstruibil, ValueError)


# ── 4. PRODUCATORUL AJUNGE LA OM ─────────────────────────────────────────────────────────────

def test_exista_ruta_si_ecranul_care_livreaza_registrul():
    arb = ast.parse(io.open(os.path.join(_RAD, "main.py"), encoding="utf-8").read())
    cai = set()
    for f in ast.walk(arb):
        if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for d in f.decorator_list:
                if (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                        and isinstance(d.func.value, ast.Name) and d.func.value.id == "app"
                        and d.args and isinstance(d.args[0], ast.Constant)):
                    cai.add((d.func.attr, d.args[0].value))
    assert ("get", "/tenants/{tenant_id}/registru-evidenta-fiscala") in cai

    # Pe STRUCTURA, nu pe text (clichet 50 / METODA §23) — acelasi tipar ca la celelalte doua
    # registre: inventarul de ecrane e o MULTIME, verdictul de ancora e o clasificare.
    from core import test_harta_ecrane as _harta
    assert _harta._ecrane_din_cod() >= {"fa-regfiscal"}, "nu exista ecran care sa-l deschida"

    from scripts import scan_ancore_rute as _anc
    v = _anc.verdicte()
    for metoda in ("GET", "POST"):
        cheie = (metoda, "/tenants/{tenant_id}/registru-evidenta-fiscala")
        assert v.get(cheie) == "ACCEPTAT", "%s nu e ACCEPTAT: %r" % (metoda, v.get(cheie))
