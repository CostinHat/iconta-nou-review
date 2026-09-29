---
title: "Cine emite factura cu TVA la vânzarea bunurilor unei firme prin executare silită?"
description: "Factura o emite organul de executare silită, pe numele și în contul debitorului, cu mențiunea că facturarea e făcută de el; TVA încasată se virează în 5 zile lucrătoare de la adjudecare."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Cine emite factura cu TVA la vânzarea bunurilor unei firme prin executare silită?

Factura nu o emite firma executată și nici cumpărătorul, ci **organul de executare silită**. El o întocmește pe numele și în contul debitorului, cu mențiunea că facturarea e realizată de organul de executare. TVA apare pe factură numai dacă operațiunea e taxabilă și debitorul e înregistrat în scopuri de TVA. Același regim se aplică și debitorului căruia i s-a anulat înregistrarea în anumite cazuri prevăzute de lege.

Pentru contabilul debitorului urmează partea practică: livrarea e a firmei, deci intră în jurnalul ei de vânzări și în decontul ei. Taxa virată de organul de executare se scade apoi la rândul de regularizări al taxei colectate, pe baza documentului de plată.

## Temeiul legal

::: ghid-temei
„În sensul art. 319 alin. (19) din Codul fiscal, în cazul bunurilor supuse executării silite care sunt livrate prin organele de executare silită, factura se întocmește de către organele de executare silită pe numele și în contul debitorului executat silit. În factură se face o mențiune cu privire la faptul că facturarea este realizată de organul de executare silită. Originalul facturii se transmite cumpărătorului, respectiv adjudecatarului, iar exemplarul al doilea se transmite debitorului executat silit. […] Organele de executare silită emit facturi cu TVA numai în cazul operațiunilor taxabile și numai dacă debitorul este înregistrat în scopuri de TVA conform art. 316 din Codul fiscal sau a fost înregistrat în scopuri de TVA și i s-a anulat înregistrarea conform art. 316 alin. (11) lit. a)-e) și h) din Codul fiscal. Nu se menționează TVA pe factură în cazul operațiunilor pentru care se aplică taxare inversă conform prevederilor art. 331 din Codul fiscal."
— HG 1/2016 (Normele Codului fiscal), Titlul VII, pct. 96 alin. (5) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

::: ghid-temei
„Dacă organul de executare silită, menționat la alin. (5) , încasează contravaloarea bunurilor, inclusiv taxa de la cumpărător sau de la adjudecatar, are obligația să vireze la bugetul de stat taxa încasată de la cumpărător ori adjudecatar în termen de 5 zile lucrătoare de la data adjudecării. Pe baza documentului de plată a taxei pe valoarea adăugată transmis de organele de executare silită, debitorul executat silit evidențiază suma achitată, cu semnul minus, la rândul de regularizări taxa colectată din decontul de taxă prevăzut la art. 323 din Codul fiscal."
— HG 1/2016 (Normele Codului fiscal), Titlul VII, pct. 96 alin. (6) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

Pe scurt:

- **Emitentul**: organul de executare silită.
- **Titularul facturii**: debitorul executat, pe numele și în contul căruia se emite.
- **Exemplarele**: originalul merge la cumpărător sau adjudecatar, al doilea exemplar la debitor.
- **TVA pe factură**: doar pentru operațiuni taxabile și doar dacă debitorul e înregistrat în scopuri de TVA, sau i s-a anulat înregistrarea în cazurile de la art. 316 alin. (11) lit. a)-e) și h) CF. La taxarea inversă de la art. 331 CF nu se menționează TVA.
- **Virarea taxei**: dacă o încasează, organul de executare virează TVA la bugetul de stat în 5 zile lucrătoare de la adjudecare.
- **Debitorul**: pe baza documentului de plată, trece suma cu minus la regularizări ale taxei colectate, ca să nu plătească de două ori.

::: ghid-exemplu
Bunurile SC Exemplu SRL, plătitoare de TVA, se adjudecă pentru 100.000 lei plus TVA 21% (21.000 lei), iar operațiunea nu intră la taxare inversă. Organul de executare emite factura pe numele SC Exemplu SRL, încasează 121.000 lei și virează 21.000 lei la bugetul de stat în 5 zile lucrătoare. SC Exemplu SRL înregistrează factura în jurnalul de vânzări, cu TVA colectată de 21.000 lei. Pe baza documentului de plată primit, trece în decont -21.000 lei la regularizări ale taxei colectate. Taxa rămasă de plată pentru această livrare este zero.
:::

## Ce se greșește în practică

- Debitorul emite și el o factură pentru aceeași livrare, iar operațiunea ajunge dublată în evidență.
- Livrarea nu se înregistrează deloc în jurnalul de vânzări al debitorului, pe motiv că factura „nu e a lui”, deși e emisă pe numele și în contul lui.
- Se omite regularizarea cu minus, iar debitorul plătește a doua oară TVA deja virată de organul de executare.
- Se pune TVA pe factură la operațiuni cu taxare inversă sau la operațiuni scutite. Pentru operațiunile scutite de la art. 292 alin. (2) lit. f) CF, debitorul poate opta pentru taxare, prin notificarea de la pct. 58 din norme.

## Ce face iConta.eu

Decontul D300 generat de iConta.eu se calculează din facturile înregistrate. Contabilul se asigură deci că livrarea facturată de organul de executare apare în evidența debitorului. Suma virată de organul de executare se introduce manual la rândul 16, „Regularizări taxă colectată”, prin grila de rânduri manuale a decontului. Aplicația nu emite facturi în numele organelor de executare silită.

[iConta.eu](/)
