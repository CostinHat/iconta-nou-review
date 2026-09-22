---
title: Termenul de depunere a D301: cum se calculează?
description: D301 se depune până la data de 25 inclusiv a lunii următoare celei în care ia naștere exigibilitatea taxei, și numai pentru perioadele în care există efectiv o astfel de exigibilitate.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Termenul de depunere a D301: cum se calculează?

Termenul de depunere a decontului special D301 nu este legat de o periodicitate fixă lunară, ci de existența efectivă a unei operațiuni a cărei exigibilitate ia naștere în luna respectivă. Calculul corect al datei-limită pornește de la înțelegerea acestei reguli.

## Temeiul legal

::: ghid-temei
**Articolul 324 alin. (2)**: Decontul special de taxă trebuie întocmit potrivit modelului stabilit prin ordin al președintelui A.N.A.F. și se depune până la data de 25 inclusiv a lunii următoare celei în care ia naștere exigibilitatea operațiunilor menționate la alin. (1). Decontul special de taxă trebuie depus numai pentru perioadele în care ia naștere exigibilitatea taxei.

Instrucțiuni OPANAF 592/2016: Decontul special se depune numai pentru perioadele în care ia naștere exigibilitatea taxei. [...] a) până la data de 25 inclusiv a lunii următoare celei în care ia naștere exigibilitatea operațiunilor prevăzute la secțiunile 1, 3, 4 și 4.1 [...]

**Articolul 75 — Calcularea termenelor**: Termenele de orice fel privind exercitarea drepturilor și îndeplinirea obligațiilor prevăzute de Codul fiscal, de prezentul cod, precum și de alte dispoziții legale aplicabile în materie, dacă legislația fiscală nu dispune altfel, se calculează potrivit dispozițiilor Codului de procedură civilă, republicat.
:::

## Regula generală și cazul special al lunii fără operațiuni

Termenul-limită este data de **25 a lunii următoare** celei în care a luat naștere exigibilitatea taxei pentru operațiunile din secțiunile 1, 3, 4 și 4.1. Spre deosebire de alte declarații lunare, D301 **nu se depune "pe zero"** pentru lunile fără operațiuni — obligația de depunere există numai pentru perioadele în care a existat efectiv o exigibilitate a taxei.

Cât privește situația în care data de 25 cade într-o zi nelucrătoare (weekend sau sărbătoare legală), Codul de procedură fiscală (art. 75) trimite la regulile de calcul al termenelor din Codul de procedură civilă. Practica fiscală uzuală extinde, în general, un asemenea termen la următoarea zi lucrătoare — dar acest principiu trebuie tratat ca practică generală, nu ca un citat exact dintr-un articol de lege verificat, pentru că textul Codului de procedură civilă nu face parte din sursele legale confirmate pentru acest ghid.

## Ce se greșește în practică

- Se depune D301 în fiecare lună, inclusiv pentru perioadele fără nicio operațiune cu exigibilitate în acea lună, deși legea cere depunere doar când există efectiv o astfel de exigibilitate.
- Se calculează termenul de la data facturii sau a plății, în loc de la data la care ia naștere exigibilitatea taxei.
- Se presupune că termenul de 25 se extinde automat la ziua lucrătoare următoare fără verificare, deși regula exactă de extindere nu are un temei citabil direct în legislația fiscală specifică D301.
- Se confundă termenul de depunere a declarației cu termenul de emitere a autofacturii (a 15-a zi a lunii următoare faptului generator, conform art. 320), care este un termen diferit, anterior.

## Ce face iConta.eu

Aplicația construiește automat numărul de evidență a plății (câmpul C(23) din structura oficială D301), care include, între altele, perioada de raportare (LLAA) și scadența calculată (ZZLLAA) după formula ANAF: scadența este stabilită la data de 25 a lunii următoare perioadei de raportare, cu gestionarea corectă a trecerii dintr-un an calendaristic în altul (rollover) atunci când perioada e decembrie.

Aplicația refuză generarea declarației pe zero (adică fără nicio operațiune introdusă), cu excepția situației în care există facturi intracomunitare identificate automat, dar neintroduse manual în grilă, caz în care aplicația le semnalează explicit contabilului. Determinarea exactă a datei-limită în cazul în care 25 cade într-o zi nelucrătoare rămâne responsabilitatea contabilului, pe baza practicii fiscale uzuale.

[iConta.eu](/)
