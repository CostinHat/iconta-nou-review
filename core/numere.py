# -*- coding: utf-8 -*-
"""core/numere.py — sursa UNICA pentru parsarea numerelor din exporturi/importuri.

Extras din core/solduri_api._numar (15.07.2026), dupa ce s-a descoperit ca ACEEASI
functie era copiata in 9 module, fiecare cu bug propriu: 6 din 9 transformau
"(200)" (format contabil = suma negativa) in 0.0 TACUT, in loc de -200. O valoare
care devine 0 in tacere e mai periculoasa decat un import refuzat - dispare din
totaluri fara nicio urma.

O sursa unica inseamna: un singur loc de reparat, un singur loc de testat.
"""


import re as _re

# [lotul 13, deficiența 655 — clasa, toată aplicația] REGULA UNICĂ a numărului scris de om, în format românesc. Oglinda JS e
# `static/js/api.js::numarRo` (aceleași exemple, `core/test_lot13_ds_sume_ro.py`; DS cap.6 „Numerele scrise de om”). Instanțele:
# D207 „1.000” la bază -> „bază 1,00 lei”; Casă „1.500” -> 1,50 lei. Regula:
#   - punctul urmat de grupuri de câte trei cifre desparte miile: „1.000” = o mie, „1.234.567,89”;
#   - virgula e zecimala: „1500,5”, „1.500,50”;
#   - un punct urmat de 1–2 sau de 4+ cifre („1234.56”, „4.9750”, „0.500”) nu poate fi separator de mii, deci e zecimală;
#   - „1,234.56” (amândouă, punctul ultimul) e scrierea englezească, citită ca atare;
#   - orice altceva („1.23.4”, „12a”, „1,2,3”) e refuzat, cu MESAJ_NUMAR_RO — nu devine un număr ghicit și nici zero.
# Nu e `common._dec`: acela citește valori INTERNE (Decimal -> str, „4.975” = cursul), unde punctul e zecimala.
MESAJ_NUMAR_RO = "Scrie numărul ca în contabilitate: 1.234,56 (punct la mii, virgulă la zecimale)."
_RE_MII = _re.compile(r"^[1-9]\d{0,2}(\.\d{3})+(,\d*)?$")
_RE_VIRGULA = _re.compile(r"^(\d+(,\d*)?|,\d+)$")
_RE_ENGLEZ = _re.compile(r"^[1-9]\d{0,2}(,\d{3})+\.\d+$")
_RE_PUNCT_ZECIMAL = _re.compile(r"^\d+\.\d+$")


def numar_ro(text):
    """Numărul scris de om (format românesc) -> `Decimal`; gol -> None; text care nu e număr -> ValueError(MESAJ_NUMAR_RO).
    Aceeași regulă ca `api.js::numarRo` (vezi blocul de mai sus)."""
    from decimal import Decimal
    if text is None:
        return None
    if isinstance(text, bool):
        raise ValueError(MESAJ_NUMAR_RO)
    if isinstance(text, (int, float, Decimal)):
        return Decimal(str(text))
    t = _re.sub(r"[\s\u00a0\u202f]", "", str(text))
    if not t:
        return None
    minus = False
    if t[0] in "-+\u2212":
        minus, t = t[0] != "+", t[1:]
    if _RE_MII.match(t):
        c = t.replace(".", "").replace(",", ".")
    elif _RE_VIRGULA.match(t):
        c = t.replace(",", ".")
    elif _RE_ENGLEZ.match(t):
        c = t.replace(",", "")
    elif _RE_PUNCT_ZECIMAL.match(t):
        c = t
    else:
        raise ValueError(MESAJ_NUMAR_RO)
    if c.startswith("."):
        c = "0" + c
    if c.endswith("."):
        c = c[:-1]
    return Decimal(("-" if minus else "") + c)


def numar(v, strict=False):
    """Transforma o valoare in numar. Accepta:
      - '1.234,56' / '1.500' / '1500,5' (RO) / '1,234.56' (EN) — regula `numar_ro` (655)
      - '(500)' -> -500.0 (format contabil: paranteze = suma negativa)
      - '500 lei' / '1.234,56 RON' / '2 buc' (sufixe uzuale in exporturi)
      - '', None -> 0.0

    strict=True -> ridica ValueError pe text neinterpretabil, in loc sa intoarca 0.
    Implicit (strict=False) e tolerant, ca sa nu schimbe comportamentul modulelor
    care nu cer inca strict.
    """
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    t = str(v).strip().replace(" ", "").replace("\xa0", "")
    if not t:
        return 0.0
    neg = t.startswith("(") and t.endswith(")")
    if neg:
        t = t[1:-1].strip()
    for suf in ("RON", "ron", "LEI", "Lei", "lei", "EUR", "eur", "buc", "BUC", "kg", "KG", "%"):
        if t.endswith(suf):
            t = t[:-len(suf)].strip()
    # [655] separatorii se citesc după regula unică a numărului scris (`numar_ro`): „1.500” = o mie cinci sute (era 1,5), „1.234.567”
    # = un milion... (era 0, tăcut), „1,234” = 1,234 (virgula e zecimala; era 1234), „1,234.56” rămâne scrierea englezească
    try:
        d = numar_ro(t)
        x = float(d) if d is not None else 0.0
    except ValueError:
        if strict:
            raise ValueError("valoare numerică neinterpretabila: %r" % (v,))
        return 0.0
    return -x if neg else x

# ============================================================
#  VALOARE FISCALA — conversie care NU inghite gunoiul
# ============================================================
def leu_aritmetic(x):
    """Rotunjirea ARITMETICĂ la leu (partea zecimală >= 0,5 -> +1), rotunjirea din structura D112 pentru contribuții și câmpurile
    calculate: structura D112 (`anaf_surse/structura_D112_0726_030826.txt`, „Rotunjirile : Contributiile se rotunjesc
    aritmetic (daca partea zecimala >= 0.5, se adauga 1 la partea intreaga)”). Aceeași regulă ca `d112._d112int` (care nu se
    atinge: orice modificare a lui `core/d112.py` declanșează pasul D1 din firul „Contract uniform A1”, decizia Costin
    04.10.2026); echivalența celor două e gardată de `core/test_lot0610_p3.py`. Folosită de statul de plată / fluturaș (comanda Costin 06.10.2026 pct.11: „netul și costul angajatorului de pe fluturaș trebuie să
    iasă din aceleași sume care merg în D112”). NU `round()` (bancar). Întoarce Decimal întreg."""
    from decimal import Decimal, ROUND_HALF_UP
    return (x if isinstance(x, Decimal) else Decimal(str(x))).quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def numar_fiscal(x, camp=""):
    """Converteste o valoare destinata unui calcul fiscal. Intoarce Decimal.

    REGULA (27.07.2026): ABSENTA e legitima, INVALIDUL e eroare.
      - None sau sir gol -> Decimal(0). Un camp optional negol nu e o eroare.
      - orice altceva neconvertibil (text, "12,5" cu virgula romaneasca, nan,
        infinit, lista) -> ValueError.

    DE CE: d112._d112int, d300._int si d390._int aveau `except: return 0`. O
    valoare stricata devenea TACIT zero intr-o declaratie depusa la ANAF. Cel mai
    periculos caz nu e textul evident gresit, ci "12,5" - un numar scris cu virgula
    zecimala romaneasca, perfect plauzibil, care iesea 0 lei.

    Tiparul corect exista deja in cod: d205._i si d101._i fac aceeasi conversie FARA
    masca. Aceasta functie e locul unic al regulii - nu se recopiaza.
    """
    from decimal import Decimal, InvalidOperation
    unde = (" pentru %s" % camp) if camp else ""
    if x is None or (isinstance(x, str) and not x.strip()):
        return Decimal(0)
    if isinstance(x, bool):
        raise ValueError("valoare fiscală booleana%s: %r" % (unde, x))
    try:
        d = Decimal(str(x).strip())
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("valoare fiscală invalidă%s: %r "
                         "(zecimalele se scriu cu punct, nu cu virgula)" % (unde, x))
    if not d.is_finite():
        raise ValueError("valoare fiscală nefinita%s: %r" % (unde, x))
    return d
