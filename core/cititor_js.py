# -*- coding: utf-8 -*-
r"""core/cititor_js.py — CITITORUL COMUN de JavaScript: albeste ce e TEXT, pastreaza ce e COD.

DE UNDE VINE (04.09.2026, lotul 10). Doua instrumente aveau fiecare **copia lui** a aceluiasi
cititor — `core/scan_refuz_tacut.py` si `core/test_aritmetica_in_prezentare.py` —, iar copiile
purtau acelasi defect: un sir `'` sau `"` care nu se inchidea pe randul lui **trecea peste
capatul randului** si albea tot pana la urmatoarea ghilimea din fisier. In JS asta nu se poate:
gramatica opreste un sir simplu la sfarsitul randului. Sora lui `_curata_sir` din acelasi fisier —
`_sfarsit_sir` — avea deja regula; `_curata_sir`, nu. Asimetria a trait de la nastere.

CE A DECLANSAT-O, si de ce nu se vedea: linia `cd.match(/filename="([^"]+)"/)` are **trei**
ghilimele. Doua se imperecheaza, a treia deschidea un „sir" care inghitea sute de randuri.
Masurat pe HEAD `277e4300`: `ecrane/facturi_ecran.js` era orb de la randul 530 incolo (639 de
randuri, 312 scurgeri), iar `api.js` de la 397 (59 de randuri). Cele doua clichete care stau pe
cititor aratau, in aceeasi zi, unul prea MIC (`_SCRIERI_MUTE`, doua scrieri mute nevazute) si unul
prea MARE (`NUME_NEUTRE_CLICHET`, o formula nevazuta) — semnul ca greseala e in amandoua
directiile, deci cifra n-are **niciun** plafon (METODA_VERIFICARE §22).

CE FACE, exact. Intoarce un text de ACEEASI lungime si cu ACELEASI randuri, in care:
  * comentariile (`//`, `/* */`) sunt albite;
  * textul sirurilor `'`, `"`, `` ` `` e albit, DAR interiorul unui `${…}` ramane COD si se
    curata recursiv — o cota scrisa in `` `${suma * cota / 100}` `` trebuie sa ramana vizibila;
  * **expresiile regulate** (`/…/flags`) sunt albite ca text. Fara asta, un `/\d{2}/` strica
    numararea acoladelor, iar unul care poarta cifre arata ca o cota cu aritmetica.

CUM DEOSEBESTE `/` DE INCEPUT DE EXPRESIE REGULATA DE IMPARTIRE: se uita la ultimul caracter
semnificativ de dinainte. Dupa o VALOARE (`a`, `1`, `)`, `]`, `"`) un `/` e impartire; dupa un
operator, o paranteza deschisa, o virgula sau un cuvant-cheie (`return`, `case`, …) e expresie
regulata. Daca `/`-ul nu se inchide pe randul lui, e tratat ca impartire — se cade in partea
sigura.

CELE TREI MODURI DE ESEC ALE ACESTUI CITITOR, scrise inainte de a fi folosit (interdictia 76):
  1. **euristica `/`** poate rata o expresie regulata scrisa imediat dupa `}` (`if(x){}/re/`) —
     `}` NU e in multimea de dinainte, fiindca `{…}` e si obiect, iar `obj/2` e impartire.
     Directia ratarii e cea sigura: regexul ramane vizibil ca si cod, nu dispare cod real.
  2. **nu e un parser**: nu stie de ASI, de `<!--`, de literalii JSX. Pe corpusul casei (numai
     module ES) tine; pe alt dialect, nu se presupune.
  3. **un sir neinchis pe randul lui** ramane albit pana la capatul randului, nu mai departe.
     Randul acela se citeste gresit — dar UN rand, nu tot fisierul.
"""

_CUVINTE_INAINTE_DE_REGEX = frozenset((
    "return", "typeof", "case", "in", "of", "new", "delete", "void", "instanceof",
    "do", "else", "yield", "await", "throw",
))

# Dupa aceste caractere un `/` NU poate fi impartire, deci e inceput de expresie regulata.
_INAINTE_DE_REGEX = "(,=:[!&|?+-*%^~<>;"


def _e_regex(ultim, cuvant):
    """`ultim` = ultimul caracter semnificativ emis ca si COD; `cuvant` = identificatorul care
    se termina in el (gol daca ultimul nu e litera/cifra)."""
    if ultim == "":
        return True                       # inceput de fisier sau de interpolare
    if cuvant in _CUVINTE_INAINTE_DE_REGEX:
        return True
    return ultim in _INAINTE_DE_REGEX


def _sfarsit_regex(src, i, n):
    """Indexul de dupa `/…/flags` care incepe la `i`, sau None daca nu se inchide pe randul lui.

    Un `/` dintr-o clasa `[...]` NU inchide expresia — `/[/]/` e legal.
    """
    j = i + 1
    in_clasa = False
    while j < n:
        c = src[j]
        if c == "\\":
            j += 2
            continue
        if c == "\n":
            return None                   # expresiile regulate nu trec de capatul randului
        if in_clasa:
            if c == "]":
                in_clasa = False
        elif c == "[":
            in_clasa = True
        elif c == "/":
            j += 1
            while j < n and (src[j].isalpha() or src[j] == "_"):
                j += 1
            return j
        j += 1
    return None


def _sfarsit_sir(src, i, n):
    """Indexul de DUPA sirul care incepe la `i`. Trateaza `${…}` din template literals."""
    q = src[i]
    j = i + 1
    while j < n:
        c = src[j]
        if c == "\\":
            j += 2
            continue
        if q == "`" and src[j:j + 2] == "${":
            j = _sfarsit_expresie(src, j + 2, n)
            continue
        if c == q:
            return j + 1
        if q != "`" and c == "\n":        # un sir simplu nu trece de capatul randului
            return j
        j += 1
    return n


def _sfarsit_expresie(src, i, n):
    """Din interiorul unui `${`, indexul de dupa acolada care il inchide. Sare peste siruri."""
    adanc, j = 1, i
    while j < n:
        c = src[j]
        if c in "\"'`":
            j = _sfarsit_sir(src, j, n)
            continue
        if c == "{":
            adanc += 1
        elif c == "}":
            adanc -= 1
            if adanc == 0:
                return j + 1
        j += 1
    return n


def _albeste(bucata, out):
    for ch in bucata:
        out.append("\n" if ch == "\n" else " ")


def _curata_sir(src, i, n, out):
    """Albeste textul unui sir, dar PASTREAZA ce e intre `${` si `}` — acolo e cod."""
    q = src[i]
    out.append(" ")                       # ghilimeaua de deschidere
    j = i + 1
    while j < n:
        c = src[j]
        if c == "\\":
            _albeste(src[j:j + 2], out)   # inclusiv randul continuat cu `\` la capat
            j += 2
            continue
        if q == "`" and src[j:j + 2] == "${":
            out.append("  ")
            k = _sfarsit_expresie(src, j + 2, n)
            _curata(src, j + 2, k - 1, out)   # interiorul e COD, se curata recursiv
            out.append(" ")                   # acolada de inchidere
            j = k
            continue
        if c == q:
            out.append(" ")
            return j + 1
        if q != "`" and c == "\n":
            # GRAMATICA JS: un sir `'` sau `"` NU trece de capatul randului. Cititorul de
            # dinainte trecea, si albea pana la urmatoarea ghilimea din FISIER — de acolo
            # orbirea masurata pe 04.09.2026. Randul se opreste aici; `\n` il emite apelantul.
            return j
        out.append("\n" if c == "\n" else " ")
        j += 1
    return n


def _curata(src, i, n, out):
    """Scoate comentariile, textul sirurilor si expresiile regulate din `src[i:n]`."""
    ultim, cuvant = "", ""
    while i < n:
        c, d = src[i], src[i:i + 2]
        if d == "//":
            j = src.find("\n", i)
            j = n if j < 0 or j > n else j
            _albeste(src[i:j], out)
            i = j
        elif d == "/*":
            j = src.find("*/", i + 2)
            j = n if j < 0 or j + 2 > n else j + 2
            _albeste(src[i:j], out)
            i = j
        elif c in "\"'`":
            i = _curata_sir(src, i, n, out)
            ultim, cuvant = '"', ""       # un sir e o VALOARE: `"a" / 2` e impartire
        elif c == "/" and _e_regex(ultim, cuvant):
            k = _sfarsit_regex(src, i, n)
            if k is None or k > n:
                out.append(c)             # nu se inchide pe rand -> se citeste ca impartire
                i += 1
                ultim, cuvant = "/", ""
            else:
                _albeste(src[i:k], out)
                i = k
                ultim, cuvant = ")", ""   # o expresie regulata e o VALOARE
        else:
            out.append(c)
            if not c.isspace():
                ultim = c
                cuvant = (cuvant + c) if (c.isalnum() or c == "_" or c == "$") else ""
            i += 1
    return i


def fara_siruri(src):
    """Textul, de ACEEASI lungime si cu ACELEASI randuri, fara comentarii, siruri si regexuri."""
    out = []
    _curata(src, 0, len(src), out)
    rez = "".join(out)
    assert len(rez) == len(src), "cititorul a schimbat lungimea — numerele de linie ar sari"
    return rez


# Numele vechi, pastrat pentru gardurile care il cheama asa.
fara_comentarii_si_siruri = fara_siruri
