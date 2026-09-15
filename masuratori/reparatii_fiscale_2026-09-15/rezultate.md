# Reparațiile fiscale din 15.09.2026 — ce s-a măsurat pe portofoliu

Măsurat **înainte** de a schimba codul, pe baza de producție (`iconta_v2`, 37 de firme active), în
citire pură. Instrumentele stau alături, ca cifra să se poată reface.

## (a) Proforma iese din D300 — DECIZII 46/49

```
documente in portofoliu: 47
   factura    emisa              29
   factura    importata          10
   factura    de_preluat          6
   factura    primita             2
proforme / avize: 0
FIRME ATINSE: 0 din 37
TOTAL documente scoase din D300: 0
TOTAL baza care nu se mai declara: 0.00 lei
TOTAL TVA care nu se mai declara:  0.00 lei
```

Defectul era real în cod, dar **neexercitat în producție**: nicio declarație existentă nu se rescrie.
*Dacă portofoliul ar fi avut proforme, reparația ar fi schimbat cifre deja depuse — și ar fi cerut
alt plan. De-aia cifra se măsoară, nu se presupune.*

## (b) Partenerul D394 se citește de pe factură — DECIZII 47/49

```
facturi emise (tip=factura): 28
cu tert_cui DIFERIT de fisa (se schimba D394): 0
fara tert_cui, cu fisa completata (raman pe fisa, ca rezerva): 0
```

## Cum se refac cifrele

```
set -a; . ~/.iconta/db.env; set +a
ICONTA_MEDIU=productie ./venv/bin/python masuratori/reparatii_fiscale_2026-09-15/masoara_tipuri_documente.py
ICONTA_MEDIU=productie ./venv/bin/python masuratori/reparatii_fiscale_2026-09-15/masoara_proforme_in_d300.py
ICONTA_MEDIU=productie ./venv/bin/python masuratori/reparatii_fiscale_2026-09-15/masoara_divergenta_partener.py
```
