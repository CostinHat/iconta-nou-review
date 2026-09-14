# -*- coding: utf-8 -*-
"""GARDĂ: o trimitere la un număr de linie din `PLAN_HARDENING.md` arată spre ce spune că citează.

DE CE EXISTĂ (13.09.2026, valul D2 al lui P7). Planul e citat pe **linie** din peste douăzeci de
module — `core/straturi.py` o face de 116 ori. Dar planul se **rescrie**: în aceeași tură în care am
adăugat paisprezece rânduri la secțiunea P7, toate citările de sub ele au început să arate spre alt
text, **tăcut**. Iar măsurând ca să le repar am găsit că zona P6 era stătută **dinainte**: patru
ancore, greșite cu ~nouă rânduri, scrise pe 12.09 și necontestate de nimic.

*O citare care nu se poate confrunta nu e un temei, e o amintire* — aceeași clasă cu lecția 26
(registrul care dă o cifră veche drept DOVADĂ) și cu `[[o-cifra-care-nu-se-poate-recalcula]]`.

CE PĂZEȘTE, în amândouă direcțiile:
  · fiecare citare care apare în cod are un rând în tabelul de mai jos (altfel tabelul îmbătrânește
    la fel ca citările — o gardă care se uită la o submulțime afirmă despre „toate" ce a verificat
    despre „câteva", lecția 25);
  · fiecare ancoră chiar poartă, la liniile alea, fragmentul pentru care e citată.

CE NU PĂZEȘTE, declarat: că fragmentul ales e **partea care contează** din text. Tabelul spune ce
trebuie să se găsească acolo, nu că e tot ce trebuia citat.
"""
import io
import os
import re

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = os.path.join(RADACINA, "PLAN_HARDENING.md")

#: ancoră (linia sau intervalul citat) -> fragment care TREBUIE să stea acolo, exact o dată.
ANCORE = {
    # P5
    "325-342": "# P5 — ASYNC / BLOCKING I/O",
    "328": "se caută rutele în care un I/O blocant",
    "330-334": "**Benchmark concurent**",
    # P6
    "705-730": "# P6 — STATELESS / SCALARE ORIZONTALĂ",
    "707": "Nicio stare business autoritativă doar în memoria unui proces",
    "708-710": "`main._alerte_ultima_trimitere`",
    "713-716": "Cache local admis, dar numai DECLARAT",
    "718-719": "trecerea de la **un singur proces**",
    "718-729": "trecerea de la **un singur proces**",
    "721-729": "**Cum se verifică.**",
    "723": "blocarea la autentificare ține pe ambele",
    "728-729": "brațul se redefinește",
    # P7
    "733-817": "# P7 — APPLICATION LAYER",
    "842-846": "**repository** — singurul care știe SQL și scheme",
    "839": "**HTTP** — validare de formă",
    "840": "**use-case** — deține tranzacția (P4)",
    "841": "**motor fiscal** — pur pe cât se poate",
    "842": "**repository** — singurul care știe SQL și scheme",
    "845-848": "un motor fiscal nu importă `db`",
    "845": "un motor fiscal nu importă `db`",
    "846": "ruta nu conține SQL",
}

_CITARE = re.compile(r"PLAN_HARDENING\.md:(\d+(?:-\d+)?)")


def _fisiere_py():
    out = []
    for rad, dirs, fis in os.walk(RADACINA):
        dirs[:] = [d for d in dirs if d not in ("venv", ".git", "__pycache__", "efactura_zip")]
        out += [os.path.join(rad, f) for f in fis if f.endswith(".py")]
    return sorted(out)


def _citari_din_cod():
    """{ancoră: [fișiere]} — derivat din repo la fiecare rulare, nu scris."""
    gasite = {}
    for cale in _fisiere_py():
        try:
            sursa = io.open(cale, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            continue
        for m in _CITARE.finditer(sursa):
            gasite.setdefault(m.group(1), []).append(os.path.relpath(cale, RADACINA))
    return gasite


def _bucata(ancora, text=None):
    linii = (text if text is not None
             else io.open(PLAN, encoding="utf-8").read()).split("\n")
    a, _, b = ancora.partition("-")
    return "\n".join(linii[int(a) - 1:int(b or a)])


def test_fiecare_citare_din_cod_are_rand_in_tabel():
    """Exhaustivitate: tabelul acoperă TOT ce citează repo-ul, nu un eșantion."""
    derivate = set(_citari_din_cod())
    assert derivate == set(ANCORE), (
        "citări fără rând în tabel: %s · rânduri fără citare în cod: %s"
        % (sorted(derivate - set(ANCORE)), sorted(set(ANCORE) - derivate)))


def test_fiecare_ancora_poarta_chiar_textul_pentru_care_e_citata():
    citari = _citari_din_cod()
    gresite = []
    for ancora, fragment in sorted(ANCORE.items()):
        if _bucata(ancora).count(fragment) != 1:
            gresite.append((ancora, fragment, sorted(set(citari.get(ancora, [])))))
    assert gresite == [], (
        "ancore care nu mai arată spre textul lor (ancoră, fragment, cine o citează): %s" % gresite)


def _deplaseaza(plan, n):
    return ("RÂND INSERAT DE PROBĂ" + chr(10)) * n + plan


def test_o_ancora_de_O_LINIE_pica_la_o_deplasare_de_UN_rand():
    """Mutația gărzii, pe un plan SIMULAT: exact defectul care a produs-o, dar fabricat.

    Se inserează un rând la începutul planului — adică se deplasează TOT cu unu, cum s-a întâmplat
    azi cu paisprezece rânduri — și se cere ca NICIO ancoră de o singură linie să nu mai potrivească.
    Fără proba asta, tabelul ar putea fi verde fiindcă fragmentele sunt atât de scurte încât se
    regăsesc oriunde.
    """
    deplasat = _deplaseaza(io.open(PLAN, encoding="utf-8").read(), 1)
    singure = {a: f for a, f in ANCORE.items() if a.isdigit()}
    assert len(singure) >= 8, "ANTI-VACUUM: nu mai sunt ancore de o linie în tabel"
    supravietuitori = [a for a, fragment in singure.items()
                       if _bucata(a, deplasat).count(fragment) == 1]
    assert supravietuitori == [], (
        "ancore de o linie care potrivesc și pe un plan deplasat — fragment prea slab: %s"
        % sorted(supravietuitori))


def test_un_INTERVAL_tolereaza_o_deplasare_mai_MICA_decat_el_si_se_spune():
    """Limita declarată a gărzii, nu o scăpare: un interval e tolerant prin construcție.

    Un interval de N rânduri nu poate deosebi o deplasare mai mică decât N — fragmentul rămâne
    înăuntru. Ce SE poate cere, și se cere aici, e ca la o deplasare cât înălțimea intervalului
    ancora să cadă. *Cine citează un interval cumpără toleranța lui; proba asta o măsoară, în loc
    s-o lase nescrisă.*
    """
    plan = io.open(PLAN, encoding="utf-8").read()
    intervale = {a: f for a, f in ANCORE.items() if not a.isdigit()}
    assert len(intervale) >= 8, "ANTI-VACUUM: nu mai sunt intervale în tabel"
    supravietuitori = []
    for ancora, fragment in intervale.items():
        a, _, b = ancora.partition("-")
        inaltime = int(b) - int(a) + 1
        if _bucata(ancora, _deplaseaza(plan, inaltime)).count(fragment) == 1:
            supravietuitori.append(ancora)
    assert supravietuitori == [], (
        "intervale care potrivesc și după o deplasare cât înălțimea lor: %s" % sorted(supravietuitori))


def test_ANTI_VACUUM_garda_chiar_vede_citari():
    citari = _citari_din_cod()
    assert len(citari) >= 15, "s-au pierdut citările din vedere: %d" % len(citari)
    total = sum(len(v) for v in citari.values())
    assert total >= 100, "numărul de citări a căzut la %d — garda se uită în gol?" % total
