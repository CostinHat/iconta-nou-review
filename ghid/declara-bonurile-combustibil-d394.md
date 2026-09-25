---
title: "Cum se declară bonurile de combustibil în D394?"
description: "Când un bon fiscal de combustibil intră în D394 ca achiziție cu factură simplificată și ce condiție trebuie să îndeplinească pentru asta."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se declară bonurile de combustibil în D394?

Bonul fiscal de la stație nu e, prin el însuși, o factură — dar Anexa 2 a formularului 394 îl tratează ca atare într-o situație precisă, iar acea situație e chiar cea a cheltuielilor curente cu carburantul.

## Temeiul legal

::: ghid-temei
„1.5. valoarea totală a bazei impozabile aferentă achiziţiilor de bunuri şi servicii pentru care s-au primit bonuri fiscale care îndeplinesc condiţiile unei facturi simplificate şi care au înscris codul de înregistrare în scopuri de TVA al beneficiarului, defalcată pe cote de TVA (24%, 21%, 20%, 19%, 11%, 9%, 5%)."
— OPANAF 2194/2025, Anexa 2, instrucțiuni de completare pct.I.1.5 (sursă: anaf_surse/opanaf_2194_2025_d394.txt:1022-1024)
:::

Condiția care decide dacă un bon de combustibil intră sau nu în D394 e explicită în text:

- Bonul trebuie să îndeplinească **condițiile unei facturi simplificate** (de regulă, o valoare sub plafonul legal pentru facturare simplificată).
- Bonul trebuie să aibă **înscris codul de înregistrare în scopuri de TVA al firmei cumpărătoare** — fără CUI-ul firmei pe bon, documentul nu e o factură simplificată din perspectiva TVA și nu intră în această categorie de raportare.
- Suma se defalcă pe cotă de TVA, exact ca orice altă achiziție taxabilă.

Practic: bonul de combustibil de la pompă, cerut cu CUI-ul firmei la momentul plății, e echivalat unei facturi simplificate și tratat ca achiziție care se declară în D394. Bonul fără CUI-ul cumpărătorului nu intră în această categorie a formularului.

## Ce se greșește în practică

- Se presupune că bonurile fiscale sunt automat excluse din D394 pentru că „nu sunt facturi" — legea le echivalează explicit unei facturi simplificate, cu condiția să aibă CUI-ul cumpărătorului înscris pe ele.
- Se cere bonul de combustibil fără CUI la pompă, din grabă, și apoi se încearcă declararea lui ca și cum ar fi avut CUI — documentul fără codul de înregistrare al beneficiarului nu îndeplinește condiția din Anexa 2.
- Se amestecă bonurile de combustibil cu bonurile fiscale obișnuite (fără TVA defalcat pe cote sau fără să îndeplinească structura unei facturi simplificate), care nu au același regim.

## Ce face iConta.eu

D394 se generează în iConta.eu din aceleași tabele de facturi (`facturi` + `factura_linii`) folosite pentru restul aplicației, cu o a doua cale de calcul independentă (`core/d394_reconciliere.py`) care recalculează totalurile pe cotă direct din liniile brute și oprește generarea dacă rezultatul diferă de cel al generatorului principal.

Această a doua cale de calcul are o limită declarată explicit în codul sursă: **nu acoperă operațiunile manuale — bonurile fiscale și borderourile, care nu au un ecran/tabelă dedicată de introducere, ci pot fi transmise doar prin câmpul „manual" al cererii de generare (rânduri TVA introduse de contabil), fără o interfață proprie în aplicație.** Practic, un bon de combustibil cu CUI-ul firmei poate ajunge în D394 fie introdus ca o achiziție obișnuită, prin fluxul normal de facturi — caz acoperit de garda de reconciliere independentă —, fie ca rând manual transmis prin acel câmp „manual" — caz pe care garda de reconciliere NU îl verifică. Rămâne responsabilitatea contabilului să se asigure că bonul respectă condiția CUI-ului înscris înainte de a-l introduce în sistem, indiferent de calea aleasă.

[iConta.eu](/)
