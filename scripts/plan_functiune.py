# -*- coding: utf-8 -*-
"""scripts/plan_functiune.py — generează `core/plan_functiune.py`: funcțiunea contabilă (A / P / A/P) a fiecărui cont din planul general,
citită din OMFP 1802/2014 pct.594 (`anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`).

[deficiența 369, comanda Costin 8.2, 18.10.2026] „Funcțiunea (A/P/B) trebuie să fie cea din planul OMFP, analiticele o moștenesc de la
sintetic”. Temei: OMFP 1802/2014 pct.593 alin.(2): „Conturile pot avea funcțiune contabilă de activ (A), pasiv (P) sau sunt bifuncționale
(A/P). În general, conturile cu funcțiune contabilă de activ corespund elementelor de natura activelor și cheltuielilor, iar conturile cu
funcțiune contabilă de pasiv corespund elementelor de natura datoriilor, capitalurilor proprii și veniturilor [...]. În conturile cu trei
cifre, cifra terminală 9 semnifică operațiuni de sens contrar celor acoperite în mod normal de conturile de nivel superior din grupa din
care fac parte.”

Regulile, în ordine: (1) marcajul scris lângă cont în pct.594; (2) contul fără marcaj moștenește de la sinteticul lui (2111 de la 211);
(3) sinteticul fără marcaj ia marcajul analiticelor, dacă e același pe toate, altfel A/P; (4) clasele 6 și 7, scrise în pct.594 fără
marcaj, după pct.593 alin.(2): cheltuielile A, veniturile P, iar contul cu cifra terminală 9 (609, 709) e de sens contrar. Clasa 8
(conturi în afara bilanțului, pct.593 alin.(3)) și clasa 9 nu au funcțiune de bilanț — nu intră.

Uz: python scripts/plan_functiune.py          -> rescrie core/plan_functiune.py
    python scripts/plan_functiune.py --verifica -> 0 identic / 1 diferă (garda: core/test_plan_functiune.py)
"""
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SURSA = os.path.join(RAD, "anaf_surse", "omfp_1802_2014_reglementari_consolidat.txt")
IESIRE = os.path.join(RAD, "core", "plan_functiune.py")


def extrage(text=None):
    """[lotul 9, 19.10.2026 — o singură extragere a planului] Conturile și marcajul scris lângă ele vin din `core/plan_conturi_omfp.PLAN`
    (extragerea unică a pct.594, `scripts/plan_conturi_omfp.py`, cu corecturile ei pe listă închisă); aici se aplică numai regulile
    (2)–(4). Până azi acest script avea parserul lui, iar cele două extrageri ale aceluiași text difereau (1496, 4315, 463 lipseau de
    aici, 2016 era în plus). Clasele 8 și 9 nu au funcțiune de bilanț — nu intră. `text` rămâne în semnătură pentru apelanții vechi."""
    sys.path.insert(0, RAD)
    from core.plan_conturi_omfp import PLAN
    conturi = [c for c in PLAN if c[0] not in "89"]
    scris = {c: PLAN[c][1] for c in conturi if PLAN[c][1]}
    conturi = list(dict.fromkeys(conturi))
    out = {}
    for c in conturi:
        if c in scris:
            out[c] = scris[c]
        elif c[0] in "67":
            normal = "A" if c[0] == "6" else "P"
            out[c] = ("P" if normal == "A" else "A") if (len(c) == 3 and c[-1] == "9") or (len(c) == 4 and c[:3][-1] == "9") else normal
    for c in conturi:                       # (2) analiticul fără marcaj, de la sintetic
        if c not in out and len(c) == 4 and c[:3] in out:
            out[c] = out[c[:3]]
    for c in conturi:                       # (3) sinteticul fără marcaj, din analitice
        if c not in out and len(c) == 3:
            fii = {out[x] for x in conturi if len(x) == 4 and x.startswith(c) and x in out}
            if fii:
                out[c] = fii.pop() if len(fii) == 1 else "A/P"
    for c in conturi:                       # analiticele rămase, după sinteticul completat la (3)
        if c not in out and len(c) == 4 and c[:3] in out:
            out[c] = out[c[:3]]
    return out


def randeaza(f):
    linii = ['# -*- coding: utf-8 -*-',
             '"""core/plan_functiune.py — GENERAT de `scripts/plan_functiune.py` din OMFP 1802/2014 pct.594 (nu se editează de mână; garda',
             '`core/test_plan_functiune.py` îl compară cu regenerarea). Funcțiunea contabilă a fiecărui cont din planul general: A (activ), P (pasiv),',
             'A/P (bifuncțional). [deficiența 369, comanda Costin 8.2] Analiticele firmei o moștenesc de la sintetic (`functiune`)."""',
             '',
             'FUNCTIUNE = {']
    for c in sorted(f):
        linii.append('    "%s": "%s",' % (c, f[c]))
    linii += ['}', '', '#: eticheta pe ecran (cu diacritice — 369: „Bifuncțional”)',
              'ETICHETA = {"A": "Activ", "P": "Pasiv", "A/P": "Bifuncțional"}', '', '',
              'def functiune(cont):',
              '    """„A” / „P” / „A/P” pentru un cont al firmei (analiticul „401.00012” sau „4111.1” moștenește de la cel mai lung cont din plan care',
              '    îl prefixează), sau None dacă nu e în planul general (clasa 8, 9, un cont inventat)."""',
              '    c = str(cont or "").strip().split(".")[0]',
              '    while c:',
              '        if c in FUNCTIUNE:',
              '            return FUNCTIUNE[c]',
              '        c = c[:-1]',
              '        if len(c) < 3:',
              '            return None',
              '    return None', '']
    return "\n".join(linii)


def main(argv):
    f = extrage()
    nou = randeaza(f)
    if "--verifica" in argv:
        vechi = open(IESIRE, encoding="utf-8").read() if os.path.exists(IESIRE) else ""
        print("identic" if vechi == nou else "diferă — regenerează: python scripts/plan_functiune.py")
        return 0 if vechi == nou else 1
    open(IESIRE, "w", encoding="utf-8").write(nou)
    print("scris %s: %d conturi" % (IESIRE, len(f)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
