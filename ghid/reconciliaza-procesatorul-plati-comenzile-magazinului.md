---
title: Cum se reconciliază procesatorul de plăți cu comenzile magazinului?
description: Reconcilierea automată din iConta.eu potrivește linii de extras cu facturi pe baza CUI-ului clientului, nu decontări de procesator cu comenzi de magazin online — acest flux rămâne manual.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se reconciliază procesatorul de plăți cu comenzile magazinului?

Un magazin online care încasează prin card acceptă plățile printr-un procesator (de exemplu Stripe sau un alt furnizor de plăți), care le decontează ulterior în contul bancar al firmei, de regulă cumulat, la un interval fix, minus comisionul propriu. Verificarea că fiecare comandă din magazin a fost efectiv încasată și decontată e o operațiune diferită de reconcilierea „linie de extras ↔ factură deschisă" pe care o face motorul de reconciliere bancară din iConta.eu.

## Temeiul legal

::: ghid-temei
„Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ."
— Legea contabilității nr. 82/1991, art. 6 alin. (1)
:::

::: ghid-temei
„Factura este document justificativ care stă la baza înregistrării în contabilitate a operațiunilor economice. Pentru operațiunile economice pentru care, conform prevederilor Codului fiscal, nu există obligația întocmirii facturii, înregistrarea în contabilitate a acestora se efectuează pe baza contractelor încheiate între părți și a documentelor financiar-contabile sau bancare care să ateste acele operațiuni, cum sunt: [...] extras de cont bancar, notă de contabilitate etc."
— OMFP 2634/2015, Anexa 1 „Norme generale", pct. 25
:::

## De ce e un flux diferit de reconcilierea bancară obișnuită

Motorul de reconciliere din iConta.eu lucrează cu o singură direcție de potrivire: fiecare linie din extrasul bancar se caută pe CUI-ul unui partener, printre facturile deschise ale acelui partener. Decontarea unui procesator de plăți nu funcționează așa:

- **Partenerul de pe linia bancară e procesatorul**, nu clientul final — extrasul arată un transfer de la Stripe/procesator, nu de la fiecare cumpărător în parte.
- **Suma e cumulată pe mai multe comenzi** și, de regulă, netă de comisionul procesatorului — nu coincide exact cu nicio factură individuală, deci nu poate ieși „verde" (potrivire exactă) nici măcar dacă s-ar căuta pe CUI-ul procesatorului.
- **Obiectul verificării** nu e „factura X e încasată", ci „toate comenzile plasate în magazin într-o perioadă au fost efectiv decontate în bancă" — o reconciliere comandă-cu-decontare, nu linie-cu-factură.

La data acestui ghid, iConta.eu nu are un modul dedicat care să importe rapoartele de decontare (payout) ale unui procesator de plăți și să le lege automat de comenzile magazinului. Este o direcție avută în vedere pentru extinderea reconcilierii bancare la alte surse decât extrasul clasic, dar neconstruită azi.

## Ce se greșește în practică

- Se caută în ecranul „Bancă" o potrivire automată între decontarea Stripe/procesator și comenzile magazinului, care nu poate apărea, pentru că linia bancară nu poartă CUI de client individual.
- Se contabilizează direct suma netă decontată ca venit, fără să se verifice separat, din raportul procesatorului, că suma corespunde exact comenzilor perioadei și comisionului reținut.
- Se confundă acest flux cu reconcilierea unei încasări individuale cu cardul (unde clientul plătește direct și apare identificabil pe linia de extras) — cele două situații au mecanici diferite.

## Ce face iConta.eu

Reconcilierea bancară automată (`core/reconciliere.py`) potrivește linii de extras cu facturi deschise, pe baza CUI-ului unui singur partener pe linie — mecanism care nu se aplică unei decontări cumulate de la un procesator de plăți, aferentă mai multor comenzi de la clienți diferiți. iConta.eu nu importă azi rapoartele de decontare (payout) ale procesatorilor de plăți și nu le leagă automat de comenzile magazinului online. Verificarea rămâne manuală: se compară raportul de tranzacții/decontare al procesatorului cu lista comenzilor din perioadă, iar suma netă decontată se înregistrează contabil cu separarea comisionului reținut ca cheltuială.

[iConta.eu](/)
