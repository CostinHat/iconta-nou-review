---
title: "Amortizarea mijloacelor fixe de leasing înapoi (lease-back)"
description: "Cum tratează reglementările contabile OMFP 1802/2014 amortizarea activului într-o operațiune de vânzare urmată de închiriere în leasing (leaseback), în funcție de tipul de leasing rezultat."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Amortizarea mijloacelor fixe de leasing înapoi (lease-back)

O operațiune de leaseback — vinzi un activ pe termen lung și îl iei imediat înapoi în leasing — pune o întrebare contabilă directă: cine mai amortizează activul după tranzacție, vânzătorul devenit locatar sau cumpărătorul devenit locator? Răspunsul depinde exclusiv de tipul de leasing rezultat din contract, nu de forma juridică a tranzacției.

## Temeiul legal

::: ghid-temei
„O tranzacție de vânzare a unui activ pe termen lung și de închiriere a aceluiași activ în regim de leasing (leaseback) se contabilizează în funcție de clauzele contractului de leasing, astfel: a) dacă tranzacția de vânzare și închiriere a aceluiași activ are ca rezultat un leasing financiar, tranzacția reprezintă un mijloc prin care locatorul acordă o finanțare locatarului, activul având rol de garanție. Entitatea beneficiară a finanțării (locatarul) nu va recunoaște în contabilitate operațiunea de vânzare a activului, nefiind îndeplinite condițiile de recunoaștere a veniturilor. Activul rămâne înregistrat în continuare la valoarea existentă anterior operațiunii de leasing, cu regimul de amortizare aferent. [...] b) dacă tranzacția de vânzare și închiriere a aceluiași activ are ca rezultat un leasing operațional, entitatea vânzătoare contabilizează o tranzacție de vânzare, cu înregistrarea scoaterii din evidență a activului și a sumelor încasate sau de încasat și a taxei pe valoarea adăugată pentru operațiunile taxabile [...]"
— OMFP 1802/2014, Reglementări contabile, pct. 219 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Concret, tratamentul amortizării se împarte în două scenarii, exact ca la orice contract de leasing:

- **Leaseback cu rezultat leasing financiar** — activul **rămâne înregistrat la vânzătorul-locatar**, la valoarea existentă anterior tranzacției, cu **regimul de amortizare aferent continuat**. Vânzarea nu se recunoaște contabil ca venit; tranzacția e tratată drept o finanțare garantată cu activul, nu drept o vânzare reală. Amortizarea rămâne, deci, în sarcina fostului proprietar, acum locatar.
- **Leaseback cu rezultat leasing operațional** — vânzătorul recunoaște efectiv vânzarea (scoate activul din evidență, înregistrează suma încasată și TVA), iar activul trece la cumpărătorul-locator, care devine cel care amortizează, conform regulii generale de la leasingul operațional (amortizare de către locator/finanțator).
- Criteriul de departajare între cele două cazuri e cel general de clasificare a leasingului (transfer de risc și avantaje, opțiune de cumpărare la preț avantajos, durata contractului față de durata de viață economică etc.), nu forma juridică a operațiunii de leaseback în sine.

## Ce se greșește în practică

- Se scoate activul din evidența vânzătorului la orice operațiune de leaseback, indiferent de rezultatul de leasing financiar sau operațional — dacă rezultă leasing financiar, activul rămâne înregistrat și amortizat de vânzător, vânzarea nefiind recunoscută contabil.
- Se recunoaște un venit din vânzare la momentul tranzacției de leaseback financiar, deși reglementarea spune explicit că „nu sunt îndeplinite condițiile de recunoaștere a veniturilor" în acest caz.
- Se schimbă regimul de amortizare (metodă, durată) odată cu operațiunea de leaseback financiar, deși textul prevede continuarea „regimului de amortizare aferent" existent înainte de tranzacție, nu un regim nou.

## Ce face iConta.eu

Motorul de amortizare al iConta.eu (`core/d406_active.py`) calculează amortizarea unui mijloc fix pe baza metodei și duratei setate pentru activ, indiferent de proveniența acestuia. La data acestui ghid, iConta.eu **nu distinge automat** o operațiune de leaseback de o achiziție sau o vânzare obișnuită de mijloc fix și nu determină singură dacă rezultatul contractului e leasing financiar sau operațional — încadrarea corectă a tranzacției (păstrarea activului la vânzător cu amortizare continuată, sau scoaterea lui din evidență cu recunoașterea vânzării), conform pct. 219 din OMFP 1802/2014, rămâne o decizie manuală a contabilului.

[iConta.eu](/)
