# -*- coding: utf-8 -*-
"""scripts/scan_forme_punct.py — CÂT DE LARG prinde un tipar de punct, pe TOT corpusul.

**De ce există.** La R171, `articol_in_act` trebuia să învețe să citească PUNCTE. Riscul e scris în
gardul care se sprijină pe el: *o numărare prea largă transformă o trimitere în proză într-un titlu,
iar un document trece din refuz în răspuns fals* — iar direcția răspunsului fals e cea liniștitoare
(articolul pare mai stabil decât e, deci se reverifică mai rar exact unde trebuie mai des).

**Ce măsoară.** Pentru fiecare formă candidată de punct: câte potriviri are pe tot corpusul și, mai
important, **câte documente ies din CIOT** — adică trec din „refuz" în „răspuns". Baza de comparație
e numărul de titluri de ARTICOL, calculat cu tiparul de articole, nu cu `titluri()` (care numără deja
și puncte, din R171) — altfel măsurătoarea și-ar include propriul rezultat.

**Ce a decis, pe 06.09.2026** *(cifrele se recalculează rulând scriptul; aici stau ca reper)*:
  · forma îngustă `9. - `   → 1.834 potriviri · **11** documente ies din ciot  → IMPLEMENTATĂ
  · forma largă  `52. Text` → 9.983 potriviri · **84** documente ies din ciot  → **REFUZATĂ**
Cele 84 includ `d101_struct_anaf.txt` (64 de „puncte"), `d112_struct_anaf.txt` (44) și
`legea_207_2015_consolidat.txt` (373) — descrieri de structură XML și enumerări din proză. Față de
24 de citări cunoscute, raportul e disproporționat: **decizia 74** din `DECIZII.md`.

*O cifră care nu se poate recalcula nu e o măsurătoare, e o amintire* — de-aia instrumentul rămâne
în repo, nu doar rezultatul lui.

Rulare:  ./venv/bin/python scripts/scan_forme_punct.py
"""
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)

from core import articol_in_act as A  # noqa: E402

CORPUS = os.path.join(RAD, "anaf_surse")

#: Formele candidate, citite din acte — nu inventate. Cheia e cum se numesc în consemnare.
FORME = {
    "ingusta `9. - `": re.compile(r"(?:^|[\s(])\d{1,3}(?:\^\d+)?\.\s*[-–]\s"),
    "larga `52. Text`": re.compile(r"(?:^|[\s(])\d{1,3}\.\s+[A-ZÎȘȚĂÂ]"),
}


def documente():
    for nume in sorted(os.listdir(CORPUS)):
        if nume.endswith((".sha256", ".json")):
            continue
        cale = os.path.join(CORPUS, nume)
        if not os.path.isfile(cale):
            continue
        try:
            t, _ = A.din_fisier(cale)
        except Exception:  # noqa: BLE001  (un document necitibil nu e o formă de punct)
            continue
        yield nume, A.corp_util(t)


def masoara():
    """{forma: {potriviri, ies_din_ciot, documente}} + numărul de cioturi pe ARTICOLE."""
    rez = {f: {"potriviri": 0, "documente": []} for f in FORME}
    ciot_pe_articole = 0
    total = 0
    for nume, corp in documente():
        total += 1
        # baza: titluri de ARTICOL, cu tiparul de articole (nu `titluri()`, care numără și puncte)
        na = len(A._TITLURI_NUMARATE.findall(corp))
        ciot = na < A.PRAG_TITLURI
        ciot_pe_articole += ciot
        for f, rx in FORME.items():
            n = len(rx.findall(corp))
            rez[f]["potriviri"] += n
            if ciot and (na + n) >= A.PRAG_TITLURI:
                rez[f]["documente"].append((nume, n))
    return rez, ciot_pe_articole, total


def main():
    rez, ciot, total = masoara()
    print("documente de corpus: %d · CIOT pe titluri de ARTICOL: %d" % (total, ciot))
    print()
    for f in FORME:
        d = rez[f]
        print("%-20s potriviri %-6d  ies din ciot: %d"
              % (f, d["potriviri"], len(d["documente"])))
    print()
    for f in FORME:
        print("--- %s: documentele care trec din REFUZ in RASPUNS ---" % f)
        for nume, n in sorted(rez[f]["documente"], key=lambda x: -x[1])[:15]:
            print("   %-58s %d" % (nume[:58], n))
        if len(rez[f]["documente"]) > 15:
            print("   ... si inca %d" % (len(rez[f]["documente"]) - 15))
        print()


if __name__ == "__main__":
    main()
