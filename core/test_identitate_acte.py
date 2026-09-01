# -*- coding: utf-8 -*-
"""GARD — un act din corpus e ACTUL pe care îl spune numele lui, și e adus o singură dată.

  core/test_identitate_acte.py

Cerut de Costin, 24.08.2026. `PROVENIENTA` răspunde la *„s-a schimbat fișierul după aducere?"* —
amprenta față de fișier. **Nu răspunde la „e fișierul actul potrivit?"** — identitatea față de nume.
Sunt două întrebări, iar a doua n-avea gardă.

DOUĂ VERIFICĂRI:
  1. **Identitatea** — dacă numele codifică un act (`oug_91_2025`, `legea_141_2025`), titlul din
     document trebuie să poarte ACELAȘI număr și an. Numerele mici de lege se repetă între ani:
     „Legea 1" există în 2020, 2011, 2005… Un fișier numit `legea_1_2020` care conține Legea 1/2011
     ar introduce un temei fals fără ca nimic să se aprindă.
  2. **Unicitatea** — niciun act nu e în corpus de două ori sub nume diferite. Măsurat pe 24.08:
     **patru** acte erau duplicate byte-identic (OPANAF 179/2022, 2194/2025, 407/2025, 206/2025),
     aduse de două ori la zile distanță. Un act în două copii înseamnă că o corectură pe una lasă
     cealaltă neatinsă.

CE NU PRINDE, declarat — și e important, fiindcă limita e chiar la marginea cazului care a produs
gardul: verificarea 1 compară **numărul și anul**, nu OBIECTUL actului. Un fișier corect numit, care
conține chiar actul cu acel număr, trece — chiar dacă actul acela nu e cel de care aveai nevoie.
Aia e o citire, nu o potrivire. (Instanța: `hg_1094_2025` avea titlul potrivit numelui; greșeala
era la descărcare, în ce act s-a cerut — gardul ăsta n-ar fi prins-o.)

Nici fișierele fără bloc de titlu — structuri, extrase, note — nu se pot verifica; se numără, iar
numărul e pinat, ca acoperirea să nu scadă tăcut. **Acoperirea de azi: 130 din 251 (52%).**
Deci gardul vede jumătate din corpusul cu nume de act — și asta se scrie, nu se presupune.
"""
import hashlib
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SURSE = os.path.join(RAD, "anaf_surse")

NUME = re.compile(r"^(lege|legea|oug|hg|og|opanaf|omfp|ordin)_(\d+)_(\d{4})", re.I)
CUV = {
    "lege": r"LEGE", "legea": r"LEGE",
    "oug": r"ORDONAN[ȚT][ĂA]\s+DE\s+URGEN[ȚT][ĂA]",
    "hg": r"HOT[ĂA]R[ÂA]RE",
    "og": r"ORDONAN[ȚT][ĂA]",
    "opanaf": r"ORDIN", "omfp": r"ORDIN", "ordin": r"ORDIN",
}
TAG = re.compile(r"<[^>]+>")
ANTET = 6000
# Numărul poate fi scris cu separator de mii: „nr. 1.094". Fără asta, tiparul taie la prima cifră.
NR = r"[0-9][0-9.]*"

# Fișiere fără bloc de titlu verificabil. MĂSURAT 24.08.2026, nu estimat: din **251** de
# fișiere cu nume de act, **130 au titlu verificabil (52%)** și 121 nu — 39 `.pdf` fără frate
# `.txt`, 57 `.txt` de extras, 25 `.html` care sunt structuri sau note, nu acte cu antet.
# Clichet: nu poate CREȘTE. Dacă scade, se coboară — altfel acoperirea reală se pierde.
#
# 121 → 123 la 01.09.2026 (R110), și cele două se NUMESC, fiindcă un clichet urcat fără nume e o
# excepție cunoscută de un singur raport: `ordin_1604_2025_intrastat_mo.pdf` și fratele lui `.txt`.
# MOTIVUL, mecanic: fișierele poartă forma **Monitorului Oficial**, unde titlul din antet e fără
# număr („ORDIN privind pragurile valorice Intrastat…"), iar numărul și data stau la PICIOR
# („Nr. 1.604." · „București, 27 octombrie 2025."). Tiparul de aici cere `ORDIN nr. N din <data>`,
# forma portalului — deci nu ratează un act neidentificabil, ci o AȘEZARE pe care n-o citește.
# NU am scris un tipar pentru forma MO, și motivul e măsurat: în tot corpusul există **un singur**
# fișier cu antet de Monitor Oficial — al meu. Un tipar calibrat pe unicul exemplar care l-a cerut
# n-ar dovedi nimic despre acoperire (METODA §22). Rămâne clasă declarată, de reparat când există
# pe ce o măsura.
CLICHET_FARA_TITLU = 123


def _text(cale):
    if cale.endswith(".pdf"):
        frate = cale[:-4] + ".txt"
        return _text(frate) if os.path.exists(frate) else None
    try:
        t = io.open(cale, encoding="utf-8", errors="ignore").read(200000)
    except OSError:
        return None
    if cale.endswith(".html"):
        t = TAG.sub(" ", t)
    return re.sub(r"\s+", " ", t)[:ANTET]


def _acte():
    """(fisier, tip, nr, an) pentru fișierele al căror NUME codifică un act."""
    out = []
    for f in sorted(os.listdir(SURSE)):
        if f.endswith((".sha256", ".json")):
            continue
        m = NUME.match(f)
        if m and os.path.isfile(os.path.join(SURSE, f)):
            out.append((f, m.group(1).lower(), m.group(2), m.group(3)))
    return out


def _titlu_din(text, tip):
    """(nr, an) din titlul propriu, sau None dacă documentul n-are bloc de titlu."""
    m = re.search(CUV[tip] + r"\s+nr\.?\s*(" + NR + r")\s+din\s+\d{1,2}\s+\S+\s+(\d{4})", text, re.I)
    return (m.group(1).replace(".", ""), m.group(2)) if m else None


def test_ANTIVACUU_corpusul_chiar_are_acte():
    a = _acte()
    assert len(a) > 30, "doar %d fisiere cu nume de act — domeniul e gresit" % len(a)


def test_titlul_din_document_confirma_numele_fisierului():
    rele, fara_titlu = [], 0
    for f, tip, nr, an in _acte():
        t = _text(os.path.join(SURSE, f))
        if not t:
            fara_titlu += 1
            continue
        gasit = _titlu_din(t, tip)
        if gasit is None:
            fara_titlu += 1
            continue
        if gasit != (nr, an):
            rele.append("%s: numele spune %s/%s, titlul spune nr. %s din %s"
                        % (f, nr, an, gasit[0], gasit[1]))
    assert not rele, (
        "acte al caror TITLU nu confirma NUMELE fisierului:\n  %s\n\n"
        "Un act sub un nume gresit introduce un temei fals fara sa se aprinda nimic."
        % "\n  ".join(rele))
    assert fara_titlu <= CLICHET_FARA_TITLU, (
        "%d fisiere fara bloc de titlu verificabil (clichet %d) — acoperirea gardului a scazut"
        % (fara_titlu, CLICHET_FARA_TITLU))


def test_niciun_act_nu_e_in_corpus_de_doua_ori():
    dupa_amprenta = {}
    for f in sorted(os.listdir(SURSE)):
        cale = os.path.join(SURSE, f)
        if f.endswith((".sha256", ".json")) or not os.path.isfile(cale):
            continue
        h = hashlib.sha256(io.open(cale, "rb").read()).hexdigest()
        dupa_amprenta.setdefault(h, []).append(f)
    dubluri = [v for v in dupa_amprenta.values() if len(v) > 1]
    assert not dubluri, (
        "acte prezente de mai multe ori, byte-identic:\n  %s\n\n"
        "O corectura pe o copie lasa cealalta neatinsa."
        % "\n  ".join(" = ".join(v) for v in dubluri))


def test_CALIBRARE_potrivirea_chiar_deosebeste_anii():
    """Cazul CONSTRUIT: acelasi numar, alt an, trebuie sa iasa nepotrivit.

    „Legea 1" exista in 2020, 2011, 2005 — daca tiparul n-ar compara ANUL, un fisier numit
    `legea_1_2020` care contine Legea 1/2011 ar trece."""
    assert _titlu_din("LEGE nr. 1 din 6 ianuarie 2020 privind pensiile", "legea") == ("1", "2020")
    assert _titlu_din("LEGE nr. 1 din 11 ianuarie 2011 a educatiei", "legea") == ("1", "2011")
    assert _titlu_din("LEGE nr. 1 din 11 ianuarie 2011 a educatiei", "legea") != ("1", "2020")


def test_CALIBRARE_numarul_cu_separator_de_mii():
    """Instanta reala: „HOTARARE nr. 1.094 din 11 decembrie 2025". Prima forma a tiparului taia la
    prima cifra si citea „nr. 1" — adica ar fi acuzat un fisier corect."""
    assert _titlu_din("HOTĂRÂRE nr. 1.094 din 11 decembrie 2025 privind", "hg") == ("1094", "2025")
    assert _titlu_din("ORDIN nr. 3.562 din 28 iunie 2024 pentru", "opanaf") == ("3562", "2024")
