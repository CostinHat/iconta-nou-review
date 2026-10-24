# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.1 pct.13–14, pachetul `verif`: forma dovezilor și a mutațiilor pachetului, verificată fără browser.

  * `frontend_test/dovada/dovezi_lot12_verif.json` — fiecare dovadă are o firmă a copiei (F1–F6, FISCALOS: `tenant_9049` … `tenant_9055`),
    pași și verificări cunoscute de `frontend_test/dovada/pasi.py`, captura numită cum o cere registrul (`core/test_deficiente._RE_CAPTURA`,
    importată, nu copiată), capturi unice; numerele cerute de pct.14 (în afară de 241 și 254, fără text) sunt toate acolo.
  * `frontend_test/e2e/mut_lot12_verif.json` — fiecare mutație are ancora EXACT o dată în fișierul ei (altfel `scripts/e2e_poarta.py
    --mutatie=` se oprește cu „ancora lipsește”, iar o ancoră dublă ar strica alt loc decât cel probat) și numește un test care există;
    fiecare test `test_def_*` din `e2e_lot12_verif.py` are cel puțin o mutație (un test fără mutație nu dovedește nimic).

N/A temei fiscal — gardă de formă (CLAUDE.md §4: „rezolvată” = dovadă pe ecran + test de capăt la capăt dovedit prin mutație)."""
import json
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOVEZI = os.path.join(RAD, "frontend_test", "dovada", "dovezi_lot12_verif.json")
MUTATII = os.path.join(RAD, "frontend_test", "e2e", "mut_lot12_verif.json")
E2E = os.path.join(RAD, "frontend_test", "e2e", "e2e_lot12_verif.py")
COPII = {"tenant_9049", "tenant_9050", "tenant_9051", "tenant_9052", "tenant_9053", "tenant_9054", "tenant_9055"}
#: comanda 12.1 pct.14, verbatim: „5, 62, 96, 119, 122, 124, 127, 135, 170, 202, 215, 216, 241, 254, 280, 283, 290” — fără 241 și 254,
#: al căror text nu există (raportul pachetului)
PCT14 = {"5", "62", "96", "119", "122", "124", "127", "135", "170", "202", "215", "216", "280", "283", "290"}


def _dovezi():
    return json.load(open(DOVEZI, encoding="utf-8"))


def test_dovezile_au_forma_pe_care_o_parcurge_pasi_py():
    """MUTAȚIE: o captură `C60_f2_x.png` (majusculă), o firmă `tenant_049` (sursa, nu copia) sau un pas necunoscut -> pică."""
    sys.path.insert(0, os.path.join(RAD, "frontend_test", "dovada"))
    import pasi
    from core.test_deficiente import _RE_CAPTURA
    rele, toate = [], []
    dovezi = _dovezi()
    assert dovezi, "anti-vacuu: fișierul dovezilor e gol"
    for x in dovezi:
        if x["firma"] not in COPII:
            rele.append("%s: firma %r nu e a copiei" % (x["nr"], x["firma"]))
        capturi = [x["captura"]] + [p["captura"] for p in x["pasi"] if p.keys() >= {"captura"}]
        toate += capturi
        rele += ["%s: captura %s nu are forma registrului" % (x["nr"], c) for c in capturi
                 if not re.match(_RE_CAPTURA % re.escape(x["nr"].lower()), "dovezi/lot12/" + c)]
        rele += ["%s: pas necunoscut %s" % (x["nr"], p) for p in x["pasi"] if not set(p) & set(pasi.PASI)]
        rele += ["%s: verificare necunoscută %s" % (x["nr"], v) for v in x["verifica"] if not set(v) & set(pasi.VERIFICARI)]
        if not x["verifica"] or not x["pasi"]:
            rele.append("%s: fără pași sau fără verificări (o captură fără text verificat nu e dovadă)" % x["nr"])
        if x.keys() >= {"posibila_de_la"} and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", x["posibila_de_la"]):
            rele.append("%s: posibila_de_la %r nu e ZZZZ-LL-ZZ" % (x["nr"], x["posibila_de_la"]))
    rele += ["captura %s apare de două ori" % c for c in sorted(set(toate)) if toate.count(c) > 1]
    assert not rele, "\n".join(rele)


def test_numerele_pct14_au_dovada_pe_firmele_de_test():
    """MUTAȚIE: scoasă dovada lui 280 din listă -> pică, cu numărul lipsă."""
    numere = {x["nr"] for x in _dovezi()}
    assert PCT14 <= numere, sorted(PCT14 - numere)


def test_mutatiile_au_ancora_unica_si_testul_lor():
    """MUTAȚIE: o ancoră schimbată cu un caracter (nu mai e în fișier) sau un test redenumit -> pică."""
    mutatii = json.load(open(MUTATII, encoding="utf-8"))
    rele = []
    for m in mutatii:
        text = open(os.path.join(RAD, m["fisier"]), encoding="utf-8").read()
        if text.count(m["ancora"]) != 1:
            rele.append("%s: ancora apare de %d ori: %r" % (m["fisier"], text.count(m["ancora"]), m["ancora"][:80]))
        if m["ancora"] == m["inlocuire"]:
            rele.append("%s: mutația nu schimbă nimic" % m["fisier"])
        fisier, functie = m["test"].split("::")
        if not re.search(r"^def %s\(" % re.escape(functie), open(os.path.join(RAD, fisier), encoding="utf-8").read(), re.M):
            rele.append("testul %s nu există" % m["test"])
    teste = re.findall(r"^def (test_def_\w+)\(", open(E2E, encoding="utf-8").read(), re.M)
    cu_mutatie = {m["test"].split("::")[1] for m in mutatii if m["test"].startswith("frontend_test/e2e/e2e_lot12_verif.py::")}
    rele += ["%s n-are nicio mutație" % t for t in teste if t not in cu_mutatie]
    assert len(teste) >= 4, "anti-vacuu: %s" % teste
    assert not rele, "\n".join(rele)
