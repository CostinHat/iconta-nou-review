# -*- coding: utf-8 -*-
"""Lotul 12, pachetul TEXTE: forma dovezilor (`frontend_test/dovada/dovezi_lot12_texte.json`) și a mutațiilor de capăt la capăt
(`frontend_test/e2e/mut_lot12_texte.json`), verificată fără browser — aceleași reguli ca la pachetul `verif`
(`core/test_lot12_verif_dovezi.py`), pe fișierele pachetului: firma copiei, pașii și verificările știute de `pasi.py`, captura în forma
registrului, ancora unei mutații EXACT o dată în fișierul ei, fiecare `test_def_*` din `e2e_lot12_texte.py` cu cel puțin o mutație.

N/A temei fiscal — gardă de formă."""
import json
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOVEZI = os.path.join(RAD, "frontend_test", "dovada", "dovezi_lot12_texte.json")
MUTATII = os.path.join(RAD, "frontend_test", "e2e", "mut_lot12_texte.json")
E2E = os.path.join(RAD, "frontend_test", "e2e", "e2e_lot12_texte.py")
COPII = {"tenant_9049", "tenant_9050", "tenant_9051", "tenant_9052", "tenant_9053", "tenant_9054", "tenant_9055"}


def test_dovezile_au_forma_pe_care_o_parcurge_pasi_py():
    """MUTAȚIE: captura `C132_f1_vechi_supervizor.png` (majusculă) -> pică."""
    sys.path.insert(0, os.path.join(RAD, "frontend_test", "dovada"))
    import pasi
    from core.test_deficiente import _RE_CAPTURA
    rele, toate = [], []
    dovezi = json.load(open(DOVEZI, encoding="utf-8"))
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
            rele.append("%s: fără pași sau fără verificări" % x["nr"])
    rele += ["captura %s apare de două ori" % c for c in sorted(set(toate)) if toate.count(c) > 1]
    assert not rele, "\n".join(rele)


def test_mutatiile_au_ancora_unica_si_testul_lor():
    """MUTAȚIE: ancora mutației 184 schimbată cu un caracter (nu mai e în `core/pontaj.py`) -> pică."""
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
    cu_mutatie = {m["test"].split("::")[1] for m in mutatii}
    rele += ["%s n-are nicio mutație" % t for t in teste if t not in cu_mutatie]
    assert sorted(teste) == sorted({"test_def_172_supervizorul_fara_d101_depus_vorbeste_limba_contabilului",
                                    "test_def_c132_supervizorul_spune_axa_d101_in_limba_contabilului",
                                    "test_def_163_mesajul_cheii_api_fara_majuscule_si_cu_diacritice",
                                    "test_def_45_mesajul_cheii_api_vine_in_vedere",
                                    "test_def_45_refuzul_emailului_facturii_vine_in_vedere",
                                    "test_def_45_confirmarea_modelului_de_factura_vine_in_vedere",
                                    "test_def_184_refuzul_pontajului_scrie_luna_ca_LL_AAAA"}), teste
    assert not rele, "\n".join(rele)
