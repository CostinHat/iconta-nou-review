# -*- coding: utf-8 -*-
"""GARDĂ (03.09.2026): **un fișier imagine nu mai intră în repo ca probă vizuală**, și **niciun cod
nu compară două imagini**.

**Cerută de Costin, în chiar tura în care §27 s-a rescris**, verbatim: *„Adaugă la curățenie: o gardă
care refuză introducerea de fișiere imagine ca probă vizuală. Fără ea, §27 rescris rămâne o intenție
și capturile revin la prima tură de interfață. Capturile pentru diagnostic, în timpul unei ture,
rămân permise — dar nu se salvează și nu devin bază de comparație."*

**DE CE E NECESARĂ, și de ce tocmai acum.** `METODA_VERIFICARE.md` §27 a scos comparația pixel cu
pixel prin decizie de arhitectură. Un document scos nu se apără singur: `test_infra_vizuala` cere ca
**unealta** să nu reapară, dar nimic n-ar fi oprit **capturile** să reintre una câte una, la prima
tură de interfață — fiecare părând, în momentul ei, o probă utilă. *Tiparul e cunoscut în registrul
ăsta sub numele lui: o regulă scrisă și nepăzită nu e o regulă.*

**CELE DOUĂ INTERDICȚII, și granița dintre ele:**

| ce | verdict |
|---|---|
| capturi făcute **în timpul** unei ture, ca să te uiți la ele | **permis** — așa se găsesc defecte apăsând |
| aceleași capturi **salvate în repo** | **refuzat** — aici cade garda |
| cod care compară două imagini (bază de comparație) | **refuzat** — a doua gardă de mai jos |

*Granița nu e „ce e o probă", care e o judecată, ci **„intră în index?"**, care e mecanic.*

**CLICHET, în ambele direcții** (METODA §22): mulțimea imaginilor din index e **pinată**. Una nouă
pică — dar și una **dispărută** pică, cerând să fie scoasă din listă. *Un clichet care păstrează
morții devine, în câteva luni, o listă despre care nu mai știi ce e adevărat.*

Rulează fără DB și fără browser: citește **indexul git** și codul de pe disc.
"""
import ast
import io
import os
import subprocess

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Extensiile socotite „fișier imagine". `.svg` intră: e vectorial, dar tot imagine — iar dacă ar
#: lipsi, o captură convertită ar ocoli garda fără să mintă nimeni.
IMAGINI = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".ico", ".tiff", ".avif", ".svg")

#: **PRODUS** — imagini care fac parte din aplicația livrată, nu din verificarea ei. Nu sunt probe:
#: le vede utilizatorul. O imagine nouă aici e legitimă, dar se **înregistrează** aici, cu ce e.
PRODUS = {
    "static/favicon.svg": "pictograma din fila browserului",
    "static/icon-192.png": "pictogramă PWA 192px (manifest)",
    "static/icon-512.png": "pictogramă PWA 512px (manifest)",
    "static/logo_login.png": "sigla de pe ecranul de autentificare",
    "static/logo_simbol.png": "simbolul din bara de sus",
}

#: **DATE DE FIRMĂ** — imagini încărcate prin aplicație, ajunse în index. *Nu sunt probe și nu sunt
#: produs: sunt date. Le las pinate, ca să nu crească tăcut, dar faptul că sunt comise e o
#: constatare în sine, nu o stare pe care s-o aprob.*
DATE_INCARCATE = {
    "static/raportari/r2_m3_c7df89e4.png": "imagine de raportare încărcată prin aplicație",
    "static/raportari/r4_m6_eefe6d93.png": "imagine de raportare încărcată prin aplicație",
}

#: **PROBE PINATE** — cele 30 de capturi rămase în index după curățarea din 03.09.2026. Sunt urme ale
#: unor stări care **nu mai există** (firma ștearsă, cabinetul dus), deci nu se pot reface rulând un
#: instrument — singura clasă pe care §27 o lasă în repo. **Lista nu are voie să crească.** Fiecare e
#: numită în `CONFORMITATE.md`, iar `core/test_capturi_numite.py` păzește numirea.
PROBE_PINATE = {
    "frontend_test/aa_1_alegere_denumire.png",
    "frontend_test/aa_1b_alegere_ANAF.png",
    "frontend_test/aa_2_dezactivare_fara_evidenta.png",
    "frontend_test/aa_3_scoatere_definitiva.png",
    "frontend_test/aa_4_dezactivare_cu_evidenta.png",
    "frontend_test/cc_scoatere_banner.png",
    "frontend_test/ff_scoatere_x_repaus.png",
    "frontend_test/ii_scoatere_375px.png",
    "frontend_test/ii_scoatere_375px_intreg.png",
    "frontend_test/ll_scoatere_375px_latit.png",
    "frontend_test/po_0_inainte_coada.png",
    "frontend_test/po_0_inainte_dashboard.png",
    "frontend_test/po_1_suspendat_coada.png",
    "frontend_test/po_1_suspendat_dashboard.png",
    "frontend_test/po_1_suspendat_mobil.png",
    "frontend_test/po_2_efectiv_coada.png",
    "frontend_test/po_2_efectiv_dashboard.png",
    "frontend_test/po_2_efectiv_mobil.png",
    "frontend_test/r118_desktop_cu_arborele_stricat.png",
    "frontend_test/r126_3_pas_confirmare.png",
    "frontend_test/r126_4_gol_refuzat.png",
    "frontend_test/r126_6_confirmat_depus.png",
    "frontend_test/r126_7_mobil.png",
    "frontend_test/r126_8_depunere_simpla.png",
    "frontend_test/r126_9_a_doua_apasare.png",
    "frontend_test/r129_anunt_fara_intrerupere.png",
    "frontend_test/r129_mobil.png",
    "frontend_test/w_date_firma_o_caseta.png",
    "frontend_test/w_divergenta_caseta.png",
    "frontend_test/w_divergenta_vie.png",
}

ADMISE = PROBE_PINATE | set(PRODUS) | set(DATE_INCARCATE)

#: Module care compară/diferențiază imagini. **Prezența unui import de-astea E mecanismul**, oricum
#: s-ar numi funcția care îl folosește — de-aia garda se uită la import, nu la nume de funcție.
MODULE_DE_COMPARATIE = {
    "PIL": "Pillow — `ImageChops.difference` e chiar comparația pixel cu pixel",
    "pixelmatch": "bibliotecă dedicată de diff de imagini",
    "imagehash": "amprentă perceptuală de imagine = comparație de imagini cu alt nume",
    "cv2": "OpenCV — `absdiff` pe capturi",
    "skimage": "scikit-image — `structural_similarity` pe capturi",
}

#: Echivalentele din lumea JS. **Aici nu se poate pe AST**: n-avem parser de JS în suită, iar
#: `node --check` spune doar dacă fișierul e valid, nu ce cheamă. *Motivul stă scris lângă gardă,
#: cum cere METODA §23.* Riscul acceptat e mic: sunt nume de API, nu cuvinte de proză.
API_JS_DE_COMPARATIE = ("toHaveScreenshot", "toMatchImageSnapshot", "pixelmatch")


def _index_git():
    """Ce e URMĂRIT sau STAGIAT — adică exact ce ar intra în commit. Nu ce e pe disc."""
    r = subprocess.run(["git", "ls-files", "-z"], cwd=RAD, capture_output=True, timeout=60)
    return [x.decode("utf-8") for x in r.stdout.split(b"\0") if x]


def imagini_din(numite):
    """Pură, ca să poată fi calibrată pe o listă fabricată, nu doar pe repo-ul de azi."""
    return {x for x in numite if os.path.splitext(x)[1].lower() in IMAGINI}


def _fisiere(ext):
    afara = ("venv", ".git", "__pycache__", "node_modules")
    for rad, dirs, fisiere in os.walk(RAD):
        dirs[:] = [d for d in dirs if d not in afara]
        for f in fisiere:
            if f.endswith(ext):
                yield os.path.join(rad, f)


def urme_de_comparatie_py(sursa):
    """Modulele de diff de imagini importate de o sursă Python. **Structural, pe AST** — un
    `# import PIL` din comentariu nu declanșează, iar `from PIL.ImageChops import difference` da."""
    try:
        arbore = ast.parse(sursa)
    except SyntaxError:
        return set()
    gasite = set()
    for nod in ast.walk(arbore):
        if isinstance(nod, ast.Import):
            for a in nod.names:
                radacina = a.name.split(".")[0]
                if radacina in MODULE_DE_COMPARATIE:
                    gasite.add(radacina)
        elif isinstance(nod, ast.ImportFrom) and nod.module:
            radacina = nod.module.split(".")[0]
            if radacina in MODULE_DE_COMPARATIE:
                gasite.add(radacina)
    return gasite


# ── 1. nicio imagine nouă în index ────────────────────────────────────────────────────────────
def test_nicio_imagine_noua_nu_intra_in_repo():
    """Miezul. *„O gardă care refuză introducerea de fișiere imagine ca probă vizuală."*"""
    gasite = imagini_din(_index_git())
    noi = sorted(gasite - ADMISE)
    assert not noi, (
        "imagini NOI în index:\n  " + "\n  ".join(noi)
        + "\n\nMETODA_VERIFICARE.md §27: verificarea vizuală se face pe REGULI (contrast, revărsare "
          "la 393 px, elemente vizibile fără derulare), nu pe asemănare cu o captură. O captură "
          "făcută ca să te uiți la ea în timpul turei e permisă — SALVATĂ în repo, nu.\n"
        "Dacă e o imagine de PRODUS (ceva ce vede utilizatorul), înregistreaz-o în `PRODUS`, cu ce e.\n"
        "Dacă e o probă a unei stări care NU se mai poate reface, e excepția din §27: se adaugă în "
        "`PROBE_PINATE` **și** se numește în CONFORMITATE.md, la restanța pe care o probează.")


def test_clichetul_nu_pastreaza_imagini_moarte():
    """Direcția opusă, cerută de METODA §22: o listă pinată care nu observă că un fișier a dispărut
    devine, în câteva luni, o afirmație despre o lume pe care n-o mai vede."""
    gasite = imagini_din(_index_git())
    disparute = sorted(ADMISE - gasite)
    assert not disparute, (
        "pinate, dar nu mai sunt în index:\n  " + "\n  ".join(disparute)
        + "\n\nScoate-le din lista din `core/test_fara_probe_imagine.py` — și, dacă erau probe, "
          "scoate-le și din CONFORMITATE.md, ca registrul să nu numească fișiere inexistente.")


def test_gardul_chiar_vede_indexul():
    """Anti-vacuu. Dacă `git ls-files` ar întoarce gol (director greșit, git lipsă), amândouă
    aserțiunile de sus ar trece pe mulțimea vidă și n-ar dovedi nimic."""
    numite = _index_git()
    assert len(numite) > 300, (
        "[anti-vacuu] indexul git pare gol (%d fișiere) — garda s-ar uita la o lume pe care n-o "
        "vede" % len(numite))
    assert imagini_din(numite), "[anti-vacuu] nicio imagine găsită în index — filtrul pe extensie s-a rupt?"


def test_clichetul_prinde_o_imagine_noua_SI_una_disparuta():
    """Calibrare pe funcția pură, în amândouă direcțiile — nu pe repo-ul de azi, care e verde.

    *Un instrument probat doar pe starea în care e verde nu dovedește că poate deveni roșu.*"""
    noua = "frontend_test/proba_noua.png"
    fabricat = sorted(ADMISE) + [noua, "core/coada_api.py"]
    # Egalitate de MULȚIMI, nu apartenență: `x in y` ar trece și dacă filtrul ar lăsa să intre pe
    # lângă captură și fișierul `.py` — adică exact greșeala din direcția opusă. METODA §23.
    assert imagini_din(fabricat) == ADMISE | {noua}, (
        "filtrul pe extensie nu întoarce exact imaginile: ori nu vede captura nouă, ori a luat "
        "și `core/coada_api.py` drept imagine")
    assert imagini_din(fabricat) - ADMISE == {noua}, "o captură nouă NU e văzută ca nouă"
    fara_una = set(sorted(ADMISE)[1:])
    assert ADMISE - fara_una, "direcția «a dispărut una» nu se aprinde"


# ── 2. niciun mecanism de comparație de imagini ───────────────────────────────────────────────
def test_niciun_cod_nu_compara_doua_imagini():
    """*„… și nu devin bază de comparație."* Interdicția nu e pe fișiere, e pe **mecanism**."""
    vinovate = []
    vazute = 0
    for cale in _fisiere(".py"):
        vazute += 1
        gasite = urme_de_comparatie_py(io.open(cale, encoding="utf-8", errors="replace").read())
        for m in sorted(gasite):
            vinovate.append("%s: importă `%s` — %s"
                            % (os.path.relpath(cale, RAD), m, MODULE_DE_COMPARATIE[m]))
    assert vazute > 100, "[anti-vacuu] doar %d fișiere .py parcurse — scanul s-a orbit" % vazute
    assert not vinovate, (
        "cod care compară imagini:\n  " + "\n  ".join(vinovate)
        + "\n\nMETODA §27: baseline-ul vizual a fost scos pe 03.09.2026 fiindcă îmbătrânește prin "
          "construcție. Dacă decizia s-a schimbat, se schimbă ACOLO întâi.")


def test_niciun_JS_nu_cere_captura_de_referinta():
    vinovate = []
    vazute = 0
    for cale in _fisiere(".js"):
        vazute += 1
        sursa = io.open(cale, encoding="utf-8", errors="replace").read()
        for api in API_JS_DE_COMPARATIE:
            if api in sursa:
                vinovate.append("%s: `%s`" % (os.path.relpath(cale, RAD), api))
    assert vazute > 20, "[anti-vacuu] doar %d fișiere .js parcurse — scanul s-a orbit" % vazute
    assert not vinovate, "JS care cere captură de referință:\n  " + "\n  ".join(vinovate)


def test_scanul_de_mecanism_prinde_mutatia():
    """RED-proof pe propriul mod de eșec: sursele fabricate de mai jos TREBUIE să fie prinse, iar
    cele nevinovate TREBUIE să nu fie. *Calibrarea pozitivă singură n-ar arăta decât că funcția
    întoarce ceva.*"""
    assert urme_de_comparatie_py("from PIL import ImageChops\n") == {"PIL"}
    assert urme_de_comparatie_py("import cv2\n") == {"cv2"}
    assert urme_de_comparatie_py("from skimage.metrics import structural_similarity\n") == {"skimage"}
    assert urme_de_comparatie_py("import PIL.ImageChops as ic\n") == {"PIL"}
    # nevinovate: comentariu, șir, și un import cu nume asemănător
    assert urme_de_comparatie_py("# from PIL import Image\n") == set()
    assert urme_de_comparatie_py("x = 'import cv2'\n") == set()
    assert urme_de_comparatie_py("import pillow_heif\n") == set()
    # sursă stricată: nu explodează, doar nu afirmă nimic
    assert urme_de_comparatie_py("def (:\n") == set()
