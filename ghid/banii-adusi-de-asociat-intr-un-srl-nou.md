---
title: Cum înregistrezi banii aduși de un asociat într-un SRL nou-înființat
description: Banii pe care un asociat îi aduce în firmă, fără majorare de capital social, sunt un împrumut și se înregistrează în contul 4551, nu ca aport la capital sau ca venit al firmei.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum înregistrez banii aduși de un asociat într-un SRL nou-înființat?

La înființare, o firmă are adesea nevoie de mai mulți bani decât capitalul social minim depus. Soluția obișnuită e ca asociatul să pună la dispoziția firmei o sumă suplimentară — dar contabil, acea sumă nu e capital, dacă nu trece prin procedura de majorare a capitalului social la Registrul Comerțului. Rămâne o datorie a firmei față de asociat, adică un împrumut.

## Temeiul legal

::: ghid-temei
**Codul fiscal (Legea 227/2015), art. 97 alin. (2)** — dacă suma poartă dobândă: „Veniturile sub formă de dobânzi [...], contractele civile încheiate se impun cu o cotă de 10% din suma acestora, impozitul fiind final [...] calculul impozitului datorat de către plătitorii de venit se efectuează la momentul plății dobânzii."

**Legea 31/1990, art. 67 alin. (2^4)** — adăugat de Legea 239/2025, în vigoare din 18.12.2025: „Societățile care, pe baza situațiilor financiare anuale, aprobate potrivit legii, au o valoare a activului net diminuată la mai puțin de jumătate din valoarea capitalului social subscris nu pot restitui acționarilor sau asociaților [...] împrumuturile luate de la aceștia."
:::

## Capital social vărsat, sau împrumut?

Cele două operațiuni nu se confundă:

- **Aport la capital social** — trece printr-o hotărâre de majorare a capitalului, se înregistrează la Registrul Comerțului, iar suma devine capital propriu al firmei (`456 = 1012`, la vărsare). Asociatul primește în schimb părți sociale suplimentare, nu banii înapoi.
- **Împrumut** — nu implică nicio formalitate la Registrul Comerțului, suma rămâne datorie a firmei și se restituie asociatului conform contractului. Se înregistrează în contul 4551.

Dacă banii intră în firmă fără nicio hotărâre de majorare de capital, contabil ei sunt un împrumut, indiferent de intenția inițială a asociatului.

## Înregistrarea contabilă

**La primirea sumei:**

- `5121 = 4551` — cu suma încasată în contul bancar al firmei

**La restituire**, cu dobândă (dacă a fost convenită):

- `4551 = 5121` — restituirea principalului
- `666 = 4551` — dobânda datorată asociatului
- `4551 = 446` — impozitul de 10% reținut pe dobândă
- `4551 = 5121` — plata dobânzii nete

## Un exemplu

::: ghid-exemplu
Asociatul unic al unui SRL nou-înființat depune **15.000 lei** în contul firmei, pentru capital de lucru, fără să majoreze capitalul social. Suma se înregistrează `5121 = 4551`, cu 15.000 lei.

După șase luni, firma restituie asociatului 5.000 lei din sumă, fără dobândă (nu a fost stabilită prin contract). Înregistrarea e simplă: `4551 = 5121`, cu 5.000 lei — soldul rămas pe 4551 e de 10.000 lei.
:::

O restituire ca aceasta e exact operațiunea vizată de art. 67 alin. (2⁴): dacă la data restituirii activul net al firmei (din ultimele situații financiare anuale aprobate) e sub jumătate din capitalul social subscris, firma nu are voie să dea banii înapoi asociatului, indiferent că suma e mică sau că nu poartă dobândă.

## Ce se greșește în practică

- **Se tratează suma ca aport la capital, fără hotărâre de majorare și fără înregistrare la Registrul Comerțului.** Fără această formalitate, banii rămân contabil un împrumut, nu capital propriu.
- **Se lasă suma nedocumentată**, ca simplu transfer bancar fără contract sau decizie a asociatului. Fără document, natura sumei e greu de dovedit la un control.
- **Se calculează dobândă „informal", fără reținere de impozit.** Dacă părțile convin o dobândă, impozitul de 10% se reține și se virează de firmă la plata dobânzii, nu se lasă în sarcina asociatului.

## Ce face iConta.eu

Aplicația înregistrează automat primirea sumei de la asociat (`5121 = 4551`) și restituirea acesteia, inclusiv dobânda calculată și impozitul de 10% reținut la sursă, dacă operațiunea e introdusă ca împrumut.

Distincția între împrumut și aport la capital social rămâne o decizie a contabilului la introducerea operațiunii — aplicația nu verifică automat dacă suma a fost sau nu însoțită de o majorare de capital social la Registrul Comerțului.

[iConta.eu](/)
