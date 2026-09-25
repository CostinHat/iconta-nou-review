---
title: "Când trebuie un PFA nou să se înregistreze în scopuri de TVA?"
description: "Plafonul actual de scutire de TVA pentru întreprinderile mici și momentul în care apare obligația de înregistrare, conform Codului fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Când trebuie un PFA nou să se înregistreze în scopuri de TVA?

Un PFA nou-înființat nu e obligat să se înregistreze în scopuri de TVA din prima zi — poate aplica regimul special de scutire pentru întreprinderile mici, atâta timp cât cifra de afaceri rămâne sub plafonul legal. Problema apare când plafonul e depășit în cursul anului, moment în care termenul de înregistrare a devenit, printr-o modificare recentă, mai strict decât înainte.

## Temeiul legal

```
::: ghid-temei
„(1) Persoana impozabilă stabilită în România conform art. 266 alin. (2) lit. a), a cărei cifră de afaceri anuală, declarată sau realizată, nu depășește plafonul de 395.000 lei, poate aplica scutirea de taxă, denumită în continuare regim special de scutire, pentru operațiunile prevăzute la art. 268 alin. (1) [...]
(6) Persoana impozabilă care aplică regimul special de scutire și a cărei cifră de afaceri [...] depășește plafonul de scutire prevăzut la alin. (1) trebuie să solicite înregistrarea în scopuri de TVA, conform art. 316, cel târziu la data depășirii plafonului. Regimul normal de taxare se aplică din data depășirii plafonului prevăzut la alin. (1), începând cu tranzacția care conduce la depășirea plafonului."
— Legea nr. 227/2015 privind Codul fiscal, art. 310 alin. (1) și (6) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::
```

Ce înseamnă asta, pas cu pas, pentru un PFA nou:

- **Plafonul actual de scutire este de 395.000 lei** cifră de afaceri anuală — sub acest nivel, PFA-ul poate opta pentru regimul special de scutire, fără TVA colectată, dar și fără drept de deducere a TVA la achiziții.
- **Pentru un PFA nou-înființat, care începe activitatea în cursul anului**, plafonul de scutire aplicabil e integral cel de 395.000 lei — nu se proratează în funcție de câte luni a funcționat efectiv în anul respectiv (art. 310 alin. (5)).
- **Momentul obligației de înregistrare s-a schimbat:** înregistrarea trebuie solicitată **cel târziu la data depășirii plafonului**, nu la un termen ulterior calculat pe zile — regimul normal de taxare se aplică chiar din tranzacția care a dus la depășire.
- Cifra de afaceri relevantă pentru verificarea plafonului include livrările de bunuri și prestările de servicii taxabile, operațiunile scutite cu drept de deducere, dar exclude livrările de active fixe corporale și cesiunea de active necorporale (art. 310 alin. (2)).

## Ce se greșește în practică

- Se presupune că înregistrarea se face „până la data de 10 a lunii următoare" celei în care a fost depășit plafonul — aceasta era regula anterioară datei de 1 septembrie 2025; regula actuală cere solicitarea înregistrării chiar la data depășirii.
- Se calculează plafonul pentru un PFA nou-înființat proporțional cu numărul de luni de activitate din anul respectiv — plafonul e cel integral, nu unul proratat.
- Se include în cifra de afaceri relevantă valoarea vânzării unui mijloc fix propriu, deși legea o exclude expres din baza de calcul a plafonului.

## Ce face iConta.eu

Verificarea plafonului de TVA, pe baza operațiunilor înregistrate în aplicație, ține de logica generală a evidenței facturilor emise; nu a fost găsit în `core/` un modul dedicat exclusiv „urmăririi plafonului de scutire TVA cu alertă la depășire" pentru PFA — contabilul rămâne cel care monitorizează cifra de afaceri cumulată și declanșează, la momentul potrivit, cererea de înregistrare în scopuri de TVA conform art. 316 din Codul fiscal.

[iConta.eu](/)
