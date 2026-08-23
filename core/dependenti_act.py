# -*- coding: utf-8 -*-
"""core/dependenti_act.py — INTERDICȚIA 61: lista dependenților unui articol, generabilă la cerere.

*„Ce se atinge când se schimbă articolul X?"* — întrebarea pe care o pui când apare o modificare
legislativă, și la care până azi se răspundea căutând.

DE CE ACUM. Planul spunea că 61 „se măsoară trivial azi: zero — legătura inversă nu există deloc".
**Nu mai e adevărat**, și tocmai de aceea se construiește: reparația lui `graf_temei` din 23.08 (R17)
a făcut ca `depinde_de(cotă)` să vadă 83 de consumatori ai salariului minim în loc de 12, iar
compunerea `articol → cote care-l citează → funcții care depind de ele` devine **fiabilă**. Pe graful
conflat, unealta asta ar fi dat răspunsuri scurte cu încredere — mai rău decât să lipsească.

ȘI ÎNCHIDE O TRIMITERE LA CEVA INEXISTENT. `TESTE.md` §282–287 descrie de mult `clustere_indirect(act)`
la forma prezentului, ca și cum ar fi o interogare disponibilă. Nu era implementată nicăieri —
semnalat 23.08 ca regula D. Asta e implementarea ei, la nivel de FUNCȚII (nu de clustere).

CE POATE, MĂSURAT: pe registrul de cote sunt **17 articole distincte**; lista dependenților se poate
genera pentru **16** din ele (al 17-lea citează o cotă pe care nicio funcție n-o atinge prin `cota()`).

CE NU POATE, declarat, fiindcă e chiar diferența dintre o unealtă și o promisiune:
  - vede doar articolele care apar într-un `Temei` **din registrul de cote**. Un articol citat în cod
    prin `Temei` fără `url` (16 din 53) sau doar în proză NU e aici.
  - vede dependența doar prin `cota()` — un literal scris de mână ocolește graful, limită moștenită
    de la `graf_temei` și declarată acolo.
  - lista e a **funcțiilor**, nu a fișierelor de test sau a ecranelor. „Ce se atinge" înseamnă „ce cod
    calculează altfel", nu „ce trebuie retestat".
"""
import collections


def _cheie_articol(t):
    return (getattr(t, "tip", None), getattr(t, "nr", None), getattr(t, "an", None),
            getattr(t, "art", None))


def harta_articol_cote():
    """{(tip, nr, an, art): {chei COTE care îl citează}}"""
    from core import common as c
    out = collections.defaultdict(set)
    for cheie, intrari in c.COTE.items():
        for it in intrari:
            if not isinstance(it, (list, tuple)) or len(it) < 3:
                continue
            t = it[2]
            if getattr(t, "art", None):
                out[_cheie_articol(t)].add(cheie)
    return dict(out)


def dependenti(tip=None, nr=None, an=None, art=None, radacina=None):
    """Ce se atinge dacă se schimbă articolul: {cote, functii, fisiere}.

    Potrivirea e pe câmpurile date: `dependenti(art="291")` prinde toate actele care modifică art.291;
    `dependenti(tip="Legea", nr=141, an=2025)` prinde tot ce citează acel act. Un apel fără niciun
    câmp ar potrivi tot — și **ridică**, fiindcă „toate" nu e un răspuns la „ce se atinge"."""
    if not any(x is not None for x in (tip, nr, an, art)):
        raise ValueError("dependenti() fără niciun câmp ar întoarce tot codebase-ul; dă cel puțin "
                         "articolul sau actul")
    from core import graf_temei as gt
    graf = gt.construieste_graf(radacina)
    cote, functii = set(), set()
    for (k_tip, k_nr, k_an, k_art), chei in harta_articol_cote().items():
        if tip is not None and str(k_tip) != str(tip):
            continue
        if nr is not None and str(k_nr) != str(nr):
            continue
        if an is not None and str(k_an) != str(an):
            continue
        if art is not None and str(k_art) != str(art):
            continue
        cote |= chei
    for k in cote:
        functii |= set(gt.depinde_de(k, radacina))
    fisiere = {graf[f]["fisier"] for f in functii if f in graf}
    return {"cote": sorted(cote), "functii": sorted(functii), "fisiere": sorted(fisiere)}


def acoperire():
    """(articole din registru, câte au lista generabilă) — cifra interdicției 61."""
    h = harta_articol_cote()
    gen = 0
    for art in h:
        if dependenti(*art)["functii"]:
            gen += 1
    return len(h), gen


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        d = dependenti(art=sys.argv[1])
        print("articol %s -> %d cote, %d functii, %d fisiere"
              % (sys.argv[1], len(d["cote"]), len(d["functii"]), len(d["fisiere"])))
        print("   cote   : %s" % ", ".join(d["cote"]))
        print("   fisiere: %s" % ", ".join(d["fisiere"]))
    else:
        tot, gen = acoperire()
        print("INTERDICTIA 61 — articole din registru: %d · cu lista dependentilor generabila: %d"
              % (tot, gen))
