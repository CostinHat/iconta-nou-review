# -*- coding: utf-8 -*-
"""Lotul 13, zona admin (plasa e2e, 26.10.2026): „confirmaCaseta is not defined” în Panou Admin -> Anunțuri / Invitații — `admin.js`
chema `confirmaCaseta` din `api.js` fără s-o importe; clicul pe „Trimite” / „Retrage” arunca o eroare JS și confirmarea nu se deschidea
(646 a-c și 646 e roșii). Niciun gard nu vedea un nume nedefinit într-un modul ES: `node --check` verifică numai sintaxa.

GARD: în fiecare modul din `static/js`, o funcție exportată de `api.js` chemată ca nume liber (`confirmaCaseta(…)`, nu `api.x(…)` /
`obj.x(…)`) e importată (static sau din `await import`), definită local ori primită ca parametru. Limită: numai exporturile lui
`api.js` (mecanismele comune, unde s-a întâmplat); un nume nedefinit venit din alt modul nu e prins aici."""
import glob
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _exporturi(text):
    return set(re.findall(r"export (?:async )?function\*? (\w+)", text)) | set(re.findall(r"export (?:const|let) (\w+)", text))


def nedefinite(text, exporturi):
    """PURĂ. Exporturile lui api.js chemate ca nume liber în `text`, fără import / definiție locală / parametru."""
    t = re.sub(r"//[^\n]*|/\*.*?\*/", "", text, flags=re.S)
    importate = set()
    for blk in re.findall(r"\{([^{}]*)\}\s*(?:=\s*await\s+import|from)", t):
        importate |= {x.strip().split(":")[-1].split(" as ")[-1].strip() for x in blk.split(",") if x.strip()}
    locale = set(re.findall(r"(?:function\*?|const|let|var|class)\s+(\w+)", t))
    locale |= set(re.findall(r"(?m)^\s*(?:async\s+)?(\w+)\s*\([^()]*\)\s*\{", t))   # metodă a unui obiect: `deschide(titlu, …) {`
    for g in re.findall(r"\(([^()]*)\)\s*(?:=>|\{)", t):
        locale |= {x.strip().split("=")[0].strip(" .{}[]") for x in g.split(",")}
    # chemarea se scrie lipit („confirmaCaseta(”); „pe activ (la …)” dintr-un text nu e o chemare
    return sorted(n for n in exporturi - importate - locale if re.search(r"(?<![\w.$'\"`:])%s\(" % re.escape(n), t))


def test_functiile_din_api_js_chemate_sunt_importate():
    api = io.open(os.path.join(RAD, "static", "js", "api.js"), encoding="utf-8").read()
    exp = _exporturi(api)
    assert {"confirmaCaseta", "arataMesaj", "atributeInactiv"} <= exp, "anti-vacuu: exporturile lui api.js nu s-au citit"
    rele, vazute = [], 0
    for p in sorted(glob.glob(os.path.join(RAD, "static", "js", "**", "*.js"), recursive=True)):
        if os.path.basename(os.path.dirname(p)) == "dist" or p.endswith(os.path.join("js", "api.js")):
            continue
        vazute += 1
        lipsa = nedefinite(io.open(p, encoding="utf-8").read(), exp)
        if lipsa:
            rele.append("%s: %s" % (os.path.relpath(p, RAD), ", ".join(lipsa)))
    assert vazute > 50, "anti-vacuu: %d module" % vazute
    assert not rele, "funcții din api.js chemate fără import (eroare JS la clic, nu la încărcare):\n" + "\n".join(rele)


def test_calibrare_numele_neimportat_e_prins_cel_importat_nu():
    exp = {"confirmaCaseta", "esc"}
    assert nedefinite('import { esc } from "../api.js";\nb.onclick = () => confirmaCaseta(b, esc(x));', exp) == ["confirmaCaseta"]
    assert nedefinite('import { esc, confirmaCaseta } from "../api.js";\nconfirmaCaseta(b, esc(x));', exp) == []
    assert nedefinite('const { confirmaCaseta } = await import("../api.js");\nconfirmaCaseta(b);', exp) == []
    assert nedefinite("api.confirmaCaseta(b); obj.esc(1);", exp) == []
