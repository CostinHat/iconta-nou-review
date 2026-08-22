# -*- coding: utf-8 -*-
"""scripts/vigoare_punct.py — vigoarea PE PUNCT, pentru actele structurate pe puncte (R2).

`scripts/vigoare_articol.py` verifică articole. Reglementările contabile (anexa OMFP 1802/2014) și
Normele OMFP 2634/2015 nu au articole, au PUNCTE — de aceea R2 a rămas deschisă.

CE FACE POSIBILĂ VERIFICAREA, și de ce e mai ieftină decât la articol: în forma consolidată, fiecare
marcaj de modificare **își spune singur adresa în actul de bază**, nu se deduce din poziție:

    (la 23-08-2024,
     Litera a) , Alineatul (2) , Punctul 9. , Sectiunea 1.3 , Capitolul 1 a fost modificată de
     Punctul 2. , Articolul I din ORDINUL nr. 4.164 din 12 august 2024, ...)

Deci un punct nu se caută în text; se citește din marcaj. Instrumentul e o citire de marcaje, nu o
analiză de structură.

LIMITA, declarată: vede DOAR punctele atinse de un marcaj de consolidare. Un punct fără marcaj e
NEMODIFICAT de la publicare — ceea ce e un răspuns, nu o necunoscută, dar e un răspuns care depinde de
completitudinea formei consolidate aduse. Amprenta fișierului e tipărită ca să se poată contrazice.
"""
import argparse
import hashlib
import io
import re
import sys

# „(la 23-08-2024," + o FEREASTRA fixa. NU pana la primul „)": adresa contine ea insasi paranteze
# inchise — „Litera a)", „Alineatul (2)" — iar prima forma a instrumentului se oprea acolo si rata
# „Punctul 9.". Prins la calibrare, pe un punct al carui raspuns era cunoscut.
_MARCAJ = re.compile(r"\(la (\d{2})-(\d{2})-(\d{4}),(.{0,700})", re.S)
_PUNCT = re.compile(r"Punctul\s+(\d+(?:\^\d+)?)\s*\.?\s*,", re.I)
_ACT = re.compile(r"(ORDINUL|ORDONAN[ȚT]A|LEGEA|HOT[ĂA]R[ÂA]REA)\s+nr\.?\s*([\d.^]+)\s+din\s+"
                  r"(\d+\s+\w+\s+\d{4})", re.I)
_FEL = re.compile(r"a fost (modificat|completat|abrogat|introdus)[a-zăâîșț]*", re.I)


def marcaje(text):
    """[(data_iso, punct, fel, act, brut)] — un rand per marcaj care numeste un PUNCT."""
    out = []
    for m in _MARCAJ.finditer(text):
        zi, luna, an, corp = m.group(1), m.group(2), m.group(3), m.group(4)
        # ADRESA e partea DINAINTE de „a fost ...": acolo se numeste punctul din actul de BAZA.
        # Dupa „a fost ... de" urmeaza punctul din actul MODIFICATOR — alt lucru, usor de confundat.
        taiat = _FEL.split(corp)[0]
        p = _PUNCT.search(taiat)
        if not p:
            continue
        fel = _FEL.search(corp)
        act = _ACT.search(corp)
        out.append({
            "data": "%s-%s-%s" % (an, luna, zi),
            "punct": p.group(1),
            "fel": (fel.group(1).lower() if fel else "?"),
            "act": ("%s %s/%s" % (act.group(1).lower(), act.group(2), act.group(3).split()[-1])
                    if act else "?"),
        })
    return out


# Actele nu numeroteaza punctele la fel: Reglementarile scriu „9. - (1) ...", Normele scriu
# „45. Registrul-jurnal ...". Prima forma a instrumentului cunostea doar tiparul cu liniuta si a
# raportat pe Anexa 1 „pct. 44-48 NEMODIFICATE" din ZERO puncte vazute — un raspuns vid, dat cu
# incredere. Se incearca amandoua si castiga cel care gaseste mai multe.
_TIPARE_PUNCT = (
    re.compile(r"(?<![\d^.])(\d+(?:\^\d+)?)\.\s*-\s"),
    re.compile(r"(?<![\d^.,)])(\d+(?:\^\d+)?)\.\s+(?=[A-ZĂÂÎȘȚ])"),
)


def _tipar(text):
    return max(_TIPARE_PUNCT, key=lambda p: len(p.findall(text)))


def intervale(text):
    """{punct: [(start, sfarsit)]} — un punct poate aparea de mai multe ori (forme multiple in acelasi
    fisier); se intorc TOATE apariile, nu prima. O forma initiala si una consolidata in acelasi fisier
    e chiar clasa de orbire scrisa in METODA."""
    poz = [(m.start(), m.group(1)) for m in _tipar(text).finditer(text)]
    d = {}
    for i, (st, p) in enumerate(poz):
        sf = poz[i + 1][0] if i + 1 < len(poz) else len(text)
        d.setdefault(p, []).append((st, sf))
    return d


def pe_punct(text):
    """{punct: [marcaje, cel mai recent primul]}

    DOUA cai de atribuire, fiindca niciuna singura nu ajunge:
      (a) marcajul NUMESTE punctul („Punctul 9. , Sectiunea 1.3 ...") — sigur, dar acopera doar 39 din
          cele 178 de marcaje ale actului;
      (b) marcajul CADE IN INTERVALUL punctului — prinde marcajele care numesc doar Sectiunea sau
          Capitolul, si care modifica totusi puncte.
    Fara (b), un punct atins printr-un marcaj de sectiune ar fi raportat „nemodificat" — adica exact
    afirmatia periculoasa, spusa cu incredere."""
    d = {}
    for m in marcaje(text):
        m["cum"] = "numit"
        d.setdefault(m["punct"], []).append(m)
    iv = intervale(text)
    for m in _MARCAJ.finditer(text):
        off = m.start()
        zi, luna, an, corp = m.group(1), m.group(2), m.group(3), m.group(4)
        fel = _FEL.search(corp)
        act = _ACT.search(corp)
        for p, spans in iv.items():
            if not any(st <= off < sf for st, sf in spans):
                continue
            r = {"data": "%s-%s-%s" % (an, luna, zi), "punct": p,
                 "fel": (fel.group(1).lower() if fel else "?"),
                 "act": ("%s %s/%s" % (act.group(1).lower(), act.group(2), act.group(3).split()[-1])
                         if act else "?"),
                 "cum": "in interval"}
            if not any(x["data"] == r["data"] and x["act"] == r["act"] for x in d.get(p, [])):
                d.setdefault(p, []).append(r)
    for k in d:
        d[k].sort(key=lambda x: x["data"], reverse=True)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fisier")
    ap.add_argument("puncte", nargs="*", help="punctele de verificat; gol = toate cele atinse")
    a = ap.parse_args()
    brut = io.open(a.fisier, "rb").read()
    text = brut.decode("utf-8", errors="replace")
    print("act    : %s" % a.fisier)
    print("amprentă: %s" % hashlib.sha256(brut).hexdigest())
    toate = marcaje(text)
    iv = intervale(text)
    d = pe_punct(text)
    print("puncte găsite în act: %d · marcaje de consolidare: %d, dintre care numesc un punct: %d"
          % (len(iv), len(_MARCAJ.findall(text)), len(toate)))
    # ANTI-VACUU: un instrument care nu vede niciun punct NU are voie sa raspunda la intrebari
    # despre puncte. Prima forma a raspuns „nemodificate" pe un act in care nu vazuse nimic.
    if not iv:
        print("\nREFUZ: n-am găsit NICIUN punct în acest act. Orice răspuns despre vigoarea unui punct\n"
              "ar fi vid. Tiparul de numerotare e altul — se adaugă în `_TIPARE_PUNCT`, nu se ocolește.")
        return 2
    print()
    cerute = a.puncte or sorted(d, key=lambda x: (len(x), x))
    lipsa = []
    for p in cerute:
        if p not in iv:
            print("  pct. %-5s NEGĂSIT ca punct în act — altceva decât «neatins de marcaje»." % p)
            continue
        ms = d.get(p)
        if not ms:
            lipsa.append(p)
            print("  pct. %-5s găsit în act, NEATINS de vreun marcaj -> nemodificat de la publicare" % p)
            continue
        ultim = ms[0]
        nap = len(intervale(text).get(p, []))
        avert = ("  ⚠ punctul apare de %d ori în fișier" % nap) if nap > 1 else ""
        print("  pct. %-5s ultima modificare %s  (%s de %s, atribuit «%s»)  · marcaje: %d%s"
              % (p, ultim["data"], ultim["fel"], ultim["act"], ultim["cum"], len(ms), avert))
        for m in ms[1:4]:
            print("           %s  %s de %s  («%s»)" % (m["data"], m["fel"], m["act"], m["cum"]))
    if lipsa:
        print("\nATENȚIE: pentru %d puncte răspunsul «nemodificat» depinde de completitudinea formei"
              " consolidate aduse — se citește împreună cu amprenta de mai sus." % len(lipsa))
    return 0


if __name__ == "__main__":
    sys.exit(main())
