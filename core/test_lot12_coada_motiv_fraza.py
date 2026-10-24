# -*- coding: utf-8 -*-
"""Lotul 12, deficiența 499 (fost N17, Costin 09.10.2026): „Coadă: mesajul de respingere se termină cu punct dublu.”

CAUZA. Motivul respingerii e scris de om („Lipsește factura furnizorului.”), iar ecranele îl puneau într-o propoziție urmată de alta
cu un punct adăugat orb: `Respinsă la validare: ${motiv}. Corecteaz-o…` -> „…furnizorului.. Corecteaz-o”. CLASA: orice loc care pune
motivul scris de om (`motiv_respingere`, din `public.declaratii_coada`) într-o propoziție încheiată cu punct.

REPARAȚIA. O singură definiție, `motivInFraza` (`static/js/ecrane/coada_trimite.js`): punctul se adaugă numai dacă omul nu și-a
încheiat fraza (., !, ?, …). Datele existente: motivele vechi rămân cum le-a scris omul (nimic nu se rescrie în bază); afișarea le
încheie corect — acoperite de cod.

GARDA. (1) Niciun fișier JS nu mai interpolează `motiv_respingere` urmat direct de „.” (un drum nou cu punctul orb pică aici).
(2) `motivInFraza` se comportă cum spune (rulată cu node, pe sursa ei). Temei: N/A — text de ecran (CLAUDE.md §9: texte directe).
LIMITA: garda citește câmpul `motiv_respingere`; un alt câmp cu text de om pus într-o frază ar cere adăugarea lui în `CAMPURI`."""
import glob
import os
import subprocess

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#: câmpurile cu motivul scris de om, citite de ecrane
CAMPURI = ("motiv_respingere",)


def _interpolari(sursa, camp):
    """(linie, text, caracterul de după) pentru fiecare `${…camp…}` din sursă — acolada închisă numărată, nu ghicită."""
    out, i = [], 0
    while True:
        j = sursa.find(camp, i)
        if j < 0:
            return out
        k = sursa.rfind("${", 0, j)
        i = j + len(camp)
        if k < 0:
            continue
        adanc, p = 0, k + 1
        while p < len(sursa):
            if sursa[p] == "{":
                adanc += 1
            elif sursa[p] == "}":
                adanc -= 1
                if adanc == 0:
                    break
            p += 1
        if p >= len(sursa) or p < j:   # câmpul nu e în interpolarea găsită
            continue
        out.append((sursa.count("\n", 0, k) + 1, sursa[k:p + 1], sursa[p + 1:p + 2]))


def test_motivul_scris_de_om_nu_e_urmat_de_punct_orb():
    rele = []
    for f in sorted(glob.glob(os.path.join(RAD, "static", "js", "**", "*.js"), recursive=True)):
        s = open(f, encoding="utf-8").read()
        for camp in CAMPURI:
            for linie, text, dupa in _interpolari(s, camp):
                # [499] „${motiv}.” dă „..” când omul și-a încheiat fraza; locul trece prin `motivInFraza`
                if dupa == "." and "motivInFraza(" not in text:
                    rele.append("%s:%d %s." % (os.path.relpath(f, RAD), linie, text[:120]))
    assert not rele, "motivul scris de om, urmat de un punct adăugat orb (deficiența 499, folosește motivInFraza):\n" + "\n".join(rele)


def _motiv_in_fraza(valori):
    src = os.path.join(RAD, "static", "js", "ecrane", "coada_trimite.js")
    prog = ("const fs = require('fs'); const s = fs.readFileSync(%r, 'utf8');"
            "const m = s.match(/export function motivInFraza[\\s\\S]*?\\n}\\n/); if (!m) { console.log('LIPSA'); process.exit(3); }"
            "const f = new Function(m[0].replace('export ', '') + '; return motivInFraza;')();"
            "console.log(JSON.stringify(%s.map((x) => f(x))));") % (src, _json(valori))
    r = subprocess.run(["node", "-e", prog], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr
    import json
    return json.loads(r.stdout.strip().splitlines()[-1])


def _json(x):
    import json
    return json.dumps(x, ensure_ascii=False)


def test_motiv_in_fraza_pune_punctul_o_singura_data():
    # [499] fraza omului încheiată rămâne cum e; neîncheiată primește punctul; gol -> „fără motiv.”
    assert _motiv_in_fraza(["lipsește factura", "Lipsește factura furnizorului.", "Unde e factura?", "  corectează contul!  ",
                            "", None, "vezi contractul…"]) == [
        "lipsește factura.", "Lipsește factura furnizorului.", "Unde e factura?", "corectează contul!", "fără motiv.", "fără motiv.",
        "vezi contractul…"]
