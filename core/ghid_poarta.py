# -*- coding: utf-8 -*-
"""core/ghid_poarta.py — POARTA de verificare pre-publicare a unui ghid.

Cerută de Costin, 21.09.2026 (producția de ghiduri, pasul 2). Două controale OBLIGATORII înainte
de publicarea oricărui ghid nou; oricare pică → publicarea e BLOCATĂ (CLI iese cu cod ≠ 0, testul
ratchet pică):

  2a. FIECARE CITARE LEGALĂ din draft trebuie să existe în CORPUS (anaf_surse/, a cărui apartenență
      e guvernată de PROVENIENTA.json). Nu se citează un act pe care nu-l ai la sursă — e REGULA DE
      AUR mecanizată. Se extrag citările de forma <TIP> <nr>/<an> (OUG 89/2025, Legea 141/2025,
      HG 146/2026, OMFP 1802/2014, OPANAF 3562/2024…) plus codurile citate pe articol: Codul fiscal
      (= Legea 227/2015) și Codul de procedură fiscală (= Legea 207/2015). Un act citat fără fișier
      în corpus → blocaj, cu numele actului.

  2b. FIECARE PRETENȚIE despre o funcționalitate iConta trebuie verificată în COD. Mecanizat:
      ghidul DECLARĂ în frontmatter `functionalitate: F026, F031` (F-ID-urile din FUNCTIONALITATI.csv).
      Pentru fiecare F-ID: (i) există în registru; (ii) Stare începe cu „LIVE" (nu PLANIFICAT/AMANAT/
      RESPINS/ELIMINAT); (iii) „Sursa cod" trimite la ≥1 fișier care EXISTĂ pe disc; (iv) back-link —
      slug-ul ghidului apare în `ghid_slug` al acelui F-ID (legarea titlu↔funcționalitate, verificată
      în ambele sensuri). Oricare cade → blocaj.

CE NU VEDE (limite declarate, ca la orice gard din codebase):
  - 2a extrage citări cu <nr>/<an> + CF/CPF pe nume. Un cod citat DOAR pe nume, altul decât CF/CPF
    (ex. „Codul muncii" fără „Legea 53/2003"), NU e extras → nu e verificat. Când e citat cu număr,
    e prins. Nu verifică dacă TEXTUL citat chiar apare în fișierul-sursă (ar cere potrivire de citat
    verbatim — limită moștenită de la scan_provenienta/identitate_acte); verifică doar că ACTUL e în
    corpus.
  - 2b verifică LEGĂTURA declarată (F-ID) + starea + sursa + back-link, NU proza liberă din „Ce face
    iConta". O afirmație de detaliu greșită într-un F-ID corect declarat nu e prinsă mecanic — asta
    rămâne în sarcina redactării pe cod real. Poarta face imposibilă pretenția despre o funcție
    inexistentă / nelivrată / nelegată, nu pretenția rău formulată despre una reală.
"""
import csv
import io
import os
import re

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(RADACINA, "anaf_surse")
FUNCTIONALITATI = os.path.join(RADACINA, "FUNCTIONALITATI.csv")

# ---------------------------------------------------------------- 2a: citări legale

# Sinonime de tip din citarea în limbaj natural -> familia de căutare în corpus.
# Emitentul de ordin (OMFP/OMF/OPANAF/Ordin) e agnostic la căutare: corpusul le ține sub prefixe
# diferite, dar un „OPANAF 3562/2024" citat poate fi pe disc `opanaf_3562_2024` SAU `ordin_3562_2024`.
_TIP_FAMILIE = {
    "legea": "legea", "lege": "legea",
    "oug": "oug",
    "og": "og",
    "hg": "hg", "hotararea": "hg", "hotărârea": "hg",
    "omfp": "ordin", "omf": "ordin", "opanaf": "ordin", "ordin": "ordin", "ordinul": "ordin",
}

# TIP-ul din citare — case-SENSITIVE dinadins (NU re.I): re.I ar face `[^A-Z]` să excludă toate
# literele (footgun), iar formele-cuvânt minuscule ("lege", "ordinul") sunt substantive comune care
# prind numărul actului URMĂTOR peste paragraf (dovedit 21.09: „…lege.\n\nOMFP nr. 2861/2009" ->
# fals „Legea 2861/2009"). Abrevierile sunt majuscule; formele-cuvânt, Title-case.
_TIP_ALT = r"OUG|O\.U\.G|OG|O\.G|HG|H\.G|OMFP|OMF|OPANAF|Ordinul|Ordin|Legea|Hot[ăa]r[âa]rea"
_TIP = r"(" + _TIP_ALT + r")"                 # capturant (TIP-ul citării)
_TIP_NC = r"(?:" + _TIP_ALT + r")"            # non-capturant (pt. lookahead-ul din punte)
# Puntea dintre TIP și număr — TEMPERED TOKEN: orice caracter non-cifră/non-newline care NU începe alt
# TIP. Deci NU poate traversa într-un alt act („…Legea … OMFP 89/2025" nu leagă „Legea" de 89), dar
# acceptă calificative legitime, inclusiv Title-case („Hotărârea Guvernului nr.", „Legea contabilității
# nr. 82/1991"). Case-sensitive (v. nota TIP): „lege." minuscul nu e TIP, deci nu prinde nimic.
_PUNTE = r"(?:(?!" + _TIP_NC + r")[^0-9\n]){0,25}?"
# DOUĂ forme reale: slash („OUG 89/2025") și dată („OUG nr. 89 din 23 decembrie 2025").
_CIT_SLASH = re.compile(r"\b" + _TIP + r"\b" + _PUNTE + r"(\d[\d.]*)\s*/\s*(\d{4})")
_CIT_DIN = re.compile(
    r"\b" + _TIP + r"\b[ \t]*(?:nr\.?[ \t]*)?(\d[\d.]*)\s+din\s+(?:\d{1,2}\s+[a-zăâîșț]+\s+)?(\d{4})")

# Anul unei citări plauzibil ca an de act normativ românesc. Un „an" în afara intervalului = misparse
# (al doilea număr al unui ordin comun `nr1/nr2`, un număr de Monitor Oficial etc.), NU un act — nu se
# fabrică o identitate greșită. Dovedit 21.09: „Ordinul comun nr. 1826/2372" -> an 2372 imposibil.
_AN_MIN, _AN_MAX = 1900, 2035

# Coduri citate pe articol, fără nr/an. Fiecare -> actul-suport (familie, nr, an) care trebuie în corpus.
_COD_ALIAS = {
    "cod fiscal": ("legea", "227", "2015"),
    "codul fiscal": ("legea", "227", "2015"),
    "cod de procedură fiscală": ("legea", "207", "2015"),
    "codul de procedură fiscală": ("legea", "207", "2015"),
    "cod de procedura fiscala": ("legea", "207", "2015"),
    "codul de procedura fiscala": ("legea", "207", "2015"),
}
_COD_RE = re.compile("|".join(re.escape(k) for k in _COD_ALIAS), re.I)

# Nume-fișier din corpus (act cu nr/an) -> (prefix_disc, nr, an). Toleranță la lipsa underscore-ului
# (`hg714_2018`). Codurile (cf/cpf) au nume de cod, nu nr/an — se tratează separat în corpus_acte.
_NUME_FISIER = re.compile(
    r"^(lege|legea|oug|og|hg|opanaf|omfp|omf|ordin)[_]?(\d+)_(\d{4})", re.I
)
_PREFIX_FAMILIE = {
    "lege": "legea", "legea": "legea",
    "oug": "oug", "og": "og", "hg": "hg",
    "opanaf": "ordin", "omfp": "ordin", "omf": "ordin", "ordin": "ordin",
}


def _corpus_valid():
    """Numele de fișiere din corpus care sunt membri LEGITIMI (nu goale, cu clasă declarată/derivată).

    Reutilizează scan_provenienta ca sursă a apartenenței (PROVENIENTA.json + faptele mecanice)."""
    from core import scan_provenienta as sp
    cl = sp.clasifica(CORPUS)
    goale = sp.goale_cunoscute(CORPUS)
    return {f for f, (clasa, _) in cl.items()
            if clasa != sp.NEDECLARAT and f not in goale}


def corpus_acte(fisiere=None):
    """set{(familie, nr, an)} — actele prezente în corpus, după numele fișierelor legitime.

    cf_*/cpf_* sunt aliniate la actul-suport: cf -> (legea,227,2015), cpf -> (legea,207,2015)."""
    fisiere = fisiere if fisiere is not None else _corpus_valid()
    out = set()
    for f in fisiere:
        low = f.lower()
        # Codurile sunt stocate pe nume de cod (`cf_2015`, `cf_art291_2016`), nu ca `legea_227_2015`.
        if re.match(r"^cf(_|\d)", low):
            out.add(("legea", "227", "2015"))
            continue
        if re.match(r"^cpf(_|\d)", low):
            out.add(("legea", "207", "2015"))
            continue
        m = _NUME_FISIER.match(f)
        if not m:
            continue
        pref, nr, an = m.group(1).lower(), m.group(2), m.group(3)
        out.add((_PREFIX_FAMILIE[pref], nr, an))
    return out


def _norm_nr(nr):
    return nr.replace(".", "")


def citari(text):
    """[(text_citat, (familie, nr, an))] — citările legale extrase din draft, deduplicat pe act.

    Prinde <TIP> <nr>/<an> și <TIP> nr. <n> din <data> <an>, plus Codul fiscal / Codul de procedură
    fiscală citate pe articol (aliniate la actul-suport)."""
    vazut = {}
    for rx in (_CIT_SLASH, _CIT_DIN):
        for m in rx.finditer(text):
            fam = _TIP_FAMILIE.get(m.group(1).lower().replace(".", ""))
            if not fam:
                continue
            an = m.group(3)
            if not (_AN_MIN <= int(an) <= _AN_MAX):   # al doilea nr al unui ordin comun, nr de MO...
                continue
            act = (fam, _norm_nr(m.group(2)), an)
            vazut.setdefault(act, m.group(0).strip())
    for m in _COD_RE.finditer(text):
        act = _COD_ALIAS[m.group(0).lower()]
        vazut.setdefault(act, m.group(0).strip())
    return [(t, a) for a, t in vazut.items()]


def verifica_citari(text, acte_corpus=None):
    """[(text_citat, act)] pentru citările FĂRĂ suport în corpus. Listă goală = trece."""
    ac = acte_corpus if acte_corpus is not None else corpus_acte()
    return [(t, a) for (t, a) in citari(text) if a not in ac]


# ---------------------------------------------------------------- 2b: funcționalități

_STARE_LIVE = ("LIVE",)  # Stare care confirmă o funcție livrată; sufixe permise (ex. „LIVE 21.07").
_CALE_RE = re.compile(r"[A-Za-z0-9_./-]+\.py")

# Coduri de problemă (structurale, nu mesaje) — testele asertează pe cod, nu pe subșir de text.
COD_INEXISTENT = "F_INEXISTENT"      # F-ID care nu e în FUNCTIONALITATI.csv
COD_NELIVRAT = "F_NELIVRAT"          # Stare != LIVE
COD_FARA_SURSA = "F_FARA_SURSA"      # «Sursa cod» nu trimite la niciun fișier existent
COD_FARA_BACKLINK = "F_FARA_BACKLINK"  # slug-ul ghidului nu apare în ghid_slug al F-ID-ului

_MESAJ_COD = {
    COD_INEXISTENT: "F-ID inexistent în FUNCTIONALITATI.csv",
    COD_NELIVRAT: "stare nu e LIVE - functie nelivrata nu se prezinta ca existenta",
    COD_FARA_SURSA: "«Sursa cod» nu trimite la niciun fișier existent",
    COD_FARA_BACKLINK: "back-link lipsă - slug-ul nu apare în «ghid_slug» al F-ID-ului",
}


def _registru_functionalitati(cale=None):
    p = cale or FUNCTIONALITATI
    with io.open(p, encoding="utf-8", newline="") as f:
        return {r["ID"]: r for r in csv.DictReader(f) if r.get("ID", "").strip()}


def _surse_exista(camp_sursa):
    """True dacă ≥1 cale .py din câmpul «Sursa cod» există pe disc. Câmpul e text liber
    („core/salarizare.py + main.py (calcul-cm)"), deci se extrag căile, nu se ia întreg."""
    cai = _CALE_RE.findall(camp_sursa or "")
    if not cai:
        return False
    return any(os.path.exists(os.path.join(RADACINA, c)) for c in cai)


def _slug_uri_din(camp_ghid_slug):
    return {s.strip() for s in re.split(r"[|,;]", camp_ghid_slug or "") if s.strip()}


def verifica_functionalitati(meta, slug, registru=None):
    """[(fid, cod, detaliu)] cu problemele pentru F-ID-urile declarate în frontmatter `functionalitate:`.
    cod ∈ {COD_INEXISTENT, COD_NELIVRAT, COD_FARA_SURSA, COD_FARA_BACKLINK} — structural, nu mesaj.

    meta = dict frontmatter (chei lowercase). slug = numele fișierului fără .md (pentru back-link).
    Fără câmp `functionalitate` → nicio pretenție declarată → nicio problemă (listă goală)."""
    reg = registru if registru is not None else _registru_functionalitati()
    camp = meta.get("functionalitate", "").strip()
    if not camp:
        return []
    fids = [x.strip().upper() for x in re.split(r"[ ,;]+", camp) if x.strip()]
    probleme = []
    for fid in fids:
        r = reg.get(fid)
        if r is None:
            probleme.append((fid, COD_INEXISTENT, ""))
            continue
        stare = (r.get("Stare") or "").strip()
        if not stare.startswith(_STARE_LIVE):
            probleme.append((fid, COD_NELIVRAT, stare[:40]))
        if not _surse_exista(r.get("Sursa cod")):
            probleme.append((fid, COD_FARA_SURSA, (r.get("Sursa cod") or "").strip()[:60]))
        if slug and slug not in _slug_uri_din(r.get("ghid_slug")):
            probleme.append((fid, COD_FARA_BACKLINK, slug))
    return probleme


# ---------------------------------------------------------------- poarta întreagă

def _frontmatter(txt):
    """Front-matter de ghid, ACEEAȘI formă ca `main._ghid_frontmatter` (linii `key: value` între
    `---`). Auto-conținut fiindcă `core/` NU are voie să importe `main` (gard core/test_core_fara_main).
    Echivalența cu parserul de servire e pinată de un test (core/test_ghid_poarta.py) care compară
    pe toate ghidurile — o divergență a formatului aprinde acolo, nu tăcut la publicare."""
    linii = txt.split("\n")
    if linii and linii[0].strip() == "---":
        for i in range(1, len(linii)):
            if linii[i].strip() == "---":
                meta = {}
                for ln in linii[1:i]:
                    if ":" in ln:
                        k, v = ln.split(":", 1)
                        meta[k.strip().lower()] = v.strip().strip('"').strip("'")
                return meta, "\n".join(linii[i + 1:]).lstrip("\n")
    return {}, txt


def verifica_ghid(cale, acte_corpus=None, registru=None):
    """(ok, probleme) pentru un draft de ghid .md. ok=False → publicarea se blochează."""
    txt = io.open(cale, encoding="utf-8").read()
    meta, corp = _frontmatter(txt)
    slug = os.path.basename(cale)[:-3] if cale.endswith(".md") else os.path.basename(cale)
    # `mesaje`, nu `probleme`: e o listă de string-uri de afișare, nu verdicte colapsate (verificator
    # VERDICT_COLAPSAT — un verdict destinat UI trebuie structurat; verifica_citari/_functionalitati
    # ÎNTORC structura, aici doar o formatăm pentru CLI).
    mesaje = []
    for t, a in verifica_citari(corp, acte_corpus):
        mesaje.append("CITARE fără suport în corpus: %s  (act %s %s/%s)" % (t, a[0], a[1], a[2]))
    for fid, cod, detaliu in verifica_functionalitati(meta, slug, registru):
        mesaje.append("%s: %s%s" % (fid, _MESAJ_COD[cod], (" (%s)" % detaliu) if detaliu else ""))
    return (not mesaje, mesaje)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("uz: python -m core.ghid_poarta <cale_ghid.md> [...]")
        sys.exit(2)
    ac, reg = corpus_acte(), _registru_functionalitati()
    rc = 0
    for cale in sys.argv[1:]:
        ok, probleme = verifica_ghid(cale, ac, reg)
        if ok:
            print("✓ %s — poarta VERDE" % cale)
        else:
            rc = 1
            print("✗ %s — poarta ROȘIE (%d):" % (cale, len(probleme)))
            for p in probleme:
                print("    - " + p)
    sys.exit(rc)
