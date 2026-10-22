# -*- coding: utf-8 -*-
"""core/cui_forma.py — FORMA în care se păstrează și se arată un cod fiscal (lotul 11, decizia Costin 10.3 pct.4, verbatim în DECIZII
„Comanda 10.3”: „CUI-ul se păstrează fără «RO» și fără spații; «RO» apare doar la afișare, după starea de plătitor de TVA.”). PUR, LEAF.

Temeiul formei afișate: CF art.318 alin.(1) — „Codul de înregistrare în scopuri de TVA, atribuit conform art. 316 și 317, are prefixul RO,
conform Standardului internațional ISO 3166 - alpha 2.” Prefixul e deci al CODULUI DE TVA, nu al CUI-ului: îl are numai persoana
înregistrată în scopuri de TVA. Pe documentele ANAF prefixul se pune tot după stare, în generatorul fiecăruia (D406 `registration_number`,
e-Factura `_vatid` din cifre + starea, factura PDF `cod_fiscal_pe_factura`) — niciunul nu se bazează pe prefixul scris în bază.

`stocare(v)`: spațiile scoase și „RO” scos din fața unui cod numai din cifre (codul românesc); codul de TVA al unui partener din alt stat
(„DE123456789”, „EL…”) rămâne cu prefixul statului lui — acela e chiar codul, nu o mențiune. `None` / gol -> None.
`afisare(cui, platitor_tva)`: „RO” + cifre numai când starea e „plătitor” (True); altfel codul așa cum e păstrat.
`SQL`: aceeași formă ca expresie SQL, pentru comparații pe coloane (`SQL.format(c="tert_cui")`).
"""
import re

#: cifrele ASCII, ca `[0-9]` din SQL (`\d` din Python ar lua și cifrele altor scrieri: „RO١٢٣” ar pierde „RO” numai în Python)
_RO_CIFRE = re.compile(r"^RO([0-9]+)$")

#: [lotul 11, subagentul CF] spațiile scoase de `stocare` (`\s` din Python = toate spațiile Unicode), scrise pentru SQL: `\s` din
#: PostgreSQL (lc_ctype en_US.UTF-8, verificat pe baza de test și pe producție) NU vede U+00A0 (spațiul nedespărțitor, cel din „RO&nbsp;…”
#: copiat de pe o pagină web), U+202F, U+2007, U+0085 și U+001C–U+001F — „RO<NBSP>18547290” rămânea cu „RO” în SQL, dar nu în Python.
#: Paritatea pe fiecare spațiu Unicode: core/test_lot11_cf_cui_forma_unica.py::test_paritatea_spatiilor_python_sql.
SPATII_SQL = "[\\s\\u0085\\u00a0\\u2007\\u202f\\u001c-\\u001f]"

#: aceeași normalizare ca `stocare`, în SQL (comparații pe coloane scrise înainte de normalizare)
SQL = "regexp_replace(regexp_replace(upper(COALESCE({c}, '')), '" + SPATII_SQL + "', '', 'g'), '^RO([0-9]+)$', '\\1')"


def stocare(v):
    """Codul fiscal în forma păstrată: fără spații, fără „RO” în fața cifrelor; None când e gol."""
    if v is None:
        return None
    t = re.sub(r"\s+", "", str(v)).upper()
    if not t:
        return None
    m = _RO_CIFRE.match(t)
    return m.group(1) if m else t


def afisare(cui, platitor_tva):
    """Codul arătat omului: „RO” + cifre la plătitorul de TVA (CF art.318 alin.(1)); altfel codul păstrat. None când e gol."""
    t = stocare(cui)
    if t is None:
        return None
    return ("RO" + t) if (platitor_tva is True and t.isdigit()) else t
