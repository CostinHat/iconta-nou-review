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
