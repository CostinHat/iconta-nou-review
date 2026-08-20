# -*- coding: utf-8 -*-
"""GARD (20.08.2026): a doua cale nu poate fi mutată peste prima în tăcere.

CAZUL CARE L-A PRODUS. `core/d112_reconciliere.py` există ca verificare în patru ochi pentru
`core/d112.py`: SQL propriu, rotunjire proprie, interdicție de a importa modulul verificat. Sub-cazul
1c-PT (part-time) e declarat „reconciliere COMPLETĂ" pe CAS+CASS. Pe 06.08.2026 podeaua part-time a
fost schimbată în `d112.py` **și în același commit** în reconciliere, cu motivul scris pe linie:
`# ... Aliniat cu d112.pull prag_pt`. Din acel moment a doua cale a încetat să mai fie a doua: a
confirmat două săptămâni o cifră pe care arbitrul (DUK regula SP1B4_1) o semnala, iar
fluturașul și declarația au declarat sume diferite pentru același salariat (70,25 lei/lună).

REGULA. O a doua cale nu e independentă prin construcție, ci prin DISCIPLINĂ: când cele două nu
coincid, întrebarea se duce la **arbitru**, nu se mută verificatorul peste verificat. Două colțuri:

  1. **Fără limbaj de aliniere** (permanent, fără baseline, fără git): niciun modul de verificare nu
     are voie să conțină „aliniat cu <modulul verificat>". E amprenta exactă a motivului greșit, și e
     scrisă în cod de cel care o face. ZERO admis — la 20.08 nu mai există nicio instanță.
     O linie care CITEAZĂ o aliniere trecută (ca să nu se piardă istoricul) poartă marcajul
     `istoric-aliniere-ok:` — același tipar cu `# upsert-ok:` din restul repo-ului.
  2. **Co-modificarea cere decizie scrisă** (la commit): dacă `core/X.py` și `core/X_reconciliere.py`
     se schimbă amândouă față de HEAD, atunci `DECIZII.md` trebuie să se schimbe în aceeași tură.
     NU interzice co-modificarea — o schimbare de lege chiar cere ambele căi. Cere doar ca motivul să
     fie consemnat, ca să nu se poată strecura „le-am aliniat" fără ca cineva să scrie de ce.

LIMITĂ DECLARATĂ: colțul 1 prinde alinierea DECLARATĂ. O aliniere tăcută (schimbi formula fără s-o
spui) nu lasă amprentă textuală — pentru aia colțul 2 e plasa, iar arbitrul rămâne judecătorul final.
"""
import ast
import os
import re
import subprocess

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CORE = os.path.join(_RAD, "core")
# „aliniat/aliniere ... <ceva>.pull / <modul>" — amprenta motivului greșit
_ALINIERE = re.compile(r"alini(?:at|ere|em|ez)\b[^\n]{0,80}?\b(d\d{3}|salarizare|pull)\b", re.I)
# O linie care DOCUMENTEAZA o aliniere trecuta (nu o face) poarta marcajul explicit, ca `# upsert-ok:`
# din restul repo-ului. Scrierea marcajului e un act deliberat: „asta e istorie, nu o aliniere noua".
_MARCAJ_ISTORIC = "istoric-aliniere-ok:"


def _perechi():
    """[(verificator_rel, verificat_rel)] deduse din numele fișierelor."""
    out = []
    for f in sorted(os.listdir(_CORE)):
        if f.endswith("_reconciliere.py") and not f.startswith("test_"):
            tinta = f.replace("_reconciliere", "")
            if os.path.exists(os.path.join(_CORE, tinta)):
                out.append(("core/" + f, "core/" + tinta))
    return out


def test_gardul_vede_caile_de_verificare():
    """Anti-vacuu: dacă tiparul de nume se schimbă, testele de mai jos ar trece pe gol."""
    p = _perechi()
    assert len(p) >= 8, "doar %d perechi verificator/verificat găsite - euristica s-a rupt" % len(p)


def test_nicio_cale_de_verificare_nu_declara_aliniere():
    """Colțul 1: ZERO admis, fără baseline."""
    rele = []
    for ver, tinta in _perechi():
        cale = os.path.join(_RAD, ver)
        for n, linie in enumerate(open(cale, encoding="utf-8", errors="replace"), 1):
            if _MARCAJ_ISTORIC in linie:
                continue
            m = _ALINIERE.search(linie)
            if m:
                rele.append("%s:%d  %s" % (ver, n, linie.strip()[:120]))
    assert not rele, (
        "Cale de verificare care declară că a fost ALINIATĂ la modulul pe care îl verifică. "
        "Dacă cele două nu coincid, decide la ARBITRU care are dreptate și repară acolo - nu muta "
        "verificatorul peste verificat:\n  - " + "\n  - ".join(rele))


def _modificate_fata_de_head():
    r = subprocess.run(["git", "-C", _RAD, "diff", "--name-only", "HEAD"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return {l.strip() for l in r.stdout.splitlines() if l.strip()}


def test_co_modificarea_cere_decizie_scrisa():
    """Colțul 2: verificator + verificat schimbate împreună -> DECIZII.md în aceeași tură."""
    mod = _modificate_fata_de_head()
    if mod is None:
        import pytest
        pytest.skip("git indisponibil")
    impreuna = [(v, t) for v, t in _perechi() if v in mod and t in mod]
    if not impreuna:
        return
    assert "DECIZII.md" in mod, (
        "Ai schimbat în aceeași tură și verificatorul, și verificatul: %s. Nu e interzis - o schimbare "
        "de lege cere ambele căi - dar motivul trebuie SCRIS, altfel nimeni nu mai poate distinge "
        "„amândouă implementează noua regulă\" de „am aliniat verificatorul ca să tacă\". "
        "Scrie decizia în DECIZII.md, cu ce spune arbitrul."
        % ", ".join("%s+%s" % (v, t) for v, t in impreuna))


def test_reconcilierea_d112_chiar_e_independenta_de_d112():
    """Ancoră pozitivă pe cazul care a produs gardul: a doua cale nu importă modulul verificat."""
    src = open(os.path.join(_CORE, "d112_reconciliere.py"), encoding="utf-8").read()
    arb = ast.parse(src)
    importate = set()
    for n in ast.walk(arb):
        if isinstance(n, ast.ImportFrom) and (n.module or "").startswith("core"):
            importate.update(a.name for a in n.names)
        elif isinstance(n, ast.Import):
            importate.update(a.name.split(".")[-1] for a in n.names)
    assert "d112" not in importate and "salarizare" not in importate, \
        "d112_reconciliere importă modulul pe care ar trebui să-l verifice independent: %s" % sorted(importate)
