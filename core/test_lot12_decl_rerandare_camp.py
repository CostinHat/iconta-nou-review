# -*- coding: utf-8 -*-
"""[lotul 12, găsită la e2e-ul 493] Un câmp de text / număr din formularele Declarațiilor nu re-desenează, la „change”, zona care îl conține.

Ce se întâmpla (static/js/ecrane/declaratii.js): `#d177-srest`, `#d107-val2ni`, `#d107-val3ni`, `#d603-tara` au la „change” `randeazaFormularD177/107`, adică
`zona.innerHTML = …` peste formularul în care stă chiar câmpul. Pentru un câmp de text „change” vine la ieșirea din câmp: contabilul scrie
suma rămasă și apasă direct „+ adaugă” (sau „Regenerează”) -> mousedown scoate focusul -> „change” -> zona se re-desenează și butonul apăsat
e înlocuit înainte de mouseup -> clicul se pierde. Cu un „change” trimis cât câmpul are încă focusul și o valoare neconfirmată, re-desenarea
scoate câmpul, browserul trimite al doilea „change” la blur, iar a doua re-desenare în mijlocul primeia aruncă „Failed to set the
'innerHTML' property … Perhaps it was moved in a 'blur' event handler?” (e2e_lot12_decl.py::test_def_493_…, 23.10.2026).
Regula: la „change” pe un câmp de text / număr se actualizează starea și textul derivat (totalurile), nu zona întreagă. Selecturile și
bifele confirmă valoarea în momentul alegerii (fără valoare neconfirmată la blur), deci re-desenarea după ele rămâne permisă.

GARDĂ statică: niciun `gv("#X").addEventListener("change"|"input"|"blur"|"focusout", …randeazaFormular…)` pe un `<input>` text/număr sau
`<textarea>`. MUTAȚIE: anti-vacuul de jos (un fragment cu tiparul) trebuie prins; pe fișierul de azi garda numește cele patru câmpuri.
"""
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ASC = re.compile(r'gv\("#([\w-]+)"\)\.addEventListener\("(?:change|input|blur|focusout)"[^\n]*randeazaFormular')


def incalcari(js):
    """[(id, tag)] — câmpurile de text / număr (sau textarea) a căror „change” / „input” / „blur” re-desenează formularul care le conține."""
    out = []
    for cid in _ASC.findall(js):
        m = re.search(r'<(input|textarea|select)\b[^>]*\bid="%s"[^>]*>' % re.escape(cid), js)
        if not m:
            continue
        tag = m.group(1)
        if tag == "select":
            continue
        tip = re.search(r'\btype="(\w+)"', m.group(0))
        if tag == "input" and tip and tip.group(1) in ("checkbox", "radio", "date"):
            continue
        out.append((cid, tag))
    return out


def test_detectorul_vede_tiparul():
    bun = '<select id="a-x"></select>\n  gv("#a-x").addEventListener("change", () => { randeazaFormularA(corp, nav); });'
    rau = '<input id="a-y" type="number">\n  gv("#a-y").addEventListener("change", (e) => { S.a = e.target.value; randeazaFormularA(corp, nav); });'
    assert incalcari(bun) == [] and incalcari(rau) == [("a-y", "input")]


def test_campul_de_text_nu_redeseneaza_zona_lui():
    js = open(os.path.join(RAD, "static", "js", "ecrane", "declaratii.js"), encoding="utf-8").read()
    assert incalcari(js) == [], ("câmpuri de text / număr care re-desenează formularul la „change” (clicul următor se pierde; „change” dublu "
                                 "la blur aruncă eroarea innerHTML): %s — actualizează numai starea și totalurile" % incalcari(js))
