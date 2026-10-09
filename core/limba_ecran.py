# -*- coding: utf-8 -*-
"""core/limba_ecran.py — ce e greșit în TEXTUL AFIȘAT pe un ecran, citit din browser (nu din sursă).

Comanda Costin 09.10.2026 („Retest 2”, pct.2, verbatim în DECIZII): „Pct.14 nu e închis. […] Decizie: verificarea se face pe ecranul
afișat, cu valorile din date și din enumerări, nu pe șirurile din codul sursă.” Gardul de sursă (`core/test_text_afisat_limbaj.py`)
nu vede o valoare din bază sau dintr-o enumerare afișată brut („incasare_client”, „liniara”), nici o sumă formatată de mână
(„1000.00”), nici textul compus în ecran din bucăți. Modulul ăsta judecă textul pe care îl citește omul; îl folosește
`frontend_test/vizual/text_ecran_scan.py` (browserul) și îl probează `core/test_limba_ecran.py` (fără browser).

Felurile de defect (fiecare cu fragmentul găsit):
  cod          — `nume_cu_underscore`, `modul.atribut`, `COD_CU_UNDERSCORE`, săgeți `->`, `$ $`, `x=1`, „GRI”/„NEVERIFICAT” ca stări interne,
                 trimiteri la proveniența internă („decizia Costin”, „pct.4)” după o decizie), comenzi („-v D406 fisier.xml”);
  diacritice   — cuvinte care cer obligatoriu diacritică (dicționarul gardului de sursă + cele găsite pe ecrane);
  majuscule    — un cuvânt scris integral cu majuscule care nu e acronim;
  suma         — o sumă cu punct zecimal („1000.00”), nu în forma românească „1.000,00”;
  data         — o dată ISO („2026-10-05”) în text;
  perioada     — o perioadă în altă formă decât „LL/AAAA” (luna) sau „T3/2026” (trimestrul): „03.2026”, „iun 2026”, „T3 2026”;
  acord        — „1 parteneri”, „1 facturi” (numeral 1 cu plural);
  abreviere    — prescurtări de programator („fact.vânz”), nu cele legale („art.”, „alin.”, „nr.”);
  jargon       — cuvinte de dezvoltator („rânduri persistate”, „amprenta notei”, „null”).
LIMITĂ declarată: un text greșit care nu are nicio formă de mai sus („Câmpul e liber”, „Contă analitice”) nu se prinde aici — de aceea
proba cere și captura ecranului citită de om (cerința E18 a comenzii).

Valorile introduse de om (numele firmei, al partenerului, al articolului) nu sunt textul aplicației: apelantul le dă în `date_excluse`
și se scot din text înainte de judecată.
"""
import re

from core.test_text_afisat_limbaj import ACRONIME, AFARA, AMBIGUE, LEXICON, MAJ_IN_CUVANT, SCURTE, TRIGGERE

#: forme fără diacritice găsite pe ecrane la retestul 09.10 (pe lângă dicționarul gardului de sursă)
TRIGGERE_ECRAN = {"initial", "initiala", "initiale", "varsat", "varsata", "liniara", "incasare", "incasari", "platit", "platita"}
_CUV = re.compile(r"[A-Za-zĂÂÎȘȚăâîșțŞŢşţ]+")
_SNAKE = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")
_COD_MARE = re.compile(r"\b[A-Z][A-Z0-9]*_[A-Z0-9_]+\b")
_PUNCT = re.compile(r"\b(?!(?:art|alin|lit|pct|nr|ex|etc|resp|max|min|instr|rd|cf|cca|str|bl|sc|ap|et|jud|tel|cod|pag|fact|op)\.)"
                    r"[a-z_][a-z0-9_]*\.[a-z_][A-Za-z0-9_]{2,}\b")
_ATRIB = re.compile(r"\b[a-z_]{2,}=\S")
_SAGEATA = re.compile(r"(?<![<-])->(?!>)|\$ \$")
_INTERN = re.compile(r"\b(?:GRI|NEVERIFICAT[EĂ]?|ROSU|VERDE)\b|decizia Costin|\bfisier\.xml\b|-v [Dd]\d{3}\b")
_MAJ = re.compile(r"(?<![\w\"'«„“])([A-ZĂÂÎȘȚŞŢ]{2,})(?![\w\"'»”])")
_SUMA = re.compile(r"(?<![\d.,])\d{3,}\.\d{2}(?![\d.,])")
_DATA = re.compile(r"\b(?:19|20)\d\d-[01]\d-[0-3]\d\b")
_PER_PUNCT = re.compile(r"(?<![\d.])(?:0[1-9]|1[0-2])\.(?:19|20)\d\d\b")
_PER_LUNA = re.compile(r"\b(?:ian|feb|mar|apr|iun|iul|aug|sep|oct|noi|dec)\.? (?:19|20)\d\d\b")
_PER_TRIM = re.compile(r"\bT[1-4](?!/(?:19|20)\d\d)\b")
_ABREV = re.compile(r"\b(?!(?:art|alin|lit|pct|nr|rd|ex|cf|str|jud|tel)\.)[a-zăâîșț]{2,5}\.[a-zăâîșț]{3,6}\b")
#: jargon de programator găsit pe ecrane (retest 09.10): ce înseamnă pentru dezvoltator, nu pentru contabil
_JARGON = re.compile(r"\b(?:persistat[eăa]?|amprent[aăei]+|payload|endpoint|hash|upsert|fallback|tenant|schema|cache|null|None|"
                     r"True|False|stub|parsabil[aăe]?|neparsabil[aăe]?)\b", re.I)
_ACORD = re.compile(r"\b1 (?:parteneri|facturi|note|conturi|clienți|furnizori|operațiuni|luni|zile|rânduri|declarații|firme|linii|"
                    r"documente|perioade|salariați|articole)\b")
EXCEPTII_ACRONIM = {"RO", "UE", "CF", "MF", "PF", "PJ", "IC", "ID", "OK", "TVA", "CNP", "CUI", "CIF", "IBAN", "PDF", "XML", "BNR", "SPV",
                    "ANAF", "DUK", "SAGA", "CAEN", "OMFP", "OPANAF", "CASS", "CAS", "CAM", "UIT", "COR", "REGES", "NIR", "SRL", "SA",
                    "PFA", "II", "IF", "ONG", "C&D", "CD", "ZIP", "CSV", "GDPR", "HG", "OUG", "MO", "AMEF", "HORECA", "SAF", "SAFT",
                    "D", "C", "SI", "SF", "SC", "RC"}


#: fișierele care decid ce e defect pe ecran: dacă se schimbă vreunul, scanul ecranelor trebuie refăcut (`core/test_text_ecran.py`)
FISIERE_INSTRUMENT = ("core/limba_ecran.py", "core/test_text_afisat_limbaj.py", "core/lexicon_diacritice.json",
                      "frontend_test/vizual/text_ecran_scan.py")


def instrument_hash():
    import hashlib
    import os
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    h = hashlib.sha256()
    for f in FISIERE_INSTRUMENT:
        h.update(f.encode())
        with open(os.path.join(rad, f), "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()[:16]


def _fara_date(text, date_excluse):
    for v in sorted({str(x) for x in (date_excluse or ()) if x and len(str(x)) >= 3}, key=len, reverse=True):
        text = text.replace(v, " ")
    return text


def defecte(text, date_excluse=()):
    """[(fel, fragment)] pentru textul afișat (după scoaterea valorilor introduse de om)."""
    t = _fara_date(text or "", date_excluse)
    out = []
    for fel, rx in (("cod", _SNAKE), ("cod", _COD_MARE), ("cod", _PUNCT), ("cod", _ATRIB), ("cod", _SAGEATA), ("cod", _INTERN),
                    ("abreviere", _ABREV), ("jargon", _JARGON), ("suma", _SUMA), ("data", _DATA), ("perioada", _PER_PUNCT), ("perioada", _PER_LUNA), ("perioada", _PER_TRIM),
                    ("acord", _ACORD)):
        out += [(fel, m.group(0)) for m in rx.finditer(t)]
    are_diac = any(c in "ăâîșțşţĂÂÎȘȚŞŢ" for c in t)
    for m in _CUV.finditer(t):
        w = m.group(0)
        low = w.lower()
        if ((low in (TRIGGERE | TRIGGERE_ECRAN) and not (are_diac and low in AMBIGUE) and w == low)
                or (low in LEXICON and (w == low or w == low.capitalize()))):   # lexiconul corpusului (Retest 2 pct.2)
            out.append(("diacritice", w))
    out += [("diacritice", m.group(0)) for m in AFARA.finditer(t)]
    out += [("majuscule", m.group(0)) for m in MAJ_IN_CUVANT.finditer(t)]
    for m in _MAJ.finditer(t):
        w = m.group(1)
        if w in ACRONIME or w in EXCEPTII_ACRONIM or re.fullmatch(r"[IVXLCDM]+", w) or re.fullmatch(r"[A-Z]\d*", w):
            continue
        if len(w) >= 4 or w in SCURTE:
            out.append(("majuscule", w))
    return out
