---
title: "Amortizarea activelor prin PNRR: regim fiscal"
description: Un activ cumpărat din fonduri PNRR nu are un regim fiscal separat — se tratează contabil și fiscal ca orice altă subvenție pentru investiții, cu reluare la venituri pe măsura amortizării.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Amortizarea activelor prin PNRR: regim fiscal

Fondurile PNRR primite pentru achiziția unui activ nu au un regim fiscal distinct în sursele verificate pentru acest ghid — se încadrează la categoria generală „subvenții pentru investiții" (inclusiv fonduri europene pentru active), cu același mecanism de recunoaștere ca orice altă subvenție de acest tip.

## Temeiul legal

::: ghid-temei
„Subvențiile aferente activelor reprezintă subvenții pentru acordarea cărora principala condiție este ca entitatea beneficiară să cumpere, să construiască sau să achiziționeze active imobilizate."
— OMFP 1802/2014, pct. 394 alin. (1)
:::

::: ghid-temei
„Subvențiile legate de activele amortizabile sunt recunoscute, de regulă, în contul de profit și pierdere pe parcursul perioadelor și în proporția în care amortizarea acelor active este recunoscută."
— OMFP 1802/2014, pct. 399 alin. (1)
:::

Mecanismul e identic celui pentru orice subvenție de investiții: dreptul de a primi finanțarea se înregistrează `445 = 4751`, încasarea `5121 = 445`, iar reluarea la venituri se face treptat, `4751 = 7584`, proporțional cu amortizarea lunară a activului cumpărat din fonduri PNRR. Activul propriu-zis se amortizează normal, la valoarea lui de intrare — subvenția nu reduce baza de amortizare, ci generează în paralel un venit reluat pe aceeași durată.

Fiscal, la impozitul pe veniturile microîntreprinderilor, venitul din reluare (7584) se scade din baza impozabilă (art. 53 alin. (1) lit. d) din Codul fiscal); la impozitul pe profit, nu există o scutire similară — venitul e impozabil.

**Notă**: nu am identificat, în sursele verificate pentru acest ghid, vreo normă specifică pentru fondurile PNRR care să deroge de la regimul general de mai sus. Dacă finanțarea ta prin PNRR vine cu obligații contractuale suplimentare (rambursare condiționată, raportare separată etc.), acestea trebuie verificate direct în contractul de finanțare, nu presupuse din regulile contabile generale.

## Ce se greșește în practică

- Se caută un regim fiscal „special PNRR" care nu există în reglementările contabile/fiscale generale — tratamentul e cel comun tuturor subvențiilor pentru investiții.
- Se reduce valoarea de amortizare a activului cu suma subvenției, în loc să se amortizeze activul integral și să se recunoască separat venitul din reluare.
- Se recunoaște toată subvenția ca venit la primirea banilor, nu treptat, pe durata amortizării.

## Ce face iConta.eu

Ecranul „Subvenții (445/741)" nu face distincție după sursa fondurilor (PNRR, alt program european, buget național) — tratează orice subvenție pentru investiții cu același mecanism: `445=4751` la drept, `5121=445` la încasare. Reluarea lunară (`4751=7584`, proporțională cu amortizarea) e calculată corect de motor (`reluare_lunara_investitii`), dar **formularul standard „Subvenții" nu are, la data acestei verificări, câmpurile necesare** (`valoare_activ`, `subventie`, `amortizare_lunara`) pentru operația „Reluare la venituri" — deși apare ca opțiune în listă, nu poate fi finalizată din ecran; reluarea trebuie introdusă manual, prin altă cale. Activul finanțat se înregistrează și se amortizează separat, prin operațiunile obișnuite de mijloace fixe. Aplicația nu ține evidența contractuală a condițiilor specifice de finanțare PNRR (rapoarte de progres, eligibilitate cheltuieli) — aceasta rămâne responsabilitatea ta, în afara evidenței contabile.

[iConta.eu](/)
