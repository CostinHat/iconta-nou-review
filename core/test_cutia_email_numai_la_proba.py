# -*- coding: utf-8 -*-
"""Cutia poștală de test (`ICONTA_EMAIL_CUTIE`, `core/observare._in_cutia_de_test`, lotul 4 — 15.10.2026) există NUMAI pe aplicația
de probă: pe producție, un email scris într-un fișier în loc să plece ar fi o confirmare de înregistrare care nu ajunge niciodată (iar
„emailul a plecat” ar fi fals). Garda: mediul producției (fișierele din `~/.iconta` încărcate de unitatea `iconta-nou`, unitatea de
referință) nu poartă variabila; rulatorul plasei o pune.
La fel cheile de TEST ale Cloudflare Turnstile (257): trec mereu, deci pe producție ar deschide formularul oricărui robot — mediul
producției nu le poartă (iar `inregistrare_libera.chei_turnstile` le refuză oricum fără cutia de test); rulatorul plasei le pune.
MUTAȚII: `Environment=ICONTA_EMAIL_CUTIE=...` sau `ICONTA_EMAIL_CUTIE=...` adăugat în `config_referinta_iconta-nou.service` -> pică;
`Environment=TURNSTILE_SECRET=1x0000000000000000000000000000000AA` adăugat acolo -> pică."""
import os
import re

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# oriunde pe un rând necomentat: `ICONTA_EMAIL_CUTIE=…` / `export …` (fișierele de mediu) și `Environment=ICONTA_EMAIL_CUTIE=…`
# (unitatea systemd) — prima formă a gărzii o căuta numai la început de rând, iar mutația cu `Environment=` a supraviețuit
_TIPAR = re.compile(r"^(?!\s*#).*\bICONTA_EMAIL_CUTIE\s*=", re.M)


def _surse_productie():
    unitate = os.path.join(_RAD, "config_referinta_iconta-nou.service")
    surse = [unitate]
    for linie in open(unitate, encoding="utf-8"):
        m = re.match(r"\s*EnvironmentFile=-?(\S+)", linie)
        if m:
            surse.append(m.group(1))
    return surse


def test_productia_nu_are_cutia_postala_de_test():
    surse = _surse_productie()
    assert len(surse) >= 3, ("anti-vacuu: unitatea de referință trebuie să numească fișierele de mediu (db.env, api_keys.env)", surse)
    cu_cutie = [s for s in surse if os.path.isfile(s) and _TIPAR.search(open(s, encoding="utf-8").read())]
    assert cu_cutie == [], "cutia poștală de test în mediul producției: %s" % cu_cutie


def test_rulatorul_plasei_o_pune():
    src = open(os.path.join(_RAD, "scripts", "e2e_poarta.py"), encoding="utf-8").read()
    assert len(re.findall(r'env\["ICONTA_EMAIL_CUTIE"\] = ', src)) == 1


def test_productia_nu_are_cheile_de_test_turnstile():
    from core import inregistrare_libera as il
    cu_chei = [s for s in _surse_productie() if os.path.isfile(s)
               and any(k in open(s, encoding="utf-8").read() for k in il.CHEI_DE_TEST)]
    assert cu_chei == [], "cheile de test Turnstile în mediul producției: %s" % cu_chei
    src = open(os.path.join(_RAD, "scripts", "e2e_poarta.py"), encoding="utf-8").read()
    assert sorted(re.findall(r'env\["(TURNSTILE_\w+)"\] = "(\w+)"', src)) == [("TURNSTILE_SECRET", il.CHEI_DE_TEST[5]),
                                                                          ("TURNSTILE_SITEKEY", il.CHEI_DE_TEST[0])]
