---
title: "Cum declar dividendele distribuite în lanț de firme"
description: "Regulile de impozitare a dividendelor plătite între persoane juridice române în structuri de tip holding, inclusiv scutirea aplicabilă în lanț."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum declar dividendele distribuite în lanț de firme

Când o societate românească distribuie dividende către o altă societate românească, iar aceasta la rândul ei le redistribuie propriilor asociați, riscul e ca aceeași sumă să fie impozitată de mai multe ori pe parcursul lanțului. Codul fiscal reglementează exact acest caz: regula generală de impozitare la 16% se aplică, dar există și o scutire pentru deținerile stabile de tip participație, menită să evite impozitarea în cascadă.

## Temeiul legal

::: ghid-temei
„O persoană juridică română care plătește dividende către o persoană juridică română are obligația să rețină, să declare și să plătească impozitul pe dividende reținut către bugetul de stat [...]. Impozitul pe dividende se stabilește prin aplicarea unei cote de impozit de 16% asupra dividendului brut plătit unei persoane juridice române. [...]
(4) Prevederile prezentului articol nu se aplică în cazul dividendelor plătite de o persoană juridică română unei alte persoane juridice române, dacă, la data plății dividendelor, fiecare dintre aceste persoane îndeplinește cumulativ următoarele condiții: a) persoana juridică beneficiară a dividendelor: (i) deține minimum 10% din titlurile de participare ale persoanei juridice române care plătește dividendele, pe o perioadă de un an împlinit până la data plății acestora inclusiv; [...] (iii) plătește, fără posibilitatea unei opțiuni sau exceptări, impozit pe profit sau orice alt impozit care substituie impozitul pe profit."
— Codul fiscal (Legea 227/2015), art. 43 alin. (1), (2) și (4) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Aplicat la un lanț de firme (de exemplu firma C plătește dividende către firma B, care le redistribuie firmei A):

- **Regula de bază**: fiecare plată de dividende între două persoane juridice române se impozitează separat, cu reținere la sursă de 16%, făcută de firma care plătește dividendul (cota e valabilă pentru dividendele distribuite începând cu 1 ianuarie 2026).
- **Scutirea „la lanț"**: dacă beneficiarul dividendului (firma B, în relația cu C) deține minimum 10% din capitalul firmei plătitoare de cel puțin un an împlinit până la data plății, iar ambele sunt plătitoare de impozit pe profit fără opțiune de exceptare, plata respectivă **nu se impozitează deloc** — nici cu 16%, nici cu altă cotă.
- Scutirea se verifică **separat, la fiecare verigă a lanțului** — condițiile de deținere ≥10% și vechime de 1 an trebuie îndeplinite de fiecare pereche plătitor-beneficiar în parte, nu doar la capătul lanțului.
- Dacă vreo verigă nu îndeplinește condițiile (de exemplu deținerea e sub 10%, sau perioada de un an nu e împlinită la data plății), acea plată se impozitează cu 16%, chiar dacă restul lanțului e scutit.

## Ce se greșește în practică

- Se presupune că scutirea se aplică automat oricărei plăți „în interiorul grupului", fără verificarea concretă a pragului de 10% și a vechimii de 1 an la data plății.
- Se calculează scutirea o singură dată, la nivelul întregului lanț, în loc să se verifice fiecare relație plătitor-beneficiar separat.
- Se ignoră condiția ca ambele persoane implicate să plătească impozit pe profit fără opțiune de exceptare — o firmă micro nu se încadrează automat aici, pentru că regimul de impozit pe veniturile microîntreprinderilor nu e „impozit pe profit" în sensul acestei scutiri.
- Se distribuie dividendul înainte de împlinirea celor 12 luni de deținere, pierzând astfel scutirea pentru acea plată, deși ea ar fi fost aplicabilă câteva zile mai târziu.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu are o funcție dedicată calculului sau declarării dividendelor distribuite în structuri de tip holding/lanț de firme — nu am găsit în cod vreun modul care să urmărească deținerile între entități afiliate sau să aplice automat scutirea de la art. 43 alin. (4). Impozitarea dividendelor între persoane juridice, mai ales în lanțuri de firme, rămâne o verificare pe care contabilul trebuie s-o facă manual, verigă cu verigă, conform regulilor de mai sus.

[iConta.eu](/)
