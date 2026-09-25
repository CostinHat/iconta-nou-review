---
title: "Cum verific SAF-T cu registrul mijloacelor fixe?"
description: "De ce secțiunea Active a D406 (SAF-T) nu e o verificare independentă a registrului de mijloace fixe, ci se generează direct din el — și ce înseamnă asta pentru un registru importat prin migrare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific SAF-T cu registrul mijloacelor fixe?

Mulți contabili se așteaptă ca declarația D406 (SAF-T), secțiunea Active, să funcționeze ca un control încrucișat — o comparație între ce spune SAF-T-ul și ce arată registrul propriu de mijloace fixe. În realitate, cele două nu sunt surse independente: SAF-T-ul se generează *din* registru, nu se compară *cu* registrul. „Verificarea" corectă înseamnă, de fapt, verificarea completitudinii registrului însuși, înainte de a-l lăsa să alimenteze declarația — subiect deosebit de relevant când registrul a fost adus prin import (migrare de la alt program).

## Temeiul legal

::: ghid-temei
„7. Informaţiile privind «Activele» din cadrul Declaraţiei informative D406 sunt întocmite la nivelul anului financiar aplicat de către contribuabili şi transmise printr-o singură depunere, respectiv o singură raportare a Declaraţiei informative D406, până la data depunerii situaţiilor financiare aferente exerciţiului financiar la care se referă.
8. Declaraţia informativă D406 pentru «Active» se poate transmite ca o declaraţie independentă, nefiind necesară introducerea tuturor secţiunilor/subsecţiunilor dintr-o Declaraţie informativă D406, ci doar a zonelor indicate ca fiind obligatorii pentru transmiterea acestui tip de informaţie."
— OPANAF 1783/2021, Anexa (Instrucțiuni de completare D406), pct. 7-8 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

- Secțiunea Active a D406 se depune o singură dată, la nivelul anului financiar, cel târziu odată cu situațiile financiare anuale — nu lunar, ca restul declarației.
- Conținutul ei (cost de achiziție, durată, adăugiri/cedări, valoare rămasă, metodă și procent de amortizare) trebuie să reflecte exact ce arată registrul de mijloace fixe al firmei la acel moment.
- Nu există, în text, o procedură separată de „reconciliere" a SAF-T-ului cu evidența — coerența se asigură prin faptul că amândouă provin din același registru.

## Ce se greșește în practică

- Se așteaptă ca aplicația să semnaleze o „diferență" între SAF-T și registru, ca la controlul TVA/D300 — un asemenea control n-are sens aici, pentru că nu există două surse independente de comparat, ci una singură din care se generează cealaltă.
- La migrarea registrului de la alt program, se importă doar valorile numerice (cost, valoare rămasă, durată), fără câmpurile care condiționează raportarea corectă în SAF-T — de exemplu contul de imobilizare pe categorie, necesar ca să se poată aplica metodele de amortizare accelerată/superaccelerată.
- Se presupune că un prag valoric vechi (de ex. 2.500 lei, valabil până la 24.02.2026) mai poate fi aplicat unui bun migrat cu dată de intrare recentă, când pragul corect se citește la data efectivă de punere în funcțiune a bunului.

## Ce face iConta.eu

Verificat direct în cod: secțiunea Active a SAF-T (`core/d406_active.py`, funcționalitatea „D406 Active") se generează direct din tabela `mijloace_fixe` — motorul de amortizare unic (liniar/degresiv/accelerat/superaccelerat, conform art. 28 Cod fiscal) e consumat atât de ecranul de mijloace fixe, cât și de generatorul SAF-T. Nu există un al doilea flux independent cu care rezultatul să fie comparat în aplicație; endpoint-ul e disponibil (`GET /tenants/{tenant_id}/d406-active`), dar **fără ecran dedicat în UI** la acest moment.

Aici intervine legătura reală cu importul de mijloace fixe la migrare (`core/mijloace_fixe_import_api.py`): la import, aplicația verifică explicit fiecare rând — cod de inventar, durată, valoare — și avertizează dacă lipsește **contul de imobilizare** pe categorie, cu mesajul din cod: „Mijloacele fixe intră în amortizare și în D406 SAF-T", pentru că fără acest cont metodele accelerat/superaccelerat sunt respinse ulterior la generarea declarației. Practic, „verificarea SAF-T cu registrul" pentru un registru migrat înseamnă rezolvarea din start a avertismentelor de import — un registru incomplet la migrare rămâne incomplet și în secțiunea Active a SAF-T, pentru că sunt aceleași date.

[iConta.eu](/)
