---
title: Micro la firmele care fac sponsorizare de imagine
description: Legea nu cunoaște o categorie separată „sponsorizare de imagine” — dacă e o sponsorizare reală, în sensul Legii 32/1994, se aplică regimul micro (abrogat din 2024); dacă firma primește în schimb servicii de promovare efective, e un contract de publicitate, nu sponsorizare, și regulile sunt complet diferite.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Micro la firmele care fac sponsorizare de imagine

„Sponsorizare de imagine” nu este un termen legal distinct — nu apare ca atare nici în Legea nr. 32/1994 privind sponsorizarea, nici în Codul fiscal. În practică, expresia ascunde de fapt **două situații complet diferite**, cu regim fiscal diferit pentru o microîntreprindere, iar distincția contează mult mai mult decât eticheta pusă pe contract.

## Temeiul legal

::: ghid-temei
„(1) Sponsorizarea este actul juridic prin care doua persoane convin cu privire la transferul dreptului de proprietate asupra unor bunuri materiale sau mijloace financiare pentru susținerea unor activități fără scop lucrativ desfășurate de către una dintre părți, denumita beneficiarul sponsorizarii.”

— *Legea nr. 32/1994, art. 1 alin. (1).*

„(1) Sponsorul ori beneficiarul are dreptul sa aducă la cunoștința publicului sponsorizarea prin promovarea numelui, a marcii sau a imaginii sponsorului. ... (5) În cadrul activităților de sponsorizare sau de mecenat se interzice ca sponsorul, mecena sau beneficiarul să efectueze reclama sau publicitate comercială, anterioară, concomitenta sau ulterioară în favoarea acestora sau a altor persoane.”

— *Legea nr. 32/1994, art. 5.*
:::

## Cele două situații care se confundă sub „sponsorizare de imagine”

1. **Sponsorizare reală, cu simpla menționare publică a sponsorului.** Legea permite beneficiarului sau sponsorului să facă public actul de sponsorizare, promovând numele, marca sau imaginea sponsorului (art. 5 alin. 1) — dar **gratuit** (art. 5 alin. 4) și fără să devină reclamă sau publicitate comercială (art. 5 alin. 5). Dacă asta e tot ce primește firma sponsor în schimb — vizibilitate/asociere de imagine, fără o prestație de publicitate contractată separat — rămâne sponsorizare în sensul legii, iar la o microîntreprindere se aplică (sau nu) regimul de credit fiscal de la art. 56 alin. (1^1) din Codul fiscal, care a fost **abrogat de la 1 ianuarie 2024**.
2. **Contract de publicitate/reclamă, numit impropriu „sponsorizare”.** Dacă firma plătește o sumă și primește în schimb o prestație de publicitate reală — logo pe materiale, mențiuni comerciale repetate, spații de reclamă — nu mai e sponsorizare în sensul Legii 32/1994 (art. 5 alin. 5 interzice exact combinația sponsorizare + reclamă comercială în favoarea sponsorului), ci un contract de prestări servicii de publicitate. Cheltuiala e deductibilă integral ca cheltuială de marketing/publicitate, dar **nu intră sub niciun regim de credit fiscal de sponsorizare** — nici cel de la profit (art. 25 alin. 4 lit. i), nici cel abrogat de la micro.

## Ce se greșește în practică

- Se numește „sponsorizare de imagine” un contract cu contraprestație publicitară reală, în speranța unui tratament fiscal mai avantajos — regimul de credit fiscal de sponsorizare nu se aplică unei prestații de publicitate.
- Se presupune că, fiind vorba de „imagine”, ar exista o regulă specială, diferită de sponsorizarea „obișnuită” — legea nu face această distincție; contează dacă există sau nu contraprestație comercială.
- La o microîntreprindere, se așteaptă o deducere din impozitul micro pentru o sponsorizare de imagine acordată în 2024-2026 — facilitatea micro a fost abrogată, indiferent de tipul sponsorizării.

## Ce face iConta.eu

`core/sponsorizari.py` nu distinge tipuri de sponsorizare (de imagine, culturală, sportivă etc.) — tratează orice sumă introdusă ca sponsorizare în sensul Legii 32/1994, cu nota contabilă `6582 = 401` (la contract) sau `6582 = 5121` (la plată directă). Aplicația nu verifică și nu poate verifica dacă în spatele contractului există sau nu o contraprestație de publicitate — această calificare rămâne responsabilitatea contabilului, pe baza clauzelor contractului. Dacă operațiunea e, de fapt, o prestație de publicitate, ea nu ar trebui introdusă prin fluxul de sponsorizare, ci înregistrată ca o cheltuială de marketing obișnuită (pe bază de factură de la prestator, cu conturile de cheltuieli/TVA uzuale), fără a trece prin `credit_sponsorizare()`.

Pentru ramura `tip_impozit="micro"` a funcției `credit_sponsorizare()`, indiferent de natura sponsorizării, calculul e activ doar pentru `la_data` în intervalul 01.04.2019–31.12.2023; pentru orice dată din 2026, funcția returnează credit 0.

[iConta.eu](/)
