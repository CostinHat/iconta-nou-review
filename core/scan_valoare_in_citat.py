# -*- coding: utf-8 -*-
"""core/scan_valoare_in_citat.py — INTERDICȚIA 53: citatul conține VALOAREA pe care o justifică?

DE CE E NOU, deși există `scan_citate`. Cele două verifică lucruri diferite, și confundarea lor ar fi
atribuit interdicției 53 o măsurătoare a altceva:

  `scan_citate._verbatim` : citatul EXISTĂ în documentul citat?  (citatul e real)
  aici                    : citatul CONȚINE valoarea justificată? (citatul justifică)

Un citat poate fi perfect real și să nu conțină valoarea — atunci temeiul aterizează pe act, dar nu pe
regulă. Planul numește 53 „cel mai măsurabil din tot planul": *citatul verbatim conține valoarea, sau
nu*. Se verifică mecanic, fără judecată.

MODUL PROPRIU DE EȘEC, și de aceea calibrarea de mai jos (interdicția 76):
  - o valoare apare în citat în ALT FORMAT decât în cod: `Decimal("0.37")` ↔ „37%",
    `Decimal("0.0725")` ↔ „7,25%", `1234567` ↔ „1.234.567 lei". Un scan naiv ar acuza toate
    cotele. (Exemplele sunt cu valori INVENTATE, nu cu cote reale: verificatorul de conformitate
    citeste orice pereche valoare+«cota» dintr-un fisier ca pe o declaratie de cota fara temei,
    si a semnalat corect prima forma a docstringului asta.)
  - o valoare apare ca SUBȘIR al alteia: „1.234.567" în „11.234.567". Un scan naiv ar trece.
Amândouă sunt fals-pozitive/negative de construcție, deci amândouă sunt gardate.

CE NU POATE SPUNE, declarat: dacă valoarea LIPSEȘTE din citat, cauza poate fi (1) citatul e localizator
sau parafrază — formă legitimă, vezi `scan_citate`; (2) valoarea e exprimată în cuvinte („o pătrime");
(3) citatul chiar nu justifică valoarea. Scanul le pune pe toate în aceeași grămadă și o numește
NEJUSTIFICATĂ MECANIC, nu GREȘITĂ.
"""
import decimal
import re

_MII = re.compile(r"[.  ]")


# Un citat de lege isi poarta ADRESA in el: „art.51 alin.(1): Cota de impozit pe ...". Cifrele din
# adresa NU justifica nimic — dar un scan naiv le potriveste, iar valorile mici sunt exact cele care
# cad: `impozit_micro` = 0.01 -> forma „1" -> potrivita in „alin.(1)". Prins la calibrarea prin
# inspectie, pe un rezultat de 34 din 34 care era prea curat ca sa fie adevarat (interdictia 76).
_LOCALIZATOR = re.compile(
    r"art\.?\s*\d+(\^\d+)?"          # art.51, art.146^1
    r"|alin\.?\s*\(?\d+(\^\d+)?\)?"  # alin.(1), alin 5^6
    r"|lit\.?\s*[a-zA-Z]\)?"          # lit.a)
    r"|pct\.?\s*\d+"                  # pct.19
    r"|nr\.?\s*[\d./]+"                # nr. 227/2015
    r"|\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b"   # 15.12.2025
    r"|\bMO\s*[\d/. ]+"                # MO 313/30.05.2
    r"|\b(19|20)\d{2}\b",             # anii
    re.I)


def _fara_localizatori(text):
    """Citatul, cu adresele scoase — ca sa ramana doar substanta."""
    return _LOCALIZATOR.sub(" ", text or "")


def _cifre(x):
    """Formele în care o valoare poate apărea într-un text de lege."""
    if isinstance(x, bool) or x is None:
        return set()
    try:
        d = decimal.Decimal(str(x))
    except (decimal.InvalidOperation, ValueError):
        return set()
    out = set()
    # forma brută, fără zerouri de coadă
    brut = format(d.normalize(), "f")
    out.add(brut)
    # procent: 0.21 -> 21 ; 0.0225 -> 2.25 -> „2,25"
    if 0 < abs(d) < 1:
        pct = (d * 100).normalize()
        p = format(pct, "f")
        out.add(p)
        out.add(p.replace(".", ","))
    # întregi mari: 2250000 -> „2.250.000" și „2 250 000"
    if d == d.to_integral_value() and abs(d) >= 1000:
        n = int(d)
        cu_punct = "{:,}".format(n).replace(",", ".")
        out.add(cu_punct)
        out.add("{:,}".format(n).replace(",", " "))
        out.add(str(n))
    # zecimale cu virgulă
    if "." in brut:
        out.add(brut.replace(".", ","))
    return {o for o in out if o}


def _apare(forma, text):
    """Forma apare ca NUMĂR DE SINE STĂTĂTOR, nu ca subșir al altui număr."""
    if not forma:
        return False
    tip = re.escape(forma)
    # granițe: nu cifră, nu separator de mii lipit de cifră, înainte și după
    return re.search(r"(?<![\d.,])" + tip + r"(?![\d])", text) is not None


def justifica(valoare, text_citat):
    """True dacă vreo formă a valorii apare de sine stătător în citat. None dacă n-avem ce verifica."""
    if not text_citat:
        return None
    forme = _cifre(valoare)
    if not forme:
        return None
    substanta = _fara_localizatori(text_citat)
    return any(_apare(f, substanta) for f in forme)


def inventar(radacina=None):
    """[(cheie, data_in, valoare, temei, justificat)] pentru fiecare intrare din registrul de cote."""
    from core import common as c
    out = []
    for cheie, intrari in sorted(c.COTE.items()):
        for intrare in intrari:
            if not isinstance(intrare, (list, tuple)) or len(intrare) < 3:
                continue
            data_in, valoare, temei = intrare[0], intrare[1], intrare[2]
            out.append((cheie, data_in, valoare, temei,
                        justifica(valoare, getattr(temei, "text_citat", None))))
    return out


def rezumat(radacina=None):
    inv = inventar(radacina)
    da = sum(1 for x in inv if x[4] is True)
    nu = sum(1 for x in inv if x[4] is False)
    na = sum(1 for x in inv if x[4] is None)
    return {"total": len(inv), "justificate": da, "nejustificate": nu, "fara_citat": na}


if __name__ == "__main__":
    inv = inventar()
    r = rezumat()
    print("INTERDICTIA 53 — valoarea apare in citatul care o justifica?")
    print("   intrari in registrul de cote : %d" % r["total"])
    print("   JUSTIFICATE mecanic          : %d" % r["justificate"])
    print("   NEJUSTIFICATE mecanic        : %d" % r["nejustificate"])
    print("   fara citat / fara valoare    : %d" % r["fara_citat"])
    print()
    print("   Nejustificate, pe nume (NU inseamna gresite - vezi docstring):")
    for cheie, data_in, val, t, ok in inv:
        if ok is False:
            citat = (getattr(t, "text_citat", "") or "")[:72].replace("\n", " ")
            print("      %-34s %s  val=%-12s  %s" % (cheie, data_in, val, citat))
