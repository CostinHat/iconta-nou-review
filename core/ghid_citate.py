# -*- coding: utf-8 -*-
"""core/ghid_citate.py — citatele din casetele de temei ale ghidurilor publice, confruntate VERBATIM cu sursele oficiale locale.

Comanda Costin 13.10.2026 (răspunsul la §6 al raportului COMANDA_13_10, pct.3, verbatim în DECIZII): „pune temeiul din lege, citat
verbatim din sursă verificată. Unde nu există normă aplicabilă, nu pune caseta. Nu inventa temeiuri.” Sursa verificată = textele din
`anaf_surse/*.txt` (descărcate din Portalul Legislativ / MO / ANAF, cu amprentă sha256; cele marcate `GRESIT_` sunt excluse).

Un citat e textul dintre „ și ” (sau " ") de pe un rând al unei casete `::: ghid-temei`. Se caută în sursă după normalizare: spațiile
comasate, ghilimelele și apostroafele unificate, ş/ţ cu sedilă = ș/ț cu virgulă, cratimele unificate. Un citat cu „…” / „[...]” (omisiune)
se verifică pe fiecare fragment de cel puțin 12 caractere. LIMITA: verifică existența textului în sursă, nu și că articolul numit
lângă el e cel corect (atribuirea rămâne la autor și la recitire).
"""
import functools
import glob
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SURSE = os.path.join(RAD, "anaf_surse")
_BLOC = re.compile(r"^:::\s*ghid-temei[^\n]*\n(.*?)^:::\s*$", re.S | re.M)
#: Un citat = pe UN rând al casetei, de la prima ghilimea de deschidere („ “ sau ") până la ULTIMA ghilimea de închidere de pe rând
#: (” “ sau "). Așa se văd și citatele închise cu ghilimea dreaptă („…") și cele cu ghilimele drepte interioare („… "taxare inversă" …”).
#: [13.10.2026] Două forme anterioare greșeau: prima tăia citatul la prima " dinăuntru (verifica numai începutul — verde fals), a doua
#: nu vedea deloc citatele „…" (unghi mort: 1.494 de citate văzute din ~7.300).
_OMISIUNE = re.compile(r"\s*(?:\[\s*(?:…|\.\.\.)\s*\]|\(\s*(?:…|\.\.\.)\s*\)|…|\.\.\.)\s*")
_DESCHIDE = "„“\""
_INCHIDE = "”“\""


def _citate_rand(rand):
    i = min((rand.find(c) for c in _DESCHIDE if c in rand), default=-1)
    if i < 0:
        return None
    j = max(rand.rfind(c) for c in _INCHIDE)
    return rand[i + 1:j].strip() if j > i + 1 and len(rand[i + 1:j].strip()) >= 12 else None


def normal(s):
    s = s.replace("ş", "ș").replace("ţ", "ț").replace("Ş", "Ș").replace("Ţ", "Ț")
    s = re.sub(r"[„”“\"«»]", "\"", s)
    s = re.sub(r"[’‘`´]", "'", s)
    s = re.sub(r"[‐‑‒–—−]", "-", s)
    s = s.replace(" ", " ").replace("­", "")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r" (?=[,.;:)\]])", "", s)          # textul din HTML-ul portalului are spațiu înaintea punctuației („317 , care”)
    s = re.sub(r"(?<=[(\[]) ", "", s)
    return s.strip().lower()


@functools.lru_cache(maxsize=1)
def corpus():
    """Textul normalizat al tuturor surselor (fără cele `GRESIT_`) — o singură citire pe proces."""
    parti = []
    for f in sorted(glob.glob(os.path.join(SURSE, "*.txt"))):
        if not os.path.basename(f).startswith("GRESIT_"):
            parti.append(normal(io.open(f, encoding="utf-8", errors="replace").read()))
    return "\n".join(parti)


def citate(text):
    """Citatele din casetele de temei ale unui ghid (textul dintre ghilimele, pe rând)."""
    out = []
    for b in _BLOC.finditer(text):
        for rand in b.group(1).splitlines():
            if rand.lstrip().startswith(("—", "–", "-", "(")):          # rândul de atribuire „— act … (sursă: …)” nu e citat
                continue
            c = _citate_rand(rand)
            if c:
                out.append(c)
    return out


def neregasite(text, corp=None):
    """Citatele care NU se regăsesc literal în sursele oficiale locale."""
    corp = corpus() if corp is None else corp
    rele = []
    for c in citate(text):
        fragmente = [normal(x).strip(" .;:,") for x in _OMISIUNE.split(c)]
        fragmente = [x for x in fragmente if len(x) >= 12]
        if not fragmente or any(x not in corp for x in fragmente):
            rele.append(c)
    return rele


def permise(slug):
    """Câte citate neliterale are voie ghidul `slug` (clichetul `core/clichet_citate_ghid.json`, măsurat la 13.10.2026); un ghid nou: 0."""
    import json
    with io.open(os.path.join(RAD, "core", "clichet_citate_ghid.json"), encoding="utf-8") as f:
        return json.load(f)["fisiere"].get(slug, 0)
