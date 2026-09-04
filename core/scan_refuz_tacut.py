# -*- coding: utf-8 -*-
"""core/scan_refuz_tacut.py — cate refuzuri ale serverului nu ajung la om.

Cerut de Costin, 27.08.2026: *„Măsoară clasa: câte formulare din aplicație pot refuza fără să
afișeze motivul?"* Instanța lui: o jumătate de oră pierdută pe „butonul nu face nimic".

CE MĂSOARĂ, exact: fiecare `catch` din `static/js` al cărui `try` conține un apel `api.*`, și
dacă **corpul lui arată ceva omului**. „Arată" = una din căile canonice de prezentare
(`arataMesaj`, `eroareCamp`, `arataEroare`, `confirmaCaseta`), o scriere în `innerHTML`/
`textContent`, sau o re-aruncare (`throw`) — care mută răspunderea mai sus.

CELE CINCI MODURI DE EȘEC ALE ACESTUI INSTRUMENT, scrise înainte de prima măsurătoare
(interdicția 76):
  1. **nu execută JS.** Un `catch` care cheamă o funcție proprie care afișează (`arata(e)`) e
     numărat drept MUT. Deci cifra „mute" e un **plafon superior**.
  2. **potrivirea blocurilor e pe acolade**, nu pe un arbore de sintaxă. Pe cod valid ține;
     pe cod cu acolade în șiruri ar aluneca — de aceea șirurile și comentariile se **albesc**
     întâi, cu cititorul reparat pe 27.08 (cel care înțelege `${…}`).
  3. **nu știe dacă apelul e declanșat de om.** Deosebește după METODĂ (scriere vs citire),
     ceea ce e un proxy: un `GET` cerut de om la apăsarea unui buton e tratat ca citire.
  4. **nu vede refuzurile care nu trec prin `api.*`** (`fetch` direct). Numărate separat.
  5. **[04.09.2026] statea pe un cititor orb.** Reparat si mutat in `core/cititor_js.py`;
     remasurat pe acelasi commit `277e4300`, cifra a urcat de la 16 la 18 — orbire, nu
     regresie. Vezi `core/test_cititor_js.py`.

CE NU MĂSOARĂ, declarat: dacă mesajul afișat e BUN. Doar dacă există vreunul.
"""
import io
import os
import re

# Cititorul de JS e COMUN din 04.09.2026. Pana atunci traia in DOUA copii — aici si in
# `core/test_aritmetica_in_prezentare.py` — si amandoua purtau acelasi defect: un sir
# `'` sau `"` neinchis pe randul lui albea tot pana la urmatoarea ghilimea din FISIER.
from core.cititor_js import fara_siruri

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_JS = os.path.join(_RAD, "static", "js")

_SCRIERE = re.compile(r"\bapi\.(post|put|del|patch|postForm|cereForm)\b")
_CITIRE = re.compile(r"\bapi\.get\b")
_FETCH = re.compile(r"(?<![\w.])fetch\s*\(")
# Calibrat 27.08.2026 pe instante REALE: `insertAdjacentHTML` chiar afiseaza
# mesajul (cabinet.js:542, flux_concediu.js:66, citite una cate una). Fara el,
# detectorul supra-raporta - iar o cifra umflata e la fel de rea ca una mica.
_ARATA = re.compile(r"\b(arataMesaj|eroareCamp|arataEroare|confirmaCaseta|alert)\s*\(|"
                    r"\.insertAdjacent(HTML|Text)\s*\(|"
                    r"\.(innerHTML|textContent|innerText)\s*=|\bthrow\b")


# ── potrivirea blocurilor ───────────────────────────────────────────────────
def _bloc(curat, i):
    """De la `{` de la poziția i, indexul de după `}` potrivit."""
    adanc, j = 0, i
    while j < len(curat):
        if curat[j] == "{":
            adanc += 1
        elif curat[j] == "}":
            adanc -= 1
            if adanc == 0:
                return j + 1
        j += 1
    return len(curat)


def perechi(curat):
    """[(start_try, corp_try, corp_catch, poz)] pentru fiecare `try {…} catch …{…}`."""
    out = []
    for m in re.finditer(r"\btry\s*\{", curat):
        i = curat.index("{", m.start())
        sf_try = _bloc(curat, i)
        rest = curat[sf_try:sf_try + 120]
        mc = re.match(r"\s*catch\s*(\([^)]*\))?\s*\{", rest)
        if not mc:
            continue                      # try/finally — nu înghite nimic
        j = curat.index("{", sf_try + mc.start())
        out.append((m.start(), curat[i:sf_try], curat[j:_bloc(curat, j)]))
    return out


def masoara():
    """{scrieri_mute, citiri_mute, cu_mesaj, fetch_direct, detalii}."""
    rez = {"scrieri_mute": [], "citiri_mute": [], "cu_mesaj": 0, "fetch_direct": []}
    for rad, _d, nume in os.walk(_JS):
        for f in sorted(nume):
            if not f.endswith(".js"):
                continue
            cale = os.path.join(rad, f)
            rel = os.path.relpath(cale, _JS)
            src = io.open(cale, encoding="utf-8").read()
            curat = fara_siruri(src)
            for poz, corp_try, corp_catch in perechi(curat):
                linia = curat.count("\n", 0, poz) + 1
                scrie = bool(_SCRIERE.search(corp_try))
                citeste = bool(_CITIRE.search(corp_try))
                if not (scrie or citeste):
                    continue
                if _ARATA.search(corp_catch):
                    rez["cu_mesaj"] += 1
                elif scrie:
                    rez["scrieri_mute"].append((rel, linia))
                else:
                    rez["citiri_mute"].append((rel, linia))
            for m in _FETCH.finditer(curat):
                rez["fetch_direct"].append((rel, curat.count("\n", 0, m.start()) + 1))
    return rez


if __name__ == "__main__":
    r = masoara()
    print("catch-uri peste un apel `api.*` care ARATĂ ceva:      %d" % r["cu_mesaj"])
    print("SCRIERI care pot refuza fără să arate motivul:        %d" % len(r["scrieri_mute"]))
    for x in r["scrieri_mute"]:
        print("    %s:%d" % x)
    print("citiri mute (badge/opțional — cost mai mic):          %d" % len(r["citiri_mute"]))
    for x in r["citiri_mute"][:20]:
        print("    %s:%d" % x)
    print("`fetch(` direct, în afara clientului:                 %d" % len(r["fetch_direct"]))
    for x in r["fetch_direct"]:
        print("    %s:%d" % x)
