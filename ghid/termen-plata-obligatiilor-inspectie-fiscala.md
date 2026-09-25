---
title: "Ce termen am pentru plata obligațiilor după o inspecție fiscală?"
description: "Termenul legal de plată pentru sumele stabilite printr-o decizie de impunere emisă în urma unei inspecții fiscale, în funcție de data comunicării deciziei."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce termen am pentru plata obligațiilor după o inspecție fiscală?

Când o inspecție fiscală se încheie cu o decizie de impunere, termenul de plată nu e o dată fixă calculată din ziua controlului, ci depinde de **data la care decizia a fost comunicată** contribuabilului. Codul de procedură fiscală tratează separat această situație de scadența obișnuită a impozitelor.

## Temeiul legal

::: ghid-temei
„ART. 156 Termenele de plată
(1) Pentru diferențele de obligații fiscale principale și pentru obligațiile fiscale accesorii, stabilite prin decizie potrivit legii, termenul de plată se stabilește în funcție de data comunicării deciziei, astfel:
a) dacă data comunicării este cuprinsă în intervalul 1 - 15 din lună, termenul de plată este până la data de 5 a lunii următoare, inclusiv;
b) dacă data comunicării este cuprinsă în intervalul 16 - 31 din lună, termenul de plată este până la data de 20 a lunii următoare, inclusiv."
— Legea 207/2015, art. 156 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Așadar, pentru diferențele de impozite, taxe și contribuții stabilite printr-o decizie de impunere emisă în urma unei inspecții fiscale:

- Dacă **decizia a fost comunicată între 1 și 15 ale lunii**, termenul de plată este **5 ale lunii următoare**.
- Dacă **decizia a fost comunicată între 16 și 31 ale lunii**, termenul de plată este **20 ale lunii următoare**.
- Aceleași reguli se aplică și pentru obligațiile accesorii (dobânzi, penalități) stabilite prin aceeași decizie, precum și, potrivit alin. (2), pentru decizia de atragere a răspunderii solidare sau decizia de impunere emisă pe baza unei declarații rectificative.
- Neplata până la acest termen face ca sumele să devină **obligații fiscale restante** (art. 157), cu efect asupra certificatului de atestare fiscală și asupra eventualelor înlesniri la plată.

## Ce se greșește în practică

- Se calculează termenul de la **data controlului** sau de la data raportului de inspecție fiscală, nu de la data comunicării efective a deciziei de impunere — cele două date pot diferi cu săptămâni.
- Se aplică un termen unic „30 de zile" din practica altor proceduri, deși art. 156 stabilește două termene fixe (5, respectiv 20 ale lunii următoare), în funcție de intervalul din lună în care a fost comunicată decizia.
- Se ignoră faptul că neplata la termen transformă suma în obligație restantă chiar dacă termenul de plată propriu-zis nu s-a împlinit încă — art. 157 alin. (1) lit. b) include explicit diferențele stabilite prin decizie de impunere printre restanțe, indiferent de termenul de plată din art. 156.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu calculează automat termenul de plată** dintr-o decizie de impunere primită în urma unei inspecții fiscale — aceasta nu e o cifră pe care aplicația o generează, ci o dată comunicată de organul fiscal, pe care contabilul o introduce manual. Aplicația are însă un modul real de urmărire a conformării fiscale (`core/control_fiscal_api.py`), care compară declarațiile datorate cu cele depuse pe baza scadențarului oficial ANAF și afișează un semafor (verde/galben/gri/roșu) per firmă, plus notificări automate către contabili când apare o neconformitate (`core/alerte_control_fiscal.py`) — dar acest mecanism urmărește declarațiile curente, nu termenele dintr-o decizie de impunere post-control.

[iConta.eu](/)
