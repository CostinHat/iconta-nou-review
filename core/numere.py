# -*- coding: utf-8 -*-
"""core/numere.py — sursa UNICA pentru parsarea numerelor din exporturi/importuri.

Extras din core/solduri_api._numar (15.07.2026), dupa ce s-a descoperit ca ACEEASI
functie era copiata in 9 module, fiecare cu bug propriu: 6 din 9 transformau
"(200)" (format contabil = suma negativa) in 0.0 TACUT, in loc de -200. O valoare
care devine 0 in tacere e mai periculoasa decat un import refuzat - dispare din
totaluri fara nicio urma.

O sursa unica inseamna: un singur loc de reparat, un singur loc de testat.
"""


def numar(v, strict=False):
    """Transforma o valoare in numar. Accepta:
      - '1.234,56' (RO) / '1,234.56' (EN)
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
    if "," in t and "." in t:
        if t.rfind(",") > t.rfind("."):
            t = t.replace(".", "").replace(",", ".")   # 1.234,56
        else:
            t = t.replace(",", "")                      # 1,234.56
    elif "," in t:
        parte = t.split(",")[-1]
        t = t.replace(",", ".") if len(parte) <= 2 else t.replace(",", "")
    try:
        x = float(t)
    except ValueError:
        if strict:
            raise ValueError("valoare numerica neinterpretabila: %r" % (v,))
        return 0.0
    return -x if neg else x

# ============================================================
#  VALOARE FISCALA — conversie care NU inghite gunoiul
# ============================================================
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
        raise ValueError("valoare fiscala booleana%s: %r" % (unde, x))
    try:
        d = Decimal(str(x).strip())
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("valoare fiscala invalida%s: %r "
                         "(zecimalele se scriu cu punct, nu cu virgula)" % (unde, x))
    if not d.is_finite():
        raise ValueError("valoare fiscala nefinita%s: %r" % (unde, x))
    return d
