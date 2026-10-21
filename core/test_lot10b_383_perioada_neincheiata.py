# -*- coding: utf-8 -*-
"""[lotul 10, deficiența 383 (grav), comanda Costin 10.2 pct.1, verbatim în DECIZII] „la F1, alegând manual luna octombrie, D300 pe 10/2026
se generează pe 20.10 și «Pune în De depus» e oferit. O declarație pe o perioadă neîncheiată se refuză la generare, cu motivul scris, la toate
declarațiile.”

Regula e una (`coada_api.perioada_neincheiata`): dispecerul o aplică PRIMUL (`declaratii_api.refuza_perioada_neincheiata` — drumul comun
al pasului 2 din Declarații, al „Trimite în coadă”, al „Generează din nou”, al reluării după validarea notelor și al API-ului), generatorul
bilanțului o aplică pe drumul ecranului Bilanț (`bilant_api.cere_an_incheiat`), lista cozii și depunerea o aplică în continuare (lotul 9).
Excepțiile (`coada_api.DECLARATII_IN_CURSUL_PERIOADEI`) au fiecare temeiul citat, căutat aici în `anaf_surse/`.
Proba pe ecran: `frontend_test/e2e/e2e_lot10b_declaratii.py::test_def_383_…`."""
import ast
import datetime as _dt
import inspect
import os
import re
import textwrap
import unicodedata

import pytest

from core import bilant_api, coada_api, declaratii_api
from core.erori import RefuzGenerare

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AZI = _dt.date(2026, 10, 20)   # ziua retestului (comanda 10.2: „D300 pe 10/2026 se generează pe 20.10”)


@pytest.fixture
def azi_20_10(monkeypatch):
    from core import common
    monkeypatch.setattr(common, "azi_ro", lambda acum=None: AZI)


def _corp_perioada_curenta(tip):
    """Corpul cererii pe perioada ÎN CURS la 20.10.2026, după periodicitatea tipului."""
    per = declaratii_api.periodicitate(tip)
    return {"lunar": {"an": 2026, "luna": 10}, "trimestrial": {"an": 2026, "trim": 4},
            "semestrial": {"an": 2026, "luna": 12}, "anual": {"an": 2026}}[per]


def test_d300_pe_luna_in_curs_se_refuza_la_generare_cu_motivul_scris(azi_20_10):
    """Cazul din comandă: D300 pe 10/2026, generat pe 20.10.2026. MUTAȚIA: `refuza_perioada_neincheiata(tip, body)` scos din
    `declaratii_api.genereaza` -> generarea trece de poartă (conn=None -> AttributeError, nu refuzul) -> ROȘU."""
    with pytest.raises(RefuzGenerare) as e:
        declaratii_api.genereaza(None, "nicio_schema", "d300", {"an": 2026, "luna": 10})
    # comanda 10.2 pct.1: „se refuză la generare, cu motivul scris”
    assert str(e.value) == ("Perioada 10/2026 nu s-a încheiat: declarația se generează și se depune după 31.10.2026, când toate "
                            "operațiunile perioadei sunt înregistrate."), str(e.value)


@pytest.mark.parametrize("tip", sorted(t for t in dict(declaratii_api.DECLARATII, **declaratii_api.SITUATII_FINANCIARE)
                                       if t not in coada_api.DECLARATII_IN_CURSUL_PERIOADEI))
def test_la_toate_declaratiile_perioada_in_curs_se_refuza(tip, azi_20_10):
    """„la toate declarațiile” (comanda 10.2 pct.1): fiecare tip, pe perioada lui în curs (luna, trimestrul, semestrul, anul), e refuzat de
    dispecer ÎNAINTE de orice citire (conn=None) și înaintea formularului manual (corp fără `manual`)."""
    with pytest.raises(RefuzGenerare, match=r"nu s-a încheiat: declarația se generează și se depune după 31\.(10|12)\.2026"):
        declaratii_api.genereaza(None, "nicio_schema", tip, _corp_perioada_curenta(tip))


def test_CALIBRARE_perioada_incheiata_trece_de_poarta(azi_20_10):
    """Aceeași cerere pe 09/2026 (încheiată pe 30.09) nu e refuzată de poartă: dispecerul merge mai departe (aici, la citirea firmei, pe
    conn=None). Garda nu refuză orice."""
    declaratii_api.refuza_perioada_neincheiata("d300", {"an": 2026, "luna": 9})
    with pytest.raises(AttributeError):
        declaratii_api.genereaza(None, "nicio_schema", "d300", {"an": 2026, "luna": 9})


def test_tipul_anual_nu_se_scurteaza_cu_o_luna_trimisa_pe_api(azi_20_10):
    """La un tip anual perioada e anul: o lună trimisă pe API (D101 cu luna 3) nu face din anul 2026 o perioadă încheiată.
    MUTAȚIA: ramura `periodicitate(tip) == "anual"` scoasă din `perioada_neincheiata` -> 03/2026 „încheiată” -> ROȘU."""
    assert coada_api.perioada_neincheiata(2026, 3, tip="d101", azi=AZI) == (
        "Anul 2026 nu s-a încheiat: declarația se generează și se depune după 31.12.2026, când toate operațiunile perioadei sunt "
        "înregistrate.")


def test_d318_perioada_de_rambursare_din_formular():
    """D318: perioada e cea de rambursare din formular (DUK regula R5.2: „annual=0 => lunaInceput<>1 sau lunaSfarsit<>12”). 01–03/2026
    s-a încheiat pe 31.03 -> nu se refuză în octombrie; 07–12/2026 se refuză până după 31.12."""
    assert coada_api.perioada_neincheiata(2026, None, tip="d318", azi=AZI,
                                          manual={"an": 2026, "luna_inceput": 1, "luna_sfarsit": 3}) is None
    assert coada_api.perioada_neincheiata(2026, None, tip="d318", azi=AZI,
                                          manual={"an": 2026, "luna_inceput": 7, "luna_sfarsit": 12}).startswith("Perioada 12/2026")


def test_forma_gresita_ajunge_la_refuzul_ei_de_forma():
    """O lună în afara intervalului nu e „perioadă neîncheiată”: poarta o lasă refuzului de formă (`valideaza_cerere`), fără excepție de
    calendar (luna 13 nu trece prin `monthrange`)."""
    declaratii_api.refuza_perioada_neincheiata("d300", {"an": 2026, "luna": 13})
    declaratii_api.refuza_perioada_neincheiata("d300", {"an": "2026", "luna": 10})


def test_bilantul_pe_anul_in_curs_se_refuza_si_pe_ecranul_bilant(azi_20_10):
    """Ecranul Bilanț generează pe drumul lui (`uc_tenants.s1005_*` / `s1003_*` -> `bilant_api.genereaza*`), nu prin dispecer: refuzul stă
    în generator, înainte de orice citire. MUTAȚIA: `cere_an_incheiat(an, "s1005")` scos din `bilant_api.genereaza` -> ROȘU."""
    for gen in (bilant_api.genereaza, bilant_api.genereaza_s1003):
        with pytest.raises(RefuzGenerare, match="Anul 2026 nu s-a încheiat"):
            gen(None, "nicio_schema", 2026)


# ── excepțiile: numai cu temei, iar temeiul e în corpus ──────────────────────────────────────────────────────────────────────────────────
_SURSA_TEMEI = {
    "d213": "anaf_surse/opanaf_216_2023_formular_213_instrainare_pachet_control_terenuri_agricole_extravilan.txt",
    "d214": "anaf_surse/ordin_216_2023__baza_265344.html",
    "d169": "anaf_surse/legea_129_2019.html",
    "d169n": "anaf_surse/legea_129_2019.html",
    "d220": "anaf_surse/opanaf_184_2013.txt",
    "d223": "anaf_surse/opanaf_184_2013.txt",
}


def _norm(t):
    t = re.sub(r"<[^>]+>", " ", t)
    t = unicodedata.normalize("NFC", t).replace("ş", "ș").replace("ţ", "ț").replace("Ş", "Ș").replace("Ţ", "Ț")
    t = t.replace("‐", "-").replace("«", "„").replace("»", "”").replace("“", "”").replace("&quot;", '"')
    return re.sub(r"\s+", " ", t)


@pytest.mark.parametrize("tip", sorted(coada_api.DECLARATII_IN_CURSUL_PERIOADEI))
def test_fiecare_exceptie_are_temeiul_citat_din_corpus(tip):
    """CLAUDE.md §3: „UNDE NU EXISTA TEMEI LEGAL, NU SE CONSTRUIESTE.” Fiecare fragment citat („…”, despărțit la „[...]”) al excepției se
    regăsește, literă cu literă (diacriticele și spațiile normalizate), în sursa oficială din `anaf_surse/`. O excepție nouă fără sursă
    în corpus -> ROȘU."""
    assert tip in _SURSA_TEMEI, "excepție fără sursă în corpus: %s" % tip
    import html as _h
    sursa = _norm(_h.unescape(open(os.path.join(RAD, _SURSA_TEMEI[tip]), encoding="utf-8", errors="ignore").read()))
    citate = re.findall(r"„(.+?)”", _norm(coada_api.DECLARATII_IN_CURSUL_PERIOADEI[tip]))
    assert citate, tip
    for c in citate:
        for fragment in (f.strip(" .,") for f in re.split(r"\[\.\.\.\]", c.replace("«", "„").replace("»", "”"))):
            fragment = re.sub(r"[„”]", "", fragment)
            assert fragment and re.sub(r"[„”\"]", "", fragment) in re.sub(r"[„”\"]", "", sursa), (tip, fragment)


def test_exceptiile_nu_au_perioada_neincheiata():
    """D213 pe anul în curs (înstrăinarea de luna asta, depusă în 10 zile): nu se refuză. MUTAȚIA: verificarea `tip in
    DECLARATII_IN_CURSUL_PERIOADEI` scoasă -> ROȘU."""
    for tip in coada_api.DECLARATII_IN_CURSUL_PERIOADEI:
        assert coada_api.perioada_neincheiata(2026, None, tip=tip, azi=AZI) is None, tip


# ── toate drumurile de generare trec prin poartă ────────────────────────────────────────────────────────────────────────────────────────
def _apeluri(f):
    """Numele apelate în corpul funcției (`a.b(...)` -> „a.b”, `b(...)` -> „b”), din arborele sintactic."""
    out = set()
    for n in ast.walk(ast.parse(textwrap.dedent(inspect.getsource(f)))):
        if isinstance(n, ast.Call):
            if isinstance(n.func, ast.Name):
                out.add(n.func.id)
            elif isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name):
                out.add("%s.%s" % (n.func.value.id, n.func.attr))
    return out


def test_drumurile_declaratiilor_trec_prin_dispecer():
    """Pasul 2 din Declarații (`/valideaza`), generarea (`/declaratii/{tip}`) și intrarea în coadă (care servește și „Generează din nou” și
    reluarea după validarea notelor) cheamă toate dispecerul, iar dispecerul cheamă poarta înaintea oricărui alt pas."""
    from core import uc_coada, uc_declaratii
    drumuri = (uc_declaratii.declaratie_valideaza, uc_declaratii.declaratie_genereaza, uc_coada.coada_adauga)
    # operator de mulțime pe numele apelate (AST), nu sub-șir; lista ocolitorilor comparată întreagă, nu iterată
    assert [f.__name__ for f in drumuri if not {"declaratii_api.genereaza"} <= _apeluri(f)] == []
    assert {"coada_adauga"} <= _apeluri(uc_coada.coada_regenereaza) and {"coada_adauga"} <= _apeluri(uc_coada.reia_declaratiile_in_asteptare)
    corp = ast.parse(textwrap.dedent(inspect.getsource(declaratii_api.genereaza))).body[0].body
    primul = [s for s in corp if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))][0]
    assert isinstance(primul, ast.Expr) and getattr(primul.value.func, "id", None) == "refuza_perioada_neincheiata", ast.dump(primul)[:200]
    assert {"cere_an_incheiat"} <= _apeluri(bilant_api.genereaza) and {"cere_an_incheiat"} <= _apeluri(bilant_api.genereaza_s1003)


#: Cine cheamă un generator de declarație DIRECT (ocolind dispecerul) și de ce nu e o generare de declarație de depus. Un drum nou care
#: cheamă direct `<modul>.genereaza(` fără să fie aici -> ROȘU: se trece prin dispecer sau se adaugă aici, cu motivul.
APELURI_DIRECTE_PERMISE = {
    "core/declaratii_api.py": "dispecerul însuși (adaptoarele)",
    "core/uc_tenants.py": "ecranul Bilanț: `bilant_api.genereaza*`, cu poarta în generator (`cere_an_incheiat`)",
    "core/control_incrucisat.py": "a doua cale a controlului încrucișat (D112 / D300 recalculate, nu depuse)",
    "core/salarii_contare.py": "nota statului de plată confruntată cu D112 (nu depune)",
    "core/stat_plata_api.py": "reținerile indemnizației din totalurile D112 (nu depune)",
    "core/registru_evidenta_fiscala.py": "registrul de evidență fiscală (rândurile D101, nu depune)",
    "core/db.py": "exemplu în docstringul lui `get_conn`",
}


def test_niciun_drum_nou_de_generare_nu_ocoleste_poarta():
    """Gard de perimetru: fișierele din `core/` (în afara generatoarelor și a testelor) care cheamă `<dNNN|bilant_api>.genereaza(` sunt exact
    cele de mai sus, fiecare cu motivul. MUTAȚIA: un apel nou `d300.genereaza(` într-un use-case -> ROȘU."""
    gasite = set()
    for f in sorted(os.listdir(os.path.join(RAD, "core"))):
        if not f.endswith(".py") or f.startswith("test_") or re.fullmatch(r"d\d+[a-z]*(_\w+)?\.py", f):
            continue
        txt = open(os.path.join(RAD, "core", f), encoding="utf-8").read()
        if re.search(r"\b(_?d\d{3}[a-z]?|_d|_ba|bilant_api)\.genereaza(_s1003)?\(", txt):
            gasite.add("core/" + f)
    assert gasite == set(APELURI_DIRECTE_PERMISE), sorted(gasite ^ set(APELURI_DIRECTE_PERMISE))
