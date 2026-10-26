# -*- coding: utf-8 -*-
"""Lotul 13 (comanda Costin 13.1), fork P1 al subagentului PORTAL — forma dovezilor și a mutațiilor (ca `test_lot12_verif_dovezi.py`):

  * `frontend_test/dovada/dovezi_lot13_portal_p1.json`: fiecare dovadă are o firmă a copiei, pași și verificări cunoscute de
    `frontend_test/dovada/pasi.py`, captura numită ca în registru (`core/test_deficiente._RE_CAPTURA`); o dovadă `portal` cere contul de
    client al copiei (`utilizator`);
  * `frontend_test/e2e/mut_lot13_portal_p1.json`: fiecare mutație are ancora EXACT o dată în fișierul ei și un test e2e care există.

Temei: N/A — tooling. Rulează după aplicarea peticelor (`l13_petice/portal_p1_*.json`): unele ancore stau în codul adus de ele.
"""
import json
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOVEZI = os.path.join(RAD, "frontend_test", "dovada", "dovezi_lot13_portal_p1.json")
MUTATII = os.path.join(RAD, "frontend_test", "e2e", "mut_lot13_portal_p1.json")


def test_dovezile_au_forma_registrului():
    sys.path.insert(0, os.path.join(RAD, "frontend_test", "dovada"))
    import pasi
    from core.test_deficiente import _RE_CAPTURA
    copii = {"tenant_%d" % n for n in range(9049, 9058)}
    rele = []
    dovezi = json.load(open(DOVEZI, encoding="utf-8"))
    for x in dovezi:
        if x["firma"] not in copii:
            rele.append("%s: firma %r nu e în copie" % (x["nr"], x["firma"]))
        if x.get("portal") and not x.get("utilizator"):
            rele.append("%s: dovada din portal fără contul de client" % x["nr"])
        if not re.match(_RE_CAPTURA % re.escape(x["nr"].lower()), "dovezi/lot13/" + x["captura"]):
            rele.append("%s: captura %s" % (x["nr"], x["captura"]))
        rele += ["%s: pas necunoscut %s" % (x["nr"], p) for p in x["pasi"] if not set(p) & set(pasi.PASI)]
        rele += ["%s: verificare necunoscută %s" % (x["nr"], v) for v in x["verifica"] if not set(v) & set(pasi.VERIFICARI)]
    assert len(dovezi) >= 9 and not rele, rele


def test_mutatiile_au_ancora_o_data_si_testul_lor():
    mut = json.load(open(MUTATII, encoding="utf-8"))
    rele = []
    for m in mut:
        n = open(os.path.join(RAD, m["fisier"]), encoding="utf-8").read().count(m["ancora"])
        if n != 1:
            rele.append("%s: ancora apare de %d ori" % (m["fisier"], n))
        fis, test = m["test"].split("::")
        if ("def %s(" % test) not in open(os.path.join(RAD, fis), encoding="utf-8").read():
            rele.append("%s: testul nu există" % m["test"])
    assert len(mut) >= 11 and not rele, rele
