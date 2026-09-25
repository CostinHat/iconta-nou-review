---
title: "Cum se înregistrează onorariile încasate cash 2026"
description: "Plafonul legal pentru încasările în numerar de la persoane fizice, aplicabil onorariilor plătite cash de clienți, conform Legii nr. 70/2015."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează onorariile încasate cash 2026

Un onorariu plătit cash de un client persoană fizică nu poate fi încasat oricât de mult dintr-o dată — legea limitează încasările în numerar de la o persoană fizică la un plafon zilnic, indiferent dacă suma provine dintr-o singură plată sau ar fi fragmentată artificial în mai multe tranșe pentru a ocoli plafonul.

## Temeiul legal

::: ghid-temei
„Articolul 4 (1) Operațiunile de încasări în numerar efectuate de persoanele prevăzute la art. 1 alin. (1), de la persoane fizice, reprezentând cesiuni de creanțe, primiri de împrumuturi sau alte finanțări, precum și contravaloarea unor livrări de bunuri sau a unor prestări de servicii se efectuează în limita unui plafon zilnic de 10.000 lei de la o persoană. [...] Sunt interzise încasările fragmentate de la o persoană, pentru operațiunile de încasări în numerar prevăzute la alin. (1), cu o valoare mai mare de 10.000 lei, precum și fragmentarea tranzacțiilor [...] respectiv fragmentarea unei livrări de bunuri sau a unei prestări de servicii, cu valoare mai mare de 10.000 lei."
— Legea nr. 70/2015 pentru întărirea disciplinei financiare privind operațiunile de încasări și plăți în numerar, art. 4 alin. (1) și (2) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Practic, pentru un profesionist (avocat, consultant, notar, orice prestator de servicii) care încasează onorarii cash de la clienți persoane fizice:

- **Plafonul e de 10.000 lei pe zi, de la aceeași persoană** — nu contează câte servicii separate se facturează în aceeași zi către același client, suma cumulată încasată cash de la el nu poate depăși plafonul.
- **Fragmentarea e explicit interzisă**: dacă onorariul total pentru un serviciu depășește 10.000 lei, nu se poate „împărți" plata cash în mai multe tranșe (chiar în zile diferite) tocmai pentru a rămâne sub plafon — legea sancționează atât fragmentarea încasării, cât și fragmentarea prestației de servicii în sine, dacă scopul e evitarea plafonului.
- Suma care depășește plafonul de 10.000 lei trebuie încasată prin instrumente de plată fără numerar (transfer bancar, card) — nu poate fi acceptată cash „peste plafon", nici parțial.

## Ce se greșește în practică

- Se acceptă onorarii cash care depășesc 10.000 lei de la același client, presupunând că plafonul se aplică doar per factură, nu per persoană/zi — legea leagă plafonul de persoana plătitoare pe zi calendaristică, indiferent de câte documente acoperă suma.
- Se împarte deliberat un onorariu mare în tranșe cash succesive, sub pragul de 10.000 lei fiecare, pentru a „respecta formal" plafonul — aceasta e exact fragmentarea interzisă explicit de art. 4 alin. (2).
- Se ignoră cumulul mai multor operațiuni cu aceeași persoană în aceeași zi (de exemplu, un avans plus onorariul final) — toate încasările cash de la aceeași persoană, în aceeași zi, se cumulează pentru verificarea plafonului.

## Ce face iConta.eu

iConta.eu are o funcționalitate reală de verificare a plafoanelor de casă, în `core/casa.py`: constanta `PLAFON_PF = 10000` reflectă exact plafonul legal pentru încasările de la persoane fizice (art. 4 alin. 1 din Legea 70/2015), iar funcția `verifica_plafon()` compară suma încasărilor cumulate de la aceeași persoană, în aceeași zi, cu acest plafon și semnalează un avertisment (`PLAFON_PF`) atunci când e depășit. Aplicația nu poate detecta însă o fragmentare intenționată pe mai multe zile diferite, concepută explicit pentru a ocoli plafonul — o astfel de practică rămâne o evaluare pe care contabilul trebuie s-o facă, dincolo de verificarea automată zilnică.

[iConta.eu](/)
