---
title: Ce diferențe între D112 și contabilitate pot atrage un control?
description: Diferențele care depășesc toleranța de rotunjire (0,5 lei per salariat) pe oricare din conturile 444, 4315, 4316 sau 436 sunt semnale reale, nu întâmplătoare — și cele mai riscante sunt statele de plată nedeclarate contabil.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce diferențe între D112 și contabilitate pot atrage un control?

Nu orice diferență între D112 și contabilitate e un risc — o mică diferență de rotunjire e normală. Dar dincolo de acel prag, orice divergență reflectă o discrepanță pe care un control ANAF ar putea-o observa la fel de ușor ca verificarea automată din iConta.eu.

## Temeiul legal

::: ghid-temei
„Articolul 147 — Depunerea Declarației privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate. (1) Persoanele fizice și juridice care au calitatea de angajatori sau sunt asimilate acestora [...] sunt obligate să depună lunar, până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc veniturile, Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate." — Codul fiscal (Legea 227/2015), art. 147
:::

Verificarea urmărește patru perechi cod D112 → cont contabil: impozit (602 → 444, 10%, art. 64 alin. 1), CAS (412+458 → 4315, 25%, art. 138 lit. a), CASS (432+459 → 4316, 10%, art. 156) și CAM (480 → 436, 2,25%, art. 220^3 alin. 1). Orice divergență pe unul din aceste patru conturi, peste toleranța de rotunjire, e diferența pe care s-ar putea baza un control.

## Ce se greșește în practică

Greșeala tipică este să se trateze o divergență semnalată ca fiind „doar un detaliu tehnic" fără urmări, deși exact acest tip de diferență este ce ar verifica și un inspector: suma declarată la stat comparată cu ce arată efectiv contabilitatea firmei. A doua greșeală este ignorarea diferenței dintre XML-ul efectiv depus la ANAF și o simplă regenerare calculată acum — dacă cele două nu coincid, riscul real e legat de ce s-a depus, nu de ce calculează acum aplicația.

## Ce face iConta.eu

`verifica_d112` (`core/control_incrucisat.py`) semnalează cu roșu orice diferență care depășește toleranța de rotunjire (0,5 lei per salariat, minim 1 leu) pe oricare din cele patru conturi, și indică cea mai probabilă cauză:

- **Cel mai riscant caz**: contul e la zero, D112 declară o sumă, și nu există nicio notă (nici în ciornă) — statul de plată pur și simplu nu a fost contabilizat, deși a fost declarat la ANAF. Acesta e tipul de diferență cu cel mai mare potențial de a atrage atenția la un control, pentru că arată o sumă declarată fără corespondent în evidența contabilă.
- Contul e la zero, dar există o notă de salarii în ciornă (nevalidată) — situație mai puțin gravă, dar tot vizibilă: obligația e cunoscută, doar neînregistrată definitiv.
- Orice altă divergență (de exemplu sold existent, dar diferit de declarat) — cauza nu poate fi dedusă automat; posibile explicații includ salariați modificați ulterior contabilizării, note manuale directe pe cont, corecții de lună anterioară sau concedii medicale cu bază de calcul diferită (OUG 158/2005).

Aplicația marchează gri, nu roșu, situația în care D112 nu s-a putut genera (eroare tehnică sau date incomplete), cu cauza explicată — pentru că un verdict fals ar fi mai riscant decât recunoașterea că nu se poate verifica. Dacă luna pur și simplu nu a avut salariați, D112 nu se datorează, iar aplicația nu produce niciun verdict pe acel cont în luna respectivă — nici verde, nici roșu, nici gri — ca să nu sugereze o verificare făcută pe un subiect inexistent.

[iConta.eu](/)
