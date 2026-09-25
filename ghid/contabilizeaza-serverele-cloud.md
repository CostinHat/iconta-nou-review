---
title: "Cum se contabilizează serverele cloud?"
description: "Un server cloud închiriat (IaaS) e o prestare de servicii, nu o achiziție de mijloc fix — se înregistrează pe cheltuială curentă, cu taxare inversă dacă furnizorul nu e stabilit în România."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează serverele cloud?

„Serverul cloud" e o denumire înșelătoare din punct de vedere contabil: firma nu cumpără un echipament fizic, ci închiriază capacitate de calcul (IaaS — Infrastructure as a Service) pe durata abonamentului. Din această diferență decurge tot tratamentul: nu e vorba de un mijloc fix amortizabil, ci de o prestare de servicii recurentă, cu regulile de TVA specifice serviciilor B2B transfrontaliere.

## Temeiul legal

::: ghid-temei
„Mijlocul fix amortizabil este orice imobilizare corporală care îndeplinește cumulativ următoarele condiții: a) este deținut și utilizat în producția, livrarea de bunuri sau în prestarea de servicii, pentru a fi închiriat terților sau în scopuri administrative; b) la data intrării în patrimoniul contribuabilului, are o valoare fiscală egală sau mai mare decât suma de 5.000 lei [...]; c) are o durată normală de utilizare mai mare de un an."
— Legea 227/2015, art. 28 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cum se aplică serverelor cloud:

- Un abonament la o infrastructură cloud (server virtual, spațiu de stocare, capacitate de procesare) nu e „deținut în patrimoniul contribuabilului" — firma nu are dreptul de proprietate asupra unui echipament identificabil, ci accesul contractual la o resursă gestionată de furnizor. Nu îndeplinește condiția de la art. 28 alin. (2) lit. a)-b), deci **nu se amortizează ca mijloc fix**, indiferent de valoarea lunară facturată.
- Costul lunar/anual al abonamentului cloud se înregistrează direct pe cheltuială curentă (cont de servicii executate de terți), în perioada la care se referă, conform principiului contabilității de angajamente.
- Dacă furnizorul de servicii cloud nu e stabilit în România (majoritatea marilor furnizori — AWS, Google Cloud, Microsoft Azure, prin entitățile lor europene), se aplică aceleași reguli de taxare inversă ca la orice serviciu B2B transfrontalier: locul prestării e la sediul beneficiarului (art. 278 alin. (2)), iar TVA se datorează de firma din România, prin taxare inversă (art. 307 alin. (2)).
- Diferența față de o achiziție de echipament fizic (un server cumpărat și instalat local) e esențială: acela ar intra sub incidența art. 28 dacă depășește pragul de 5.000 lei și are durată de utilizare peste un an, cu amortizare pe durata normală de funcționare — un abonament cloud nu.

## Ce se greșește în practică

- Se capitalizează costul unui abonament cloud anual plătit în avans ca „mijloc fix" sau ca imobilizare, pe motiv că suma depășește pragul de 5.000 lei — pragul din art. 28 se aplică doar bunurilor deținute în patrimoniu, nu serviciilor de infrastructură închiriate.
- Se omite taxarea inversă a facturii de la furnizorul cloud nestabilit în România, tratând-o ca pe o cheltuială „gata cu TVA inclus" pentru că suma facturată e în valută și pare „externă", nu supusă regulilor românești de TVA.
- Se recunoaște integral cheltuiala în luna plății, chiar dacă abonamentul acoperă o perioadă viitoare (plată anuală în avans) — corect e repartizarea cheltuielii pe perioada la care se referă serviciul, prin cheltuieli în avans.

## Ce face iConta.eu

iConta.eu tratează achizițiile de servicii ca prestări curente, nu ca mijloace fixe, și aplică taxarea inversă (4426=4427, sau TVA nedeductibilă dar datorată pentru firmele neplătitoare conform art. 317) pentru achizițiile de la furnizori nestabiliți în România. Aplicația nu clasifică automat o factură ca „abonament cloud" versus „achiziție de echipament" — utilizatorul e cel care alege contul contabil corect (cheltuială de servicii vs. imobilizare) la introducerea notei; iConta.eu aplică apoi regulile de TVA și, dacă e cazul, de amortizare corespunzătoare alegerii făcute.

[iConta.eu](/)
