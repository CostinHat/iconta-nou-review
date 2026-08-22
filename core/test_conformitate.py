# -*- coding: utf-8 -*-
"""GARDĂ: fiecare interdicție din plan are secțiune în CONFORMITATE.md, completă. (22.08.2026)

DE CE (Costin): «Cifrele confruntării nu au voie să existe doar în raport. Raportul se citește o
dată; registrul rămâne.» Prima confruntare a produs opt cifre care au trăit doar într-un mesaj — dacă
nimeni nu le mai citea, munca de măsurare se pierdea și s-ar fi refăcut de la zero.

CE FACE IMPOSIBIL:
  - o interdicție din `PLAN_ARHITECTURA.md` fără secțiune în `CONFORMITATE.md`;
  - o secțiune cu un câmp OBLIGATORIU gol — «un câmp gol nu e permis: dacă nu se poate măsura, scrie
    NEMĂSURABILĂ cu motivul»;
  - o stare din afara celor patru. «Investigată» NU e o stare;
  - o secțiune orfană, pentru o interdicție care nu există în plan;
  - o interdicție NOUĂ adăugată în plan fără secțiune — cazul care motivează gardul cel mai tare,
    fiindcă planul crește (25 -> 48 într-o zi).

CE NU FACE, declarat: nu verifică dacă cifra e CORECTĂ, nici dacă măsurătoarea a fost bine făcută.
Verifică forma și completitudinea. Adevărul unei cifre se probează prin calibrare, nu prin gardă.

CITIREA CÂMPURILOR, cu motivul (22.08, după RED-proof): valoarea unui câmp se citește cu `[ \t]*`,
NU cu `\\s*`, fiindcă `\\s` cuprinde și linia nouă. Prima formă a gardului lăsa un câmp golit să
împrumute textul rândului URMĂTOR — mutația «câmp obligatoriu gol» a trecut. Un gard care citește
peste marginea rândului măsoară alt fișier decât cel scris.
"""
import io
import os
import re

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = os.path.join(RAD, "PLAN_ARHITECTURA.md")
CONF = os.path.join(RAD, "CONFORMITATE.md")

STARI = ("MĂSURATĂ", "NEMĂSURABILĂ", "PARȚIAL", "NEÎNCEPUTĂ")

# Câmpurile cerute de Costin. Fiecare trebuie să existe ȘI să aibă conținut.
CAMPURI = ("stare", "cifra", "instanțe", "calibrare", "ce nu vede", "unde ajunge efectul")

CAP_TABEL = "CE E INTERZIS PRIN CONSTRUCȚIE"


def _camp(corp, nume):
    """Valoarea câmpului `nume`, sau None dacă lipsește. Se oprește la capătul RÂNDULUI."""
    m = re.search(r"^[ \t]*[-*]?[ \t]*\*\*%s\*\*[ \t]*:[ \t]*(.*)$" % re.escape(nume),
                  corp, re.M | re.I)
    return None if m is None else m.group(1).strip()


def _interdictii_din_plan():
    """{numar: text} din tabelul PARTEA VI. Se citește din plan, nu dintr-o listă copiată aici —
    altfel gardul ar apăra o lume pe care planul a părăsit-o."""
    t = io.open(PLAN, encoding="utf-8").read()
    # Nu `.index`: un ValueError ar spune «substring not found», nu CE s-a rupt.
    assert CAP_TABEL in t, (
        "în PLAN_ARHITECTURA.md nu mai există capul de tabel %r. Ori s-a redenumit secțiunea, ori "
        "planul s-a rescris — gardul NU poate citi interdicțiile, deci nu are ce apăra. Se repară "
        "aici, nu se ocolește." % CAP_TABEL)
    i = t.index(CAP_TABEL)
    j = t.index("\n# ", i)
    out = {}
    for m in re.finditer(r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|", t[i:j], re.M):
        out[int(m.group(1))] = m.group(2).replace("**", "").strip()
    return out


def _sectiuni_din_conformitate():
    """{numar: (titlu, corp)} — o secțiune începe cu `## N — <titlu>`."""
    t = io.open(CONF, encoding="utf-8").read()
    buc = re.split(r"^## (\d+)\s*[—-]\s*(.+)$", t, flags=re.M)
    out = {}
    for k in range(1, len(buc), 3):
        out[int(buc[k])] = (buc[k + 1].strip(), buc[k + 2])
    return out


@pytest.fixture(scope="module")
def plan():
    return _interdictii_din_plan()


@pytest.fixture(scope="module")
def conf():
    return _sectiuni_din_conformitate()


def test_planul_chiar_se_citeste(plan):
    """ANTI-VACUU. Dacă parsarea planului se strică, toate testele de mai jos ar trece pe zero
    interdicții — exact interdicția 19 („o gardă care raportează favorabil pe zero rânduri")."""
    assert len(plan) >= 25, (
        "doar %d interdicții citite din plan — parsarea s-a rupt, nu planul s-a golit" % len(plan))
    assert 1 in plan and "registru" in plan[1].lower()


def test_citirea_campurilor_se_opreste_la_capatul_randului():
    """ANTI-VACUU pe INSTRUMENT, nu pe date. Cazul real din RED-proof: un câmp golit care împrumută
    rândul următor. Fără proba asta, `test_niciun_camp_obligatoriu_gol` trece pe un fișier golit."""
    corp = "- **cifra**: \n- **instanțe**: 3 apeluri\n"
    assert _camp(corp, "cifra") == "", "un câmp gol trebuie citit GOL, nu cu textul rândului următor"
    assert _camp(corp, "instanțe") == "3 apeluri"
    assert _camp(corp, "calibrare") is None


def test_fiecare_interdictie_are_sectiune(plan, conf):
    lipsa = sorted(set(plan) - set(conf))
    assert not lipsa, (
        "interdicții din plan FĂRĂ secțiune în CONFORMITATE.md: %s.\n"
        "O interdicție nouă în plan cere secțiune — chiar și NEÎNCEPUTĂ. Așa se vede de la început "
        "cât e de făcut, nu se descoperă pe parcurs." % lipsa)


def test_nicio_sectiune_orfana(plan, conf):
    """Direcția inversă: o secțiune pentru o interdicție care nu mai există în plan e o măsurătoare
    despre o lume care s-a schimbat."""
    orfane = sorted(set(conf) - set(plan))
    assert not orfane, "secțiuni în CONFORMITATE.md fără interdicție în plan: %s" % orfane


def test_starea_e_dintre_cele_patru(conf):
    """«Investigată» nu e o stare."""
    rele = []
    for n, (_titlu, corp) in sorted(conf.items()):
        val = _camp(corp, "stare")
        if val is None:
            rele.append("  #%d: fără câmpul `stare`" % n)
            continue
        val = val.strip("*").split("—")[0].split("(")[0].split(",")[0].strip()
        if val not in STARI:
            rele.append("  #%d: stare %r — cele patru sunt: %s" % (n, val, ", ".join(STARI)))
    assert not rele, "stări nevalide:\n" + "\n".join(rele)


def test_niciun_camp_obligatoriu_gol(conf):
    """«Un câmp gol nu e permis: dacă nu se poate măsura, scrie NEMĂSURABILĂ cu motivul.»"""
    rele = []
    for n, (_titlu, corp) in sorted(conf.items()):
        for camp in CAMPURI:
            val = _camp(corp, camp)
            if val is None:
                rele.append("  #%d: lipsește câmpul `%s`" % (n, camp))
            elif len(val.strip("*—- ")) < 3:
                rele.append("  #%d: câmpul `%s` e GOL" % (n, camp))
    assert not rele, ("câmpuri obligatorii lipsă sau goale (%d):\n" % len(rele)) + "\n".join(rele[:20])


def test_masuratele_au_cifra_si_calibrare(conf):
    """O stare MĂSURATĂ fără cifră sau fără calibrare e o afirmație fără probă. Calibrarea trebuie să
    numească ce caz cunoscut a fost GĂSIT — altfel cifra nu se poate crede."""
    rele = []
    for n, (_titlu, corp) in sorted(conf.items()):
        st = _camp(corp, "stare") or ""
        if "MĂSURATĂ" not in st:
            continue
        cif = _camp(corp, "cifra") or ""
        if not re.search(r"\d", cif):
            rele.append("  #%d: MĂSURATĂ fără cifră" % n)
        if "găsit" not in (_camp(corp, "calibrare") or "").lower():
            rele.append("  #%d: MĂSURATĂ fără caz de calibrare GĂSIT" % n)
    assert not rele, "măsurători fără probă:\n" + "\n".join(rele)


def test_partialele_spun_ca_cifra_e_plafon(conf):
    """O stare PARȚIAL fără declararea limitei se citește ca un total. Cifra unei măsurători pe o
    formă declarată e un PLAFON INFERIOR, iar asta trebuie scris, nu subînțeles."""
    rele = []
    for n, (_titlu, corp) in sorted(conf.items()):
        if "PARȚIAL" not in (_camp(corp, "stare") or ""):
            continue
        text = ((_camp(corp, "ce nu vede") or "") + " " + (_camp(corp, "cifra") or "")).lower()
        if "plafon" not in text and "nu e un total" not in text:
            rele.append("  #%d: PARȚIAL fără să spună că cifra e un plafon inferior" % n)
    assert not rele, "\n".join(rele)


def test_nemasurabilele_spun_de_ce(conf):
    """O stare NEMĂSURABILĂ fără motiv e o scuză."""
    rele = []
    for n, (_titlu, corp) in sorted(conf.items()):
        if "NEMĂSURABILĂ" in (_camp(corp, "stare") or ""):
            if "motiv" not in corp.lower():
                rele.append("  #%d: NEMĂSURABILĂ fără motivul scris" % n)
    assert not rele, "\n".join(rele)


def test_se_vede_cat_e_de_facut(plan, conf):
    """Rostul fișierului: «așa se vede de la început cât e de făcut, nu se descoperă pe parcurs».
    Dacă toate ar fi NEÎNCEPUTE, cifra n-ar mai spune nimic."""
    stari = [(_camp(corp, "stare") or "?").split()[0] for _n, (_t, corp) in conf.items()]
    assert stari.count("NEÎNCEPUTĂ") < len(stari), "nimic măsurat — fișierul e o listă, nu un registru"
    assert len(conf) == len(plan)
