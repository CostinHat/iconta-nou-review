# -*- coding: utf-8 -*-
"""GARD [03.09.2026]: ocolirea de curatenie se deschide din INDEX, si numai pentru curatenie.

**Regula pazita** (`PLAN_LUCRU.md`, regula 7 de conducere a lucrului, Costin 03.09.2026):
*„Operatiunile de curatenie — stergeri de fisiere, .gitignore, mutari — nu ruleaza teste deloc."*
Cu conditia, in aceeasi comanda: *„eticheta e ignorata daca commitul atinge vreun fisier executabil
sau vreun registru. … Altfel devine cheia care deschide tot."*

**CELE DOUA DIRECTII, fiindca una singura n-ar dovedi nimic** (METODA §22):
  1. pe un commit care CHIAR e curatenie, instrumentul deschide — altfel ar putea raspunde mereu
     „nu" si ar parea perfect de sigur, iar poarta n-ar scurta niciodata nimic;
  2. pe fiecare dintre cele patru feluri de a NU fi curatenie (executabil, registru, forma gresita,
     fisier numit de ceva), instrumentul refuza — si SPUNE care fisier l-a facut sa refuze.

**CE NU PAZESTE, declarat.** Ramura `commit-msg` care cere eticheta cand poarta CHIAR a fost sarita
nu se poate exercita din suita: daca indexul ar fi numai-curatenie, suita n-ar rula deloc — exact
ce cere regula. Testul functional de mai jos compara hook-ul cu verdictul instrumentului in starea
reala a indexului, deci acopera intotdeauna doar una dintre cele doua ramuri. Cealalta e acoperita
prin clasificare, pe intrari sintetice.
"""
import os
import shlex
import subprocess
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from scripts import curatenie as C  # noqa: E402
from scripts import perimetru as P  # noqa: E402

#: Registre si nume-numite, ca argumente EXPLICITE ale clasificarii: testele de mai jos nu depind
#: de starea arborelui de azi. Ce depinde de arbore e strans in `test_..._VEDE_lumea...`.
REG = {"CONFORMITATE.md", "PLAN_LUCRU.md", "anaf_surse/INDEX.json", "INDEX.json"}


def _cai_din_motive(motive):
    """Prima bucata a fiecarui motiv — instrumentul le scrie ca `<ce> — <de ce>`."""
    return {m.split(" — ")[0] for m in motive}


# ── directia 1: o curatenie adevarata trece ──────────────────────────────────
def test_stergeri_mutari_si_gitignore_TREC():
    """Daca instrumentul n-ar deschide niciodata, regula 7 ar fi scrisa si nepazita: fiecare tura
    de stergere ar plati in continuare cele 22 de minute pe care comanda le-a masurat."""
    intrari = [("D", "_arhiva/captura_veche.png", ""),
               ("R100", "_arhiva/a.csv", "_arhiva/b.csv"),
               ("M", ".gitignore", "")]
    assert C.clasifica(intrari, REG, set()) == []


# ── directia 2: cele patru feluri de a NU fi curatenie ───────────────────────
def test_un_EXECUTABIL_atins_inchide_ocolirea():
    """Conditia lui Costin, litera intai. `.py` si `.js` — imprumutate, nu redefinite aici."""
    for cale in ("core/d100.py", "static/js/nir.js"):
        motive = C.clasifica([("D", cale, "")], REG, set())
        assert _cai_din_motive(motive) >= {cale}, (
            "%s a trecut ca «curatenie» — un executabil sters poate strica orice" % cale)


def test_un_REGISTRU_atins_inchide_ocolirea():
    """Conditia lui Costin, litera a doua. Si pe mutare, nu doar pe stergere: un registru mutat
    dispare la fel de complet pentru garda care il deschide dupa nume."""
    assert _cai_din_motive(C.clasifica([("D", "CONFORMITATE.md", "")], REG, set())) >= \
        {"CONFORMITATE.md"}
    assert _cai_din_motive(C.clasifica([("R100", "PLAN_LUCRU.md", "vechi/PLAN_LUCRU.md")],
                                       REG, set())) >= {"PLAN_LUCRU.md"}


def test_ORICE_ALTCEVA_decat_stergere_mutare_gitignore_inchide_ocolirea():
    """*„Se aplica DOAR la stergeri, .gitignore si mutari."* Un fisier adaugat, o modificare de
    continut, o mutare cu continut schimbat (`R097`, nu `R100`) — niciuna nu e curatenie."""
    for intrare in (("A", "raport_nou.txt", ""),
                    ("M", "date_test/sume.csv", ""),
                    ("R097", "a.txt", "b.txt"),
                    ("T", "legatura", "")):
        motive = C.clasifica([intrare], REG, set())
        assert motive, "%s a trecut ca «curatenie», desi nu e nici stergere, nici mutare pura" % (
            intrare,)


def test_un_fisier_NUMIT_in_ce_se_comite_nu_e_curatenie():
    """Gaura pe care primele doua conditii o lasa deschisa, si e cea care doare: un `.xsd`, o
    fixtura `.json`, o captura numita intr-un registru NU sunt nici executabile, nici registre —
    dar daca ceva le deschide, stergerea lor e o modificare prin absenta, iar suita cade la
    urmatorul commit, in bratele altcuiva."""
    motive = C.clasifica([("D", "declaratii/d406.xsd", "")], REG, {"d406.xsd"})
    assert _cai_din_motive(motive) >= {"declaratii/d406.xsd"}


def test_FAIL_CLOSED_cand_git_nu_raspunde():
    """Un instrument de scurtat care greseste spre «da» nu e instrument, e portita."""
    assert C.clasifica(None, REG, set()), "index necitibil raportat ca «curatenie»"
    assert C.clasifica([], REG, set()), "index gol raportat ca «curatenie»"


# ── ca definitiile sa nu se desparta in tacere ───────────────────────────────
def test_definitiile_sunt_IMPRUMUTATE_de_la_perimetru_nu_rescrise():
    """A doua definitie a aceluiasi lucru e inceputul unei divergente tacute: peste o luna,
    `perimetru.py` ar sti ca un registru nou e registru, iar ocolirea de curatenie n-ar sti.
    Aserttiunea e pe IDENTITATE de obiect, nu pe egalitate de valori — o copie cu acelasi continut
    ar trece la egalitate si ar diverge la prima modificare."""
    assert C.EXT_EXECUTABILE is P.EXT_EXECUTABILE
    assert C.registre() == P._documente_urmarite()


def test_cautarea_de_referinte_VEDE_lumea_despre_care_raporteaza():
    """[anti-vacuu, in amandoua directiile] O cautare care intoarce mereu multimea vida ar declara
    „curatenie" pe orice stergere; una care intoarce mereu tot n-ar deschide niciodata. Se cere,
    pe arborele real: un nume care CHIAR e citat e gasit, si unul inventat NU e.

    **Numele inventat se CONSTRUIESTE la rulare, si asta a costat o poarta.** Prima forma il scria
    ca literal — iar cand fisierul asta a intrat in index, `git grep --cached` l-a gasit chiar in
    testul care il declara inexistent. *Un gard care se cauta pe sine raporteaza despre o lume care
    il contine* ([[gard-care-nu-se-verifica-pe-sine]], instanta noua)."""
    inventat = "zzz_%s_%d.png" % ("nume" + "_inventat", os.getpid())
    gasite = C.numite_in_arbore(["CONFORMITATE.md", inventat])
    assert gasite == {"CONFORMITATE.md"}


# ── cablarea: o regula scrisa si necablata nu e o regula pazita ──────────────
def _tokenuri(cale):
    """Cuvintele unui script `sh`, fara comentarii. Se citeste cu `shlex`, nu cu cautare de sir:
    numele instrumentului scris intr-un COMENTARIU nu inseamna ca hook-ul il cheama — exact
    deosebirea ceruta de METODA §23, aplicata pe singura structura pe care shell-ul o are."""
    out = []
    with open(os.path.join(_RAD, "scripts", "githooks", cale), encoding="utf-8") as f:
        for linie in f:
            try:
                out += shlex.split(linie, comments=True)
            except ValueError:          # ghilimele deschise pe mai multe randuri
                continue
    return out


def test_AMANDOUA_hookurile_cheama_instrumentul():
    """`pre-commit` sare poarta, `commit-msg` cere marturia. Daca vreunul nu mai cheama
    instrumentul, ocolirea devine ori inaccesibila, ori tacuta."""
    for hook in ("pre-commit", "commit-msg"):
        chemat = [t for t in _tokenuri(hook) if t.endswith("curatenie.py")]
        assert chemat, "%s nu mai cheama scripts/curatenie.py — regula 7 e scrisa, nu cablata" % hook


def test_commit_msg_cere_ETICHETA_exact_cand_poarta_a_fost_sarita(tmp_path):
    """Functional, pe hook-ul adevarat: verdictul instrumentului si raspunsul hook-ului trebuie sa
    fie aceeasi afirmatie. Mesajul de proba poarta dinadins `# diff-citit:` si `# multe-fisiere-ok:`
    — altfel hook-ul ar putea respinge din alt motiv, iar testul ar trece pe cauza gresita."""
    e_curatenie, _motive, _intrari = C.verdict()
    baza = ("Proba de calibrare a portii de curatenie\n\n"
            "# diff-citit: proba de calibrare, nu un commit real; nimic de aplicat\n"
            "# multe-fisiere-ok: proba de calibrare\n")
    for cu_eticheta in (False, True):
        msg = tmp_path / ("msg_%s.txt" % cu_eticheta)
        text = baza + ("# doar-curatenie: proba de calibrare a etichetei\n" if cu_eticheta else "")
        msg.write_text(text, encoding="utf-8")
        r = subprocess.run(["sh", os.path.join(_RAD, "scripts", "githooks", "commit-msg"),
                            str(msg)], cwd=_RAD, capture_output=True, text=True)
        trecut = (r.returncode == 0)
        assert trecut == (cu_eticheta == e_curatenie), (
            "hook-ul si instrumentul nu spun acelasi lucru: indexul e curatenie=%s, mesajul poarta "
            "eticheta=%s, iar hook-ul a %s.\n%s" % (
                e_curatenie, cu_eticheta, "trecut" if trecut else "respins", r.stdout[-600:]))
