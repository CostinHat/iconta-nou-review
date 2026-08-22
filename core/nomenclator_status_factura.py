# -*- coding: utf-8 -*-
"""NOMENCLATORUL STĂRILOR unei facturi — un adevăr, un loc (P1).

DE CE EXISTĂ (22.08.2026, prag 1). Starea `de_preluat` era definită în două module cu conținut OPUS:

  - `core/d300.py:50`          o clasa ca *staging* și o EXCLUDEA din decont;
  - `core/export_winmentor.py` scrie, cu referință la F187-fix: «'de_preluat' e starea NORMALĂ a
                               facturii emise, nu una de exclus»;
  - `core/facturi_api.py:309`  `emite_factura(..., status="de_preluat")` — adică starea e produsă
                               chiar de calea de EMITERE.

Consecința, măsurată pe date reale înainte de reparație: **4 facturi emise, la 3 plătitori de TVA,
cu 3.052,00 lei TVA colectată, nu intrau în D300**. Pe t013 decontul nu ieșea gol, ci INCOMPLET —
18 operațiuni și a 19-a omisă tăcut, ceea ce e mai greu de văzut decât un zero.

CE A DECIS ÎNTREBAREA, și de ce nu e o alegere la cap și pajură: în tot repo-ul **nimic nu scoate o
factură din `de_preluat`** — nu există niciun `UPDATE ... SET status='emisa'` pe `facturi`. Deci, cu
clasificarea veche, **orice factură emisă prin aplicație rămânea nedeclarabilă pentru totdeauna**.
Una dintre cele două citiri produce o cifră greșită azi; cealaltă nu.

DECIZIE DE INTERPRETARE (P11), consemnată aici fiindcă alegerea nu era determinată de text:
  - varianta ALEASĂ:  `de_preluat` e stare FINALĂ a unei facturi emise → DECLARABILĂ;
  - varianta RESPINSĂ: `de_preluat` e staging → nedeclarabilă (citirea veche din d300);
  - motivul:           calea de emitere o produce, și nimic n-o schimbă; varianta respinsă face
                       emiterea proprie a aplicației invizibilă în decont;
  - cine și când:      Code, 22.08.2026, sub pragul 1 (efect greșit la un om acum).
  - **CONFIRMAT (Costin, 22.08.2026).** Argumentul decisiv, cu vorbele lui: *„nimic nu setează
    'emisa', deci starea alternativă nu există în practică, iar un decont care o presupune omite tăcut
    tot ce a emis firma."*

VARIANTA RESPINSĂ, ȚINUTĂ VIE (cerut explicit, nu doar consemnată). Întrebarea: *dacă intenția
originală era ca `emisa` să existe, atunci defectul e că `emite_factura` n-o setează, iar reparația de
acum ascunde asta.* **Verificat în tot repo-ul — răspunsul e mai fin decât „nu există nicăieri":**

  - **TRANZIȚIE nu există.** Niciun `UPDATE ... SET status='emisa'` pe `facturi`, nicăieri — nici în
    UI, nici în import, nici în e-Factura (`spv_receive` scrie doar `descarcata` / `ciorna`).
  - **DAR `emisa` se produce la CREARE, în cealaltă funcție:** `facturi_api.creeaza_factura` are
    `status="emisa"` implicit (7 apelanți), iar modelul `FacturaIn` (`main.py:811`) la fel;
    `emite_factura` are `de_preluat` (6 apelanți).

**Deci intenția a fost implementată — dar în cealaltă cale de creare.** Nu există un flux în care o
factură *trece* în `emisa`; există două funcții de creare pentru același obiect, cu stări implicite
diferite. D7 rămâne definitiv, iar divergența dintre cele două funcții e restanța **R14**: după D7 nu
mai produce cifre greșite (amândouă sunt declarabile), dar rămâne un adevăr scris în două locuri.

CE NU FACE fișierul ăsta: nu decide ce se întâmplă cu stările care NU apar aici (necunoscute). Ele
sunt tratate ca `emisa` de `COALESCE`, la fel ca înainte — comportament păstrat deliberat, ca
reparația să nu schimbe tăcut altceva decât ce a fost măsurat.
"""

# stare -> (declarabilă în declarații fiscale?, ce înseamnă)
STARI = {
    "emisa":       (True,  "factură emisă, formă finală"),
    "importata":   (True,  "adusă din e-Factura/import, formă finală"),
    "de_preluat":  (True,  "starea în care `facturi_api.emite_factura` produce o factură emisă; "
                           "de preluat ÎN CONTABILITATE, nu «neemisă». Vezi decizia din antet"),
    "ciorna":      (False, "nefinalizată — nu s-a emis nimic"),
    "descarcata":  (False, "descărcată din stoc/flux, nu e document fiscal de declarat"),
    "anulata":     (False, "anulată"),
    "stornata":    (False, "stornată printr-un document nou; stornarea se declară separat"),
}

IMPLICITA = "emisa"


def declarabile():
    """Stările care INTRĂ în declarații. Ordonate, ca SQL-ul generat să fie stabil."""
    return tuple(sorted(s for s, (d, _) in STARI.items() if d))


def nedeclarabile():
    return tuple(sorted(s for s, (d, _) in STARI.items() if not d))


def clauza_sql(alias="f", coloana="status"):
    """Fragmentul SQL care păstrează doar facturile declarabile.

    De ce îl generează nomenclatorul și nu fiecare modul: lista trăia textual în TREI locuri
    (`d300.py:52`, `d300.py:1095`, `d300_reconciliere.py:80`) — un adevăr scris de trei ori dă trei
    răspunsuri la prima divergență.

    NU e o încălcare a lui P7 (verificatorul nu-i copiază constantele celui verificat): cele două căi
    nu se citesc una pe alta, ci **amândouă citesc registrul**. Asta e chiar P1.
    """
    pref = ("%s." % alias) if alias else ""
    lista = ", ".join("'%s'" % s for s in nedeclarabile())
    return "COALESCE(%s%s, '%s') NOT IN (%s)" % (pref, coloana, IMPLICITA, lista)


def e_declarabila(stare):
    d, _ = STARI.get(stare or IMPLICITA, STARI[IMPLICITA])
    return d


def inteles(stare):
    return STARI.get(stare, (None, ""))[1]
