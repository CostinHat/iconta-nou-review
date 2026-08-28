# -*- coding: utf-8 -*-
"""GARD [HH, 28.08.2026]: o captură comisă fără proprietar în registru pică poarta.

REGULA pe care o păzește (`METODA_VERIFICARE.md` §27, scrisă azi): capturile de ecran sunt de **două**
feluri, iar numai unul intră în repo.
  - **baseline** — regenerabilă cu un instrument, referință **locală**; rămâne afară (`.gitignore`,
    decizia lui Costin din 26.08.2026);
  - **probă** — dovada că un lucru s-a întâmplat o dată, pe o stare care **nu mai există**; intră
    **selectiv**, și se **numește în `CONFORMITATE.md`, la restanța pe care o probează**.

DE CE E NEVOIE DE GARD, și nu ajunge principiul. Convenția spunea *„o captură fără proprietar în
registru e, prin construcție, suspectă"* — dar suspiciunea nu se autoverifică. Prima rulare a
scanului ăstuia, în ziua în care regula s-a scris, a găsit **16 din 17** capturi comise **nenumite**:
opt de ieri, pomenite doar printr-un **glob** (`frontend_test/aa_*.png`), și opt de pe 20.08, de
dinainte ca regula să existe. Adică regula era încălcată **de propriul ei autor, în ziua în care a
scris-o**, iar fără gard n-ar fi aflat nimeni.

CE FACE IMPOSIBIL: o captură nouă comisă fără ca numele ei de fișier să apară în `CONFORMITATE.md`.

CE NU FACE, declarat:
  - **nu judecă dacă e baseline sau probă.** Distincția e o judecată (METODA §27); gardul cere doar
    ca fiecare captură comisă să aibă un **proprietar** scris. O captură-baseline comisă din greșeală
    trece dacă cineva îi scrie numele în registru — dar atunci a scris-o cineva, deliberat.
  - **nu verifică dacă mențiunea e ADEVĂRATĂ** — că textul de lângă nume descrie chiar captura aia.
    Aia rămâne citire.
  - **nu se aplică retroactiv.** Capturile de dinainte de regulă stau într-o listă declarată, care
    **nu are voie să crească**.
"""
import io
import os
import subprocess

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REGISTRU = os.path.join(_RAD, "CONFORMITATE.md")

# Capturi comise ÎNAINTE ca regula să existe (commit `9d963d6`, 20.08.2026 — patru-ochi: indicatorul
# nu mai minte). Regula s-a scris pe 28.08, iar decizia lui Costin a fost explicită: *„nu adăuga alte
# capturi retroactiv — regula se aplică de-acum înainte."* A le numi acum în registru ar însemna să
# scriu, opt zile mai târziu, ce probează fiecare — adică exact repovestirea pe care am refuzat-o la
# `GARZI.md`. Lista **nu are voie să crească**; când una iese din repo sau primește proprietar, se
# scoate de aici deliberat.
INAINTE_DE_REGULA = {
    "po_0_inainte_coada.png", "po_0_inainte_dashboard.png",
    "po_1_suspendat_coada.png", "po_1_suspendat_dashboard.png", "po_1_suspendat_mobil.png",
    "po_2_efectiv_coada.png", "po_2_efectiv_dashboard.png", "po_2_efectiv_mobil.png",
}


def capturi_comise():
    """Numele fișierelor `.png` urmărite de git sub `frontend_test/`.

    Se citește din **index**, nu de pe disc: o captură abia adăugată în stage e deja aici, deci
    gardul o prinde **la commitul care o aduce**, nu la următorul. Cele ~230 de artefacte
    neurmărite nu intră — regula e despre ce **se comite**."""
    r = subprocess.run(["git", "-C", _RAD, "ls-files", "frontend_test/*.png",
                        "frontend_test/**/*.png"], capture_output=True, text=True)
    return sorted({os.path.basename(x) for x in (r.stdout or "").split("\n") if x.strip()})


def _registru():
    return io.open(_REGISTRU, encoding="utf-8").read()


def nenumite(nume=None, text=None):
    t = _registru() if text is None else text
    return [n for n in (nume if nume is not None else capturi_comise())
            if n not in INAINTE_DE_REGULA and t.count(n) == 0]


def test_fiecare_captura_comisa_e_NUMITA_in_registru():
    rele = nenumite()
    assert not rele, (
        "capturi comise fără proprietar în `CONFORMITATE.md` (%d):\n  %s\n"
        "O captură-probă se numește la restanța pe care o probează (METODA §27) — altfel e un "
        "fișier binar despre care, peste o lună, nimeni nu mai știe ce arată. Dacă e baseline, "
        "n-avea ce căuta în repo." % (len(rele), "\n  ".join(rele)))


def test_lista_de_dinainte_de_regula_NU_creste():
    """Clichet în ambele direcții. Lista e o **datorie declarată**, nu o portiță: o captură nouă
    strecurată în ea ar goli gardul, iar una care a ieșit din repo trebuie scoasă și de aici,
    altfel lista devine o colecție de morți."""
    comise = set(capturi_comise())
    intruse = sorted(INAINTE_DE_REGULA - comise)
    assert not intruse, (
        "nume din lista «dinainte de regulă» care nu mai sunt comise: %s — scoate-le deliberat"
        % intruse)
    assert len(INAINTE_DE_REGULA) == 8, (
        "lista «dinainte de regulă» are %d intrări, nu 8 — a crescut? Regula se aplică de-acum "
        "înainte; o captură NOUĂ nu are ce căuta acolo." % len(INAINTE_DE_REGULA))


def test_ANTI_VACUU_scanul_chiar_vede_capturi():
    comise = capturi_comise()
    assert len(comise) >= 9, (
        "[anti-vacuu] doar %d capturi comise văzute — dacă lista e goală, gardul de mai sus e "
        "adevărat despre nimic" % len(comise))
    assert INAINTE_DE_REGULA <= set(comise)
    assert len(_registru()) > 100000, "registrul nu s-a citit — orice nume ar părea nenumit"


def test_CALIBRARE_o_captura_NENUMITA_e_prinsa():
    """Modul de eșec propriu regulii: cineva comite o captură și uită s-o lege de o restanță."""
    assert nenumite(nume=["proba_inexistenta.png"]) == ["proba_inexistenta.png"]
    # și direcția cealaltă: una numită NU se raportează
    assert nenumite(nume=["cc_scoatere_banner.png"]) == []


def test_CALIBRARE_un_GLOB_in_registru_NU_tine_loc_de_nume():
    """A doua formă, și e chiar greșeala găsită la prima rulare: ieri am scris în R82 *„capturile
    sunt comise, în `frontend_test/aa_*.png` și `w_*.png`"*. Un glob e o mențiune pentru un om și
    **nimic** pentru un instrument — iar peste o lună nici omul nu mai știe care erau.
    """
    fals = "capturile sunt in frontend_test/aa_*.png si w_*.png"
    assert nenumite(nume=["aa_1_alegere_denumire.png"], text=fals) == ["aa_1_alegere_denumire.png"]
