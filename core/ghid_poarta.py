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
    # [13.10.2026, comanda Costin — răspunsul la §6 COMANDA_13_10 pct.3: „citat verbatim din sursă verificată … Nu inventa temeiuri.”]
    # un citat de temei care nu se regăsește literal în anaf_surse oprește publicarea; ghidurile vechi au voie numai cu cele din clichet
    from core import ghid_citate as _gc
    rele = _gc.neregasite(txt)
    if len(rele) > _gc.permise(slug):
        mesaje += ["CITAT care nu se regăsește literal în sursele oficiale locale: „%s”" % c[:120] for c in rele]
    # [17.5-C9, C-ghid pct.4] valoarea fiscală datată și exemplul ei, față de registru (`verifica_valori_fiscale`)
    mesaje += [_mesaj_valoare(slug, a) for a in verifica_valori_fiscale(corp)]
    return (not mesaje, mesaje)


# ---------------------------------------------------------------- 3: valorile fiscale datate (17.5-C9, C-ghid pct.4)
#
# Regula (CLAUDE.md §10): pentru orice ghid cu valoare fiscală datată se identifică regimul, evenimentul fiscal, perioada și cheia din
# registru (`core.common.COTE`); valoarea și exemplul se compară cu registrul; diferența oprește publicarea. Cheia judecată aici:
# `impozit_dividend` (cota după data DISTRIBUIRII: hotărârea fixează anul). O frază intră în judecată când e despre dividende
# (`dividend` / `distribu`) și are o cotă; nu intră frazele despre lichidare (art.97 alin.(5), altă cheie) și cele despre art.78.
# Anul frazei: primul an de după «distribu…» / «hotăr…» (anul profitului sau al plății nu fixează cota); fără cuvântul-cheie, singurul
# an al frazei. Interimarele urmează aceeași regulă (cota anului distribuirii interimare, păstrată la regularizare: OUG 156/2024
# art.LXV alin.(5), Legea 141/2025 art.VII alin.(2)). Mai multe cote într-o frază: fiecare cu anul cel mai apropiat.
# Trei verificări în plus: o frază care neagă o cotă din registru („niciodată 10%”), lista cotelor istorice fără ani (trebuie să fie
# exact mulțimea registrului) și aritmetica exemplului (impozit = brut × cotă, net = brut − impozit, diferența dintre impozite).
# LIMITE DECLARATE: o cotă scrisă în litere („zece la sută”) și o frază fără an nu se judecă; regimul PJ scutit nu se recunoaște
# (ghidul îl spune ca verificare separată).

_CHEIE_DIVIDEND = "impozit_dividend"
_RE_ACT = re.compile(r"\b\d{1,5}/\d{4}\b")                                   # „156/2024”: anul actului nu e perioada afirmației
_RE_MO = re.compile(r"\([^)]*Monitorul[^)]*\)")
_RE_AN = re.compile(r"\b(20[0-4]\d)\b")
_RE_COTA = re.compile(r"(?<![\d.,])(\d{1,2})(?:[,.]\d+)?\s*%")
_RE_CONTEXT = re.compile(r"dividend|distribu", re.I)
_RE_EXCLUS = re.compile(r"lichidar|partaj|dob[âa]nd|reinvest|elemente similare|impozitul pe profit|impozitare (?:integral|de \d)|art\.\s*(?:78|53|224)\b|nerezident", re.I)
#: frazele care descriu o greșeală („se aplică din inerție cota veche…”) citează intenționat cota greșită: nu se judecă (limită declarată)
_RE_GRESEALA = re.compile(r"ignor|gre[șs]|confund|iner[țt]ie|cota veche|[îi]n loc de|eroare|capcan|nu presupune|nu recalcul|f[ăa]r[ăa] s[ăa] (?:se )?verific", re.I)
#: lista cotelor istorice („cotele au fost 5%, 8% și 16%”) se judecă numai ca istoric al dividendelor, nu când fraza amestecă alte impozite
_RE_ISTORIC = re.compile(r"istoric|au fost|cotele|valori", re.I)
_RE_ALTE_IMPOZITE = re.compile(r"micro|venitur|profit", re.I)
_RE_INTERIMAR = re.compile(r"interimar|regulariz", re.I)
#: anul legat strâns de cotă: „16% în 2026”, „8% (de la 2023)”, „5% (2016–2022)”, „10% pentru distribuirile din 2025”; „2025 (10%)”
_RE_AN_DUPA = re.compile(r"^\s*\)?\s*(?:\(|—|–|-|,)?\s*(?:de la|[îi]n|din|pentru|[îi]ncep[âa]nd cu|pentru distribuirile din)?\s*"
                         r"(?:\d{1,2}\s+[a-zăâîșț]+\s+|\d{2}\.\d{2}\.)?(20[0-4]\d)\b")
_RE_AN_INAINTE = re.compile(r"(20[0-4]\d)(?:\s*[–-]\s*20[0-4]\d)?\s*(?:\(|:|→|->)?\s*$")
_RE_CHEIE_AN = re.compile(r"distribu|hot[ăa]r[âa]", re.I)
_RE_NEGARE = re.compile(r"niciodat[ăa]|nu a existat|n-a existat|nu exist[ăa]", re.I)
_RE_SUMA = r"(\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?"


def _fraze(corp):
    """Frazele corpului: liniile (și elementele de listă), tăiate la sfârșit de propoziție. Fără marcajul Markdown."""
    out = []
    for linie in corp.split("\n"):
        t = re.sub(r"[*_`]", "", linie).strip(" -\t")
        if not t:
            continue
        out += [f.strip() for f in re.split(r"(?<=[.!?])\s+(?=[A-ZĂÂÎȘȚ„])", t) if f.strip()]
    return out


def _curata(fraza):
    return _RE_ACT.sub(" ", _RE_MO.sub(" ", fraza))


def _cote_registru(cote=None):
    from core import common as _c
    return sorted((cote if cote is not None else _c.COTE)[_CHEIE_DIVIDEND], key=lambda r: r[0])


def _cota_la(an, cote):
    """Cota registrului (procent întreg ca text, ex. „10”) pentru o distribuire din anul `an`, sau None când anul e înaintea registrului."""
    from datetime import date
    val = None
    for din, v, _t in cote:
        if date(an, 12, 31) >= din:
            val = v
    if val is None:
        return None
    return format((val * 100).normalize(), "f")


def _an_strans(cur, cote_f, i):
    """Anul legat strâns de a i-a cotă a frazei (imediat după ea sau imediat înainte), fără să treacă peste altă cotă; None altfel."""
    p = cote_f[i][1]
    m_c = _RE_COTA.match(cur, p)
    sfarsit = m_c.end() if m_c else p
    urm = cote_f[i + 1][1] if i + 1 < len(cote_f) else len(cur)
    m = _RE_AN_DUPA.match(cur[sfarsit:min(urm, sfarsit + 45)])
    if m:
        return int(m.group(1))
    prec = (_RE_COTA.match(cur, cote_f[i - 1][1]).end()) if i > 0 else 0
    m = _RE_AN_INAINTE.search(cur[max(prec, p - 16):p])
    return int(m.group(1)) if m else None


def _an_frazei(fraza, ani):
    m = _RE_CHEIE_AN.search(fraza)
    if m:
        dupa = [a for a in ani if a[1] >= m.start()]
        inainte = [a for a in ani if a[1] < m.start()]
        if dupa:
            return dupa[0][0]
        if inainte:
            return inainte[-1][0]
    distincti = {a[0] for a in ani}
    return next(iter(distincti)) if len(distincti) == 1 else None


def verifica_valori_fiscale(corp, cote=None):
    """[17.5-C9, C-ghid pct.4] Afirmațiile din ghid care contrazic registrul cheii `impozit_dividend`: listă de dict-uri
    {afirmatie, perioada, asteptat, gasit} (goală = conform). PURĂ (registrul se poate da, pentru probe pe copie)."""
    reg = _cote_registru(cote)
    valori = {format((v * 100).normalize(), "f") for _d, v, _t in reg}
    abateri = []
    for fraza in _fraze(corp):
        if not _RE_CONTEXT.search(fraza) or _RE_EXCLUS.search(fraza):
            continue
        cur = _curata(fraza)
        cote_f = [(m.group(1), m.start()) for m in _RE_COTA.finditer(cur)]
        if not cote_f:
            continue
        ani = [(int(m.group(1)), m.start()) for m in _RE_AN.finditer(cur)]
        neg = _RE_NEGARE.search(cur)
        if neg:
            for c, _p in cote_f:
                if c in valori and 0 <= _p - neg.end() <= 15:
                    abateri.append({"afirmatie": fraza, "perioada": "-", "asteptat": "cota de %s%% există în registru" % c,
                                    "gasit": "fraza neagă cota de %s%%" % c})
            continue
        if not ani:
            distincte = {c for c, _p in cote_f}
            if len(distincte) >= 3 and _RE_ISTORIC.search(cur) and not _RE_ALTE_IMPOZITE.search(cur) and distincte != valori:
                abateri.append({"afirmatie": fraza, "perioada": "toate", "asteptat": "cotele registrului: %s" % ", ".join(
                    "%s%%" % v for v in sorted(valori, key=float)), "gasit": ", ".join("%s%%" % v for v in sorted(distincte, key=float))})
            continue
        if _RE_GRESEALA.search(cur):
            continue
        perechi = []
        for i, (c, p) in enumerate(cote_f):
            an = _an_strans(cur, cote_f, i)
            if an is None and len(cote_f) == 1:
                an = _an_frazei(cur, ani)
            if an is not None:
                perechi.append((an, c))
        interimar = bool(_RE_INTERIMAR.search(cur))
        for an, c in perechi:
            asteptat = _cota_la(an, reg)
            # interimarele păstrează cota anului situațiilor interimare la regularizarea din anul următor
            if interimar and c == _cota_la(an - 1, reg):
                continue
            if asteptat != c:
                abateri.append({"afirmatie": fraza, "perioada": "distribuire %d" % an,
                                "asteptat": ("%s%%" % asteptat) if asteptat else "perioadă fără valoare în registru", "gasit": "%s%%" % c})
    abateri += _verifica_exemple(corp, reg)
    return abateri


def _num(s):
    from decimal import Decimal
    return Decimal(s.replace(".", "").replace(",", "."))


def _verifica_exemple(corp, reg):
    """Aritmetica exemplelor cu dividende din blocurile `::: ghid-exemplu`: impozit = brut × cotă (cota anului din linie, din registru),
    net = brut − impozit, diferența spusă = diferența impozitelor."""
    from decimal import Decimal, ROUND_HALF_UP
    abateri = []
    for bloc in re.findall(r":::\s*ghid-exemplu(.*?):::", corp, re.S):
        if not _RE_CONTEXT.search(bloc):
            continue
        b = re.sub(r"[*_`]", "", bloc)
        mb = re.search(_RE_SUMA + r"\s*lei(?:\s+brut|\s+profit)", b)
        if not mb:
            continue
        brut = _num(mb.group(1))
        impozite = []
        for fraza in _fraze(b):
            mi = re.search(r"impozit(?:ul)?\s+(\d{1,2})\s*%\s*=\s*" + _RE_SUMA + r"\s*lei", fraza)
            if not mi:
                continue
            cota = Decimal(mi.group(1))
            imp = _num(mi.group(2))
            impozite.append(imp)
            impozit_asteptat = (brut * cota / 100).quantize(Decimal("0.01"), ROUND_HALF_UP)   # impozitul pe dividende al exemplului (nu TVA)
            if imp != impozit_asteptat:
                abateri.append({"afirmatie": fraza, "perioada": "exemplu", "asteptat": "impozit %s lei" % _lei(impozit_asteptat),
                                "gasit": "impozit %s lei" % _lei(imp)})
            mn = re.search(r"(?:net|primește|primeste)\D{0,40}?" + _RE_SUMA + r"\s*lei", fraza[mi.end():])
            if mn and _num(mn.group(1)) != brut - imp:
                abateri.append({"afirmatie": fraza, "perioada": "exemplu", "asteptat": "net %s lei" % _lei(brut - imp),
                                "gasit": "net %s lei" % _lei(_num(mn.group(1)))})
        for fraza in _fraze(b):
            md = re.search(r"diferen\w*.*?" + _RE_SUMA + r"\s*lei", fraza)
            if md and len(impozite) == 2 and _num(md.group(1)) != abs(impozite[0] - impozite[1]):
                abateri.append({"afirmatie": fraza, "perioada": "exemplu", "asteptat": "diferența %s lei" % _lei(abs(impozite[0] - impozite[1])),
                                "gasit": "diferența %s lei" % _lei(_num(md.group(1)))})
    return abateri


def _lei(d):
    from decimal import Decimal
    d = Decimal(d)
    intreg = "{:,}".format(int(d)).replace(",", ".")
    return intreg if d == int(d) else intreg + "," + ("%.2f" % (d - int(d)))[2:]


def _mesaj_valoare(slug, a):
    return "VALOARE FISCALĂ diferită de registru (%s) — pagina %s, %s: așteptat %s, găsit %s: „%s”" % (
        _CHEIE_DIVIDEND, slug, a["perioada"], a["asteptat"], a["gasit"], a["afirmatie"][:160])


def ghiduri_afectate(director=None, cote=None):
    """[17.5-C9, C-ghid pct.4] {slug: [abateri]} pe TOATE ghidurile din `ghid/` (și cele vechi, din afara clichetului de citări) care au
    cel puțin o afirmație judecată pentru cheia `impozit_dividend`; abaterile goale = conform. Folosită de garda de publicare."""
    d = director or os.path.join(RADACINA, "ghid")
    out = {}
    for f in sorted(os.listdir(d)):
        if not f.endswith(".md"):
            continue
        _m, corp = _frontmatter(io.open(os.path.join(d, f), encoding="utf-8").read())
        if not _judecate(corp):
            continue
        out[f[:-3]] = verifica_valori_fiscale(corp, cote)
    return out


def _judecate(corp):
    """True când ghidul are cel puțin o frază despre dividende cu cotă și an (sau un exemplu cu dividende)."""
    for fraza in _fraze(corp):
        if _RE_CONTEXT.search(fraza) and not _RE_EXCLUS.search(fraza):
            cur = _curata(fraza)
            if _RE_COTA.search(cur) and (_RE_AN.search(cur) or _RE_NEGARE.search(cur)):
                return True
    return bool(re.search(r":::\s*ghid-exemplu(?:(?!:::).)*dividend", corp, re.S | re.I))


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
