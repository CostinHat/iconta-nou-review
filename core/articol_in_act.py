# -*- coding: utf-8 -*-
"""LOCALIZAREA UNUI ARTICOL ÎNTR-UN ACT — logica scoasă din `scripts/vigoare_articol.py`.

**De ce există ca modul, 31.08.2026.** Logica asta trăia la nivel de script, sub `sys.argv`, deci
nu se putea importa: cine avea nevoie de ea o **re-scria**. Am făcut-o de două ori într-o oră, ca să
măsor interdicția 55, și amândouă copiile au dat cifre greșite — prima a raportat *0 caractere*
pentru OUG 89/2025 art. III, unde instrumentul găsește **3700**; a doua a raportat *„fără fișier în
corpus"* despre Codul fiscal, care e acolo. *O logică neimportabilă nu rămâne una singură: se
multiplică prost.* `scripts/vigoare_articol.py` importă de aici — o singură implementare.

CELE PATRU REPARAȚII PLĂTITE, păstrate cuvânt cu cuvânt din script, fiindcă fiecare a costat o
măsurătoare falsă:

  1. **Cifre ROMANE.** Actele modificatoare își numerotează articolele cu cifre romane („Articolul
     III", „Articolul LXVI"). Terminatorul cerea o cifră arabă, deci potrivirea nu se putea încheia
     și ieșea NEGĂSIT — exact pe articolele care poartă schimbările fiscale.
  2. **Forma de CITARE se exclude.** „Articolul III **din** LEGEA nr. 173…" numește articolul altui
     act. Fără excludere, art. III al lui OUG 89/2025 a primit un „modificat la 16-08-2026" care
     aparținea art. XXXVI, și a produs o alarmă falsă pe **trei** valori din registru.
  3. **Titlul se recunoaște după marcajul `+` al portalului**, nu după poziția în linie: forma reală
     e „) \\n + \\n Articolul III (1) Prin derogare…".
  4. **Fără fereastră fixă.** Forma dinainte capta cel mult 2600 de caractere și cerea ca următorul
     titlu să încapă în ele; un articol mai lung ieșea NEGĂSIT — și tocmai articolele lungi sunt cele
     cu condiții, adică cele care poartă valori.

**A CINCEA REPARAȚIE, găsită DE extragere** (31.08.2026). Scriptul aplica, peste tăierea la
următorul titlu, o a doua tăiere cu un tipar **lax** — fără excluderea `din`. Aceea potrivea forma
de **citare** dinăuntrul unui marcaj de consolidare: *„… Articolul I ORDONANȚA DE URGENȚĂ nr. 79
**din** 8 noiembrie 2017 …"*. Consecința, măsurată pe registru: **5 din 26 de perechi** își schimbau
răspunsul, iar `CF art. 78` — deducerea din salarii — apărea cu **532 de caractere și un singur an
de modificare (2021)** în loc de **16.719 caractere și șase ani (2018, 2020, 2021, 2023, 2024,
2026)**. Trunchierea tăia articolul la primul marcaj și **arunca alineatele de după el, cu tot cu
modificările lor.**

*Direcția greșelii e cea liniștitoare, și de-aia contează:* un articol părea **mai stabil decât e**,
deci ar fi primit pragul de reverificare cel mai lung exact acolo unde trebuie cel mai scurt. A doua
tăiere s-a păstrat **numai** pe calea de rezervă `ART. <n>`, unde chiar e nevoie de un terminator.
Probat: pe cele trei articole schimbate, fragmentul nou nu conține **niciun** titlu de alt articol.

CE NU FACE, declarat: nu spune că articolul **spune** ce îi atribuim — aia e o citire, nu o
potrivire. Aici se răspunde doar la *există în documentul ăsta?* și *ce marcaje poartă?*
"""
import html as _html
import io
import os
import re

#: Sub atâtea titluri de articol, documentul e un CIOT și nu se poate afirma nimic despre un
#: articol al lui. Pagina `DetaliiDocument` a portalului e un ciot pentru actele mari: Codul fiscal
#: a venit în 4.407 caractere, iar instrumentul a răspuns „NEGĂSIT" pentru toate cele cinci articole
#: cerute — **cu încredere**. Un „negăsit" despre un act neadus nu e un răspuns, e o tăcere care
#: arată ca un răspuns. Criteriul nu e lungimea (arbitrară), ci dacă actul adus ARE articole.
PRAG_TITLURI = 2

_TITLU_ORICARE = re.compile(
    r"(?:\+\s*|(?:^|\n)\s*)Articol(?:ul)?\s*[\dIVXLC]+(?:\^\d+)?\b(?!\s+din\b)")
_TITLURI_NUMARATE = re.compile(r"(?im)^\s*\+?\s*Articol(?:ul)?\s+[\dIVXLC]")


def text(h):
    """HTML sau text brut → text normalizat, cu liniile păstrate (titlurile se ancorează pe ele)."""
    h = re.sub(r"(?is)<(script|style).*?</\1>", " ", h)
    h = re.sub(r"(?i)<br\s*/?>", "\n", h)
    h = re.sub(r"(?i)</(p|div|tr|li|h[1-6])>", "\n", h)
    h = re.sub(r"<[^>]+>", " ", h)
    h = _html.unescape(h)
    h = re.sub(r"[ \t\xa0]+", " ", h)
    return re.sub(r"\n\s*\n+", "\n\n", h).strip()


def din_fisier(cale):
    """(text, amprenta) pentru un fișier de corpus. Amprenta e garda: `test_corpus_amprenta`
    verifică la fiecare poartă că fișierul e cel adus."""
    import hashlib
    brut = io.open(cale, "rb").read()
    return text(brut.decode("utf-8", "replace")), hashlib.sha256(brut).hexdigest()[:16]


def corp_util(t):
    """Partea de după «Forma printabilă», dacă există — restul e antet de portal."""
    i = t.find("Forma printabilă")
    return t[i:] if i > 0 else t


def titluri(t):
    """Câte titluri de articol se văd. Sub `PRAG_TITLURI`, documentul e un ciot."""
    return len(_TITLURI_NUMARATE.findall(t))


def e_ciot(t):
    return titluri(t) < PRAG_TITLURI


def fragment(t, art):
    """Textul articolului `art`, sau `None` dacă nu e în documentul ăsta.

    Se caută titlul, apoi URMĂTORUL titlu (oricum ar fi numerotat), și se taie între ele.
    """
    corp = corp_util(t)
    esc = re.escape(str(art))
    tit = re.compile(r"(?:\+\s*|(?:^|\n)\s*)Articol(?:ul)?\s*%s\b(?!\^)(?!\s*\^)(?!\s+din\b)" % esc)
    m0 = tit.search(corp)
    if m0:
        urm = _TITLU_ORICARE.search(corp, m0.end())
        brut = corp[m0.end():urm.start() if urm else len(corp)]
    else:
        m = re.search(r"ART\.\s*%s\b(.{0,2600}?)(?=ART\.\s*\d|\Z)" % esc, corp, re.S)
        if m is None:
            return None
        brut = m.group(1)
        stop = re.search(r"\n?\s*\+?\s*Articol(?:ul)?\s*[\dIVXLC]", brut)
        if stop:
            brut = brut[:stop.start()]
    return re.sub(r"\s+", " ", brut).strip()


def abrogat(frag):
    return bool(re.match(r"^\(?1?\)?\s*Abrogat", frag, re.I)) or \
        bool(re.search(r"^\s*Abrogat", frag, re.I))


def marcaje(frag):
    """[(data, ce)] — marcajele de consolidare „(la ZZ-LL-AAAA, … a fost modificat de …)".

    **ÎȘI NORMALIZEAZĂ SINGUR INTRAREA** (01.09.2026, R111). Tiparul are `.{0,190}?`, iar `.` nu
    trece peste linia nouă: pe text cu linii păstrate, aproape niciun marcaj nu se potrivea. Mergea
    doar fiindcă singurul apelant era `fragment`, care colapsează spațiile la ieșire — o precondiție
    reală, nescrisă nicăieri. **Măsurat pe Codul fiscal: 2.020 de ocurențe brute, `marcaje` întorcea
    UNA.** Am căzut chiar eu în ea, măsurând clasa lui R111. Normalizarea aici e idempotentă pentru
    fragmente și face funcția onestă pentru orice apelant.
    """
    frag = re.sub(r"\s+", " ", frag or "")
    return [(d, re.sub(r"\s+", " ", ce).strip())
            for d, ce in re.findall(r"\(la (\d{2}-\d{2}-\d{4}),(.{0,190}?)\)", frag)]


#: Cache pe cale: `inregistreaza_modificari` normalizează corpul întreg (2,5 MB pentru Codul fiscal),
#: iar `categorie` o poate întreba o dată per temei. Cheia e calea; corpusul nu se schimbă în timpul
#: unei rulări, iar `test_corpus_amprenta` păzește la fiecare poartă că fișierele sunt cele aduse.
_INREGISTREAZA = {}


def inregistreaza_modificari(cale):
    """Documentul consemnează VREO modificare de consolidare, oriunde în corpul lui?

    **Întrebarea pe care instrumentul trebuia să și-o pună despre sine** (R111). „Zero marcaje în
    articolul N" înseamnă două lucruri foarte diferite:
      - documentul consemnează modificări în alte părți, dar nu pentru articolul ăsta → **nemodificat**;
      - documentul nu consemnează nicio modificare, nicăieri → **nu se poate ști din el**.
    Fără deosebirea asta, a doua situație se citea ca prima și producea `STABIL` — adică *verificat
    mai rar*, direcția largă, dintr-o sursă care nu putea răspunde.

    Măsurat 01.09.2026: `cod_fiscal_227_2015_consolidat.html` **1.400** · `oug_89_2025.html` **18**
    (deci art. III cu zero marcaje e un STABIL REAL, iar decizia din antetul lui `reverificare` se
    păstrează) · `legea_201_2025.html`, `oug_156_2024.pdf`, `ordin_1604_2025_intrastat_mo.txt` **0**.
    """
    if cale not in _INREGISTREAZA:
        try:
            t, _amp = din_fisier(cale)
        except OSError:
            return False
        _INREGISTREAZA[cale] = bool(marcaje(corp_util(t)))
    return _INREGISTREAZA[cale]


def ani_modificare(frag):
    """Anii distincți în care articolul a fost modificat, din marcajele lui."""
    return sorted({d[-4:] for d, _ in marcaje(frag)})


def cauta(cale, art):
    """{stare, frag, ani, titluri} pentru un articol într-un fișier de corpus.

    `stare` e una din: `CIOT` · `NEGASIT` · `ABROGAT` · `GASIT` · `FISIER_LIPSA`.
    Cele trei feluri de „nu pot spune" se DEOSEBESC — un fișier lipsă, un act-ciot și un articol
    care chiar nu e acolo sunt trei lucruri diferite, iar un singur „nu" le-ar topi într-unul.
    """
    if not os.path.exists(cale):
        return {"stare": "FISIER_LIPSA", "frag": None, "ani": [], "titluri": 0}
    t, _amp = din_fisier(cale)
    n = titluri(t)
    if n < PRAG_TITLURI:
        return {"stare": "CIOT", "frag": None, "ani": [], "titluri": n}
    frag = fragment(t, art)
    if frag is None:
        return {"stare": "NEGASIT", "frag": None, "ani": [], "titluri": n}
    return {"stare": "ABROGAT" if abrogat(frag) else "GASIT",
            "frag": frag, "ani": ani_modificare(frag), "titluri": n}
