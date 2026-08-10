# -*- coding: utf-8 -*-
"""core/identitate.py — validare OFFLINE a identitatii fiscale (CUI / CNP), sursa CANONICA pentru
DECLARATII (LANT legislatie TURA 3, 10.08.2026).

Pana la tura 28 (CATALOG_INVALIDITATE.md, tema T1) validatoarele existau imprastiate
(solduri_parteneri_api.valideaza_cui, salariati_import_api/asociati_import_api.valideaza_cnp,
tenant_provisioning.cui_valid) si erau folosite DOAR la import/provisioning - NICIODATA in generatoarele
de declaratii. Consecinta (probat pe 9/9 declaratii): un CUI/CNP cu cifra de control gresita, lungime
gresita sau non-numeric era emis TACIT; il prindea doar DUK (mesaj brut la depunere) sau nimeni.

Acest modul e LEAF (fara import de db/api) - importabil din orice generator fara risc de import circular.
Algoritmul e obiectiv (lege), nu depinde de ANAF online. Verificat contra valorilor pe care DUK le
accepta/respinge (301111003 valid / 301111004 invalid; 143000000 valid / 143000009 invalid).

Cele patru validatoare vechi raman (au propriii apelanti/teste); acesta e sursa pentru apelantii NOI
(declaratiile). Consolidarea lor pe acesta = curatare ulterioara, nu se forteaza aici (risc pe poarta).
"""
import datetime

_CHEIE_CUI = (7, 5, 3, 2, 1, 7, 5, 3, 2)                       # ponderi control CUI (Cod fiscal / ANAF)
_CHEIE_CNP = (2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9)              # cheia oficiala CNP 279146358279


def valideaza_cui(cui):
    """(valid: bool, motiv: str) - cifra de control a CUI romanesc, OFFLINE. Accepta forma cu/fara
    prefix RO si spatii (se extrag doar cifrele). CUI romanesc = 2-10 cifre (numar 1-9 + control).
    motiv in {ok, lipsa, lungime (2-10 cifre), cifra de control}."""
    c = "".join(ch for ch in str(cui or "") if ch.isdigit())
    if not c:
        return False, "lipsa"
    if not (2 <= len(c) <= 10):
        return False, "lungime (2-10 cifre, are %d)" % len(c)
    corp, ctrl = c[:-1].rjust(9, "0"), int(c[-1])
    s = sum(int(corp[i]) * _CHEIE_CUI[i] for i in range(9))
    rest = (s * 10) % 11
    if rest == 10:
        rest = 0
    return (rest == ctrl), ("ok" if rest == ctrl else "cifra de control")


def valideaza_cnp(cnp):
    """(valid: bool, motiv: str) - CNP romanesc: format 13 cifre + prima 1-9 + data valabila + judet
    1-52 + cifra de control (cheia 279146358279). motiv in {ok, format (13 cifre), prima cifra,
    luna invalida, data invalida, judet invalid, cifra de control}."""
    s = str(cnp or "").strip()
    if len(s) != 13 or not s.isdigit():
        return False, "format (13 cifre)"
    if s[0] not in "123456789":
        return False, "prima cifra (1-9)"
    sx = int(s[0]); aa = int(s[1:3]); ll = int(s[3:5]); zz = int(s[5:7])
    sec = {1: 1900, 2: 1900, 3: 1800, 4: 1800, 5: 2000, 6: 2000, 7: 2000, 8: 2000, 9: 1900}.get(sx, 1900)
    if not (1 <= ll <= 12):
        return False, "luna invalida"
    try:
        datetime.date(sec + aa, ll, zz)
    except ValueError:
        return False, "data invalida"
    if not (1 <= int(s[7:9]) <= 52):
        return False, "judet invalid"
    ctrl = sum(int(s[i]) * _CHEIE_CNP[i] for i in range(12)) % 11
    ctrl = 1 if ctrl == 10 else ctrl
    return (ctrl == int(s[12])), ("ok" if ctrl == int(s[12]) else "cifra de control")


def valideaza_cif(cif):
    """CIF partener = CUI (persoana juridica) SAU CNP (persoana fizica). (valid, tip, motiv) unde
    tip in {cui, cnp, ?}. Un cod de 13 cifre cu prima 1-9 e incercat intai ca CNP; altfel ca CUI."""
    c = "".join(ch for ch in str(cif or "") if ch.isdigit())
    if not c:
        return False, "?", "lipsa"
    if len(c) == 13 and c[0] in "123456789":
        v, m = valideaza_cnp(c)
        return v, "cnp", m
    v, m = valideaza_cui(c)
    return v, "cui", m
