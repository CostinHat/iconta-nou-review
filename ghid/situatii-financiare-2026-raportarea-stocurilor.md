---
title: "Situații financiare 2026: raportarea stocurilor"
description: "Principiile contabile care guvernează evaluarea și corectarea erorilor privind stocurile în situațiile financiare anuale, potrivit reglementărilor OMFP 1802/2014."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Situații financiare 2026: raportarea stocurilor

Raportarea corectă a stocurilor în situațiile financiare anuale nu se rezumă la o simplă listă de cantități și valori — reglementările contabile impun principii de evaluare și, atunci când apar erori, reguli precise despre cum se corectează, în funcție de momentul în care sunt descoperite.

## Temeiul legal

::: ghid-temei
„65. - (1) Erorile constatate în contabilitate se pot referi fie la exercițiul financiar curent, fie la exercițiile financiare precedente.
66. - (1) Erorile din perioadele anterioare sunt omisiuni și declarații eronate cuprinse în situațiile financiare ale entității pentru una sau mai multe perioade anterioare."
— OMFP nr. 1.802/2014 (Reglementări contabile), pct. 65-66 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Ce rezultă pentru raportarea stocurilor în situațiile financiare ale anului 2026:

- Evaluarea elementelor din situațiile financiare, deci și a stocurilor, se face potrivit principiilor generale — continuitatea activității, permanența metodelor, prudența și contabilitatea de angajamente (pct. 47-53 din aceleași reglementări).
- O eroare de stoc descoperită **înainte** de aprobarea situațiilor financiare ale anului la care se referă se corectează în acel exercițiu; o eroare descoperită **ulterior**, aferentă unor exerciții anterioare, se tratează distinct, ca eroare din perioade anterioare, potrivit pct. 65-66.
- Metoda de evaluare a ieșirilor din gestiune a stocurilor (FIFO, cost mediu ponderat etc.), o dată aleasă, trebuie aplicată consecvent de la un exercițiu la altul (principiul permanenței metodelor).

## Ce se greșește în practică

- Se corectează o eroare de stoc descoperită într-un an ulterior direct pe cheltuiala/venitul curent, ca și cum ar fi o operațiune a anului în curs, în loc să fie tratată ca eroare din perioade anterioare.
- Se schimbă metoda de evaluare a stocurilor de la un an la altul fără o justificare documentată, încălcând principiul permanenței metodelor.
- Se raportează stocurile la valoarea din ultima factură de achiziție, fără a verifica dacă evaluarea la data bilanțului respectă principiul prudenței (de exemplu, stocuri cu mișcare lentă sau deteriorate).

## Ce face iConta.eu

Verificat în cod: `core/d406_stocuri.py` calculează soldurile de deschidere și închidere ale stocurilor (cantitate și valoare) pe baza mișcărilor înregistrate, pentru raportarea SAF-T la cerere ANAF, iar `core/bilant.py` generează situațiile financiare anuale (F10/F20) din soldurile balanței; aplicația nu are, la acest moment, un modul separat de tratare a corectării erorilor de stoc din exerciții anterioare potrivit pct. 65-66 — o astfel de corecție rămâne o operațiune contabilă manuală, introdusă de contabil.

[iConta.eu](/)
