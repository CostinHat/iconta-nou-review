---
title: Greșeala de a nu corela D300 cu balanța
description: Depunerea D300 direct din generarea automată, fără o comparație cu balanța pe conturile de TVA, e cea mai frecventă cale prin care o diferență reală trece neobservată până la un control.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Greșeala de a nu corela D300 cu balanța

Cea mai frecventă greșeală la depunerea TVA nu e o eroare de calcul, ci lipsa unei comparații: D300 se generează și se depune direct, fără să fie verificată față de rulajele contabile ale conturilor de TVA. Cele două surse — declarația și contabilitatea — pot diverge legitim (fapt generator vs. înregistrare), dar și din erori reale, iar fără comparație nu poți deosebi între ele.

## Temeiul legal

::: ghid-temei
Art. 281 din Codul fiscal (Legea 227/2015) — "Faptul generator pentru livrări de bunuri și prestări de servicii" — stabilește momentul de la care se naște obligația de TVA. D300 se calculează pe facturile lunii (fapt generator); balanța pe înregistrările contabile efectiv făcute. Diferența dintre cele două nu e automat eroare — dar nici nu poate fi ignorată fără verificare. Titlul și numărul articolului sunt confirmate în sursele legale folosite de aplicație; textul integral nu e citat literal aici.
:::

## De ce contează comparația

Verificarea acoperă cinci conturi (4427, 4426, 4423, 4424 și, informativ, 4428), fiecare cu o stare verde/roșu/gri și o toleranță de 1 leu. Fără ea:

- o factură fără notă validată rămâne nedetectată până la un eventual control;
- un storno neînregistrat la furnizor sau client poate distorsiona soldul de TVA fără să fie observat;
- o factură înregistrată în altă lună decât data ei poate produce o diferență care, necorelată, arată ca o eroare mai mare decât e în realitate.

## Ce se greșește în practică

- Se depune D300 imediat după generare, fără verificare separată față de balanță — mai ales sub presiunea termenului de depunere.
- Se presupune că, dacă aplicația a generat declarația automat, ea corespunde deja cu contabilitatea — generarea și verificarea sunt două lucruri diferite.
- Se ignoră starea gri (nu s-a putut verifica), tratând-o ca pe un verde tacit — gri înseamnă lipsă de informație, nu confirmare.

## Ce face iConta.eu

Aplicația compară automat, lunar, D300 cu rulajele celor cinci conturi de TVA, pe bază de note validate, și afișează pentru fiecare o stare distinctă (verde, roșu sau gri), cu o toleranță de 1 leu. Verificarea nu înlocuiește generarea declarației, ci rulează separat, tocmai pentru a prinde diferențele înainte de depunere, nu după.

[iConta.eu](/)
