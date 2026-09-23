---
title: Cum gestionez SAF-T pentru mai multe firme de contabilitate?
description: Semaforul de conformare fiscală arată dintr-o singură ecran starea D406 a întregului portofoliu, sortată automat astfel încât firmele cu restanțe apar primele.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum gestionez SAF-T pentru mai multe firme de contabilitate?

Pentru un cabinet cu mai multe firme-client, urmărirea manuală a obligației D406 (SAF-T) firmă cu firmă — fiecare cu propriul regim de TVA și propria periodicitate — devine repede greu de ținut sub control. Semaforul de conformare fiscală tratează exact acest caz: o vedere de portofoliu, cu fiecare firmă evaluată individual, dar afișată într-un singur ecran.

## Temeiul legal

::: ghid-temei
„Contribuabilii/Plătitorii transmit Declaraţia informativă D406 lunar sau trimestrial, urmând perioada fiscală aplicabilă pentru taxa pe valoarea adăugată (TVA). Contribuabilii care au ca perioadă fiscală aplicabilă pentru taxa pe valoarea adăugată semestrul sau anul transmit Declaraţia informativă D406 trimestrial."

*(OPANAF nr. 1783/2021, Anexa 4, pct. 2)*
:::

Pentru firmele neînregistrate în scopuri de TVA, regula e simplă: transmit D406 trimestrial (pct. 3 din aceeași anexă). Aceste două reguli, aplicate automat pe fiecare firmă din portofoliu, în funcție de propriul ei regim de TVA, stau la baza semaforului.

## Cum funcționează vederea de portofoliu

Ecranul de Control fiscal afișează lista tuturor firmelor din cabinet, fiecare cu o pastilă colorată (verde = la zi, galben = de urmărit, roșu = restanță, gri = nu se poate verifica, de regulă din lipsa unei informații din profilul firmei — de exemplu regimul de TVA necompletat). Lista e sortată automat: firmele cu restanțe apar primele, apoi cele de urmărit, apoi cele la zi. Un sumar din capul ecranului totalizează numărul de firme din fiecare categorie, pentru o privire de ansamblu rapidă asupra întregului portofoliu.

Pentru fiecare firmă, verdictul acoperă 9 declarații simultan (D100, D101, D112, D205, D300, D301, D390, D394, D406) — D406 e doar una dintre ele, evaluată cu propria regulă de periodicitate, dedusă din regimul de TVA al firmei respective.

## Ce se greșește în practică

- Se verifică D406 separat, firmă cu firmă, în loc de vederea unică de portofoliu, care le arată pe toate simultan, sortate după urgență.
- Se ignoră firmele marcate „gri" (nu se poate verifica) — starea gri nu înseamnă „la zi", ci „lipsește o informație din profilul firmei" (de exemplu regimul de TVA), care trebuie completată pentru ca semaforul să poată evalua D406 corect.

## Ce face iConta.eu

Motorul F022 (`core/control_fiscal_api.py`), accesibil prin `GET /control-fiscal`, evaluează întregul portofoliu al cabinetului dintr-o singură cerere, firmă cu firmă, și întoarce lista sortată cu pastilele de stare. Fiecare verdict poartă motivul explicit — inclusiv pentru D406, unde regula de periodicitate (lunar la plătitorii de TVA cu perioadă lunară, trimestrial pentru restul) e derivată automat din profilul fiscal al fiecărei firme.

[iConta.eu](/)
