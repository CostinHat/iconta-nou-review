# -*- coding: utf-8 -*-
"""GARDĂ: infrastructura de testare vizuală (frontend_test/vizual) nu poate dispărea tăcut.

Uneltele care verifică **REGULI**, sursa axe vandorizată și helperul de navigare TREBUIE să existe.
Dacă vreuna e ștearsă, suita pică — exact ce cere Regula 6 (unealta permanentă intră în verificator,
nu doar în documentație).

Introdusă 17.08.2026 împreună cu infra vizuală (marca de referință 66f50cd).

**[03.09.2026] BASELINE-URILE AU IEȘIT DIN GARDĂ, ȘI DIN REPO** — decizia de arhitectură a lui
Costin, verbatim: *„un baseline vizual e o probă care îmbătrânește prin construcție — se strică la
orice schimbare legitimă, iar atunci se regenerează ca să treacă și devine formalitate. Ce se
păstrează sunt regulile, care nu îmbătrânesc: contrast minim, nicio revărsare la 393 px, elementele
principale vizibile fără derulare. Alea au prins lucruri reale; capturile n-au prins nimic."*

Garda asta purta chiar mecanismul acela: cerea ca `baseline_scan.py` și cele cinci `baseline/*.png`
să existe. Acum cere **uneltele de regulă** — `axe_scan` (contrast, etichete, landmarks),
`mobil_scan` (revărsare la 393 px, ținte de atingere, ce dispare pe touch) și `interactiune_scan`
(comportament la apăsare, cuplat mecanic de `test_acoperire_vizuala`). *Ce s-a scos e comparația
pixel cu pixel; ce a rămas e tot ce a prins vreodată ceva.*

Rulează fără DB și fără browser — doar prezența fișierelor.
"""
import io
import os

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIZ = os.path.join(RADACINA, "frontend_test", "vizual")

ECRANE = ["import_mijloace_fixe", "vector_fiscal", "plan_conturi", "stat_plata", "declaratii"]

#: Uneltele care verifică o REGULĂ, nu o asemănare. Fiecare poartă, în dreptul ei, regula pe care o
#: apără — ca ștergerea vreuneia să spună ce se pierde, nu doar că lipsește un fișier.
UNELTE = {
    "axe_scan.py": "contrast minim, etichete, landmarks (WCAG AA)",
    "mobil_scan.py": "nicio revărsare la 393 px, ținte de atingere ≥24px, ce dispare pe touch",
    "interactiune_scan.py": "comportament la apăsare + revărsare la text lung",
    "nav_ecrane.py": "singurul loc de adevăr pentru ecranele parcurse",
}


def test_uneltele_de_REGULA_exista():
    for f, regula in sorted(UNELTE.items()):
        cale = os.path.join(VIZ, f)
        assert os.path.isfile(cale), (
            "unealtă vizuală lipsă: frontend_test/vizual/%s — cu ea se pierde regula «%s»"
            % (f, regula))


def test_mecanismul_de_COMPARATIE_PIXEL_nu_se_intoarce():
    """Direcția opusă, și e chiar decizia: baseline-urile **nu se reintroduc**.

    Fără garda asta, cineva (eu, peste o lună) ar putea reface `baseline_scan.py` fiindcă „lipsește
    ceva din infra vizuală" — iar motivul pentru care a fost scos nu e scris în cod, ci într-o
    decizie. *O regulă scrisă și nepăzită se pierde exact așa.* Motivul stă în
    `METODA_VERIFICARE.md` §27."""
    assert not os.path.isfile(os.path.join(VIZ, "baseline_scan.py")), (
        "`baseline_scan.py` a reapărut. Comparația pixel cu pixel a fost scoasă deliberat pe "
        "03.09.2026 — v. METODA_VERIFICARE.md §27. Dacă decizia s-a schimbat, se schimbă ACOLO întâi.")
    assert not os.path.isdir(os.path.join(VIZ, "baseline")), (
        "directorul `baseline/` a reapărut. Un baseline îmbătrânește prin construcție; ce se "
        "păstrează sunt regulile — v. METODA_VERIFICARE.md §27.")


def test_axe_vandorizat_prezent():
    axe = os.path.join(VIZ, "axe.min.js")
    assert os.path.isfile(axe), "axe.min.js lipsește — axe-core trebuie vandorizat offline"
    # marker de conținut: nu un fișier gol / placeholder
    cap = io.open(axe, encoding="utf-8").read(400)
    assert "axe" in cap and os.path.getsize(axe) > 100_000, "axe.min.js pare trunchiat/gol"


def test_cele_cinci_ecrane_declarate():
    """nav_ecrane.ECRANE = exact cele cinci ecrane problematice numite de Costin, în ordine."""
    sursa = io.open(os.path.join(VIZ, "nav_ecrane.py"), encoding="utf-8").read()
    for ecran in ECRANE:
        assert '"%s"' % ecran in sursa, "ecranul %s nu mai e în nav_ecrane.ECRANE" % ecran


# ── [LOTUL 10, 04.09.2026] Dependentele uneltelor, derivate — nu inca o lista ────────────────
#
# INSTANTA. `frontend_test/w_auth.py` — tokenul mintuit si navigarea la firma, de care atarna
# TOATA infrastructura de aici — a fost sters de pe disc pe 26.08, odata cu `b87dad49` („Scoate
# din urmarire cele 234 de artefacte maturate din greseala"). Timp de noua zile **24 de fisiere**,
# printre ele toate cele patru unelte de mai sus, s-au importat dintr-un `.pyc` de 4,6 KB ramas in
# `__pycache__`. Nimic n-a devenit rosu: Python incarca bytecode fara sa-i ceara sursa. Un
# `find -name __pycache__ -delete` — curatenia obisnuita — ar fi oprit tacut tot.
#
# Garda de deasupra n-a vazut-o fiindca cerea fisiere DINTR-O LISTA, iar `w_auth` nu era in ea si
# nici macar in acelasi director. *O lista scrisa de mine vede exact ce mi-am amintit sa scriu.*
# Asta deriva ce trebuie sa existe din chiar `import`-urile uneltelor: ce cheama o unealta trebuie
# sa se poata citi.
import ast

#: Module care vin din afara (stdlib sau instalate) — nu se cauta ca fisier in repo.
_DIN_AFARA = {"os", "sys", "io", "json", "re", "glob", "time", "math", "subprocess", "hashlib",
              "datetime", "collections", "urllib", "traceback", "pathlib", "shutil", "tempfile",
              "playwright", "pytest", "psycopg2", "PIL", "requests"}

#: Unde poate trai o sursa importata de o unealta vizuala.
_CAI = [os.path.join(RADACINA, "frontend_test", "vizual"),
        os.path.join(RADACINA, "frontend_test"),
        RADACINA]


def _importuri(cale):
    """Numele de modul de nivel inalt importate de fisier."""
    arbore = ast.parse(io.open(cale, encoding="utf-8").read())
    nume = set()
    for n in ast.walk(arbore):
        if isinstance(n, ast.Import):
            nume |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            nume.add(n.module.split(".")[0])
    return nume


def test_dependentele_uneltelor_exista_ca_sursa():
    lipsa = []
    for unealta in UNELTE:
        cale = os.path.join(VIZ, unealta)
        for modul in sorted(_importuri(cale)):
            if modul in _DIN_AFARA:
                continue
            if any(os.path.isfile(os.path.join(c, modul + ".py")) for c in _CAI):
                continue
            if os.path.isdir(os.path.join(RADACINA, modul)):   # pachet al repo-ului (`core`)
                continue
            lipsa.append("%s importa `%s`, care n-are sursa nicaieri" % (unealta, modul))
    assert not lipsa, (
        "unelte vizuale care se sprijina pe module fara sursa:\n  " + "\n  ".join(lipsa)
        + "\n\nDaca modulul mai exista doar ca `.pyc` in `__pycache__`, uneltele merg pana la "
          "prima curatenie, si se opresc apoi fara ca nimic sa devina rosu.")


def test_garda_asta_chiar_are_ce_verifica():
    """Anti-vacuu: daca `_importuri` n-ar gasi nimic, testul de sus ar trece despre nimic."""
    total = set()
    for unealta in UNELTE:
        total |= _importuri(os.path.join(VIZ, unealta))
    assert "w_auth" in total, (
        "niciuna dintre unelte nu mai importa `w_auth` — ori s-a schimbat arhitectura (si atunci "
        "se scrie aici de ce), ori garda se uita in fisierele gresite")
    assert len(total) >= 6, "prea putine importuri gasite (%d) — parserul nu vede fisierele" % len(total)
