---
title: "Cum înregistrez o chitanță găsită după închiderea lunii?"
description: "Ce spune legea despre perioadele contabile închise și blocarea modificărilor, plus ce verifică (și ce nu verifică) azi iConta.eu la emiterea unei chitanțe."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum înregistrez o chitanță găsită după închiderea lunii?

O chitanță apare, uitată prin hârtii, după ce luna în care s-a petrecut operațiunea e deja închisă contabil. Legea recunoaște explicit conceptul de „perioadă închisă" — dar regula ei nu e despre cum se forțează o înregistrare veche, ci despre faptul că, odată închisă, o perioadă nu mai trebuie atinsă.

## Temeiul legal

::: ghid-temei
„Sistemele informatice de prelucrare automată a datelor în domeniul financiar-contabil trebuie să răspundă la următoarele criterii considerate minimale: [...] să nu permită inserări, modificări sau eliminări de date pentru o perioadă închisă [...]"
— OMFP 2634/2015, Anexa 1 „Norme generale", pct. 58 lit. h) (sursă: anaf_surse/omfp_2634_2015_anexa1_norme_generale.txt)
:::

- Norma cere explicit ca programele informatice financiar-contabile să **blocheze** inserările, modificările sau eliminările de date pentru o perioadă deja închisă — nu să ofere o cale de a „forța" retroactiv o înregistrare veche.
- Consecința practică: o chitanță găsită după închiderea lunii nu se introduce cu data ei reală, din luna închisă, ci se tratează ca eveniment contabil constatat în perioada curentă, de regulă printr-o notă de contabilitate care documentează atât operațiunea inițială omisă, cât și data la care a fost descoperită.
- Aceeași regulă a succesiunii cronologice a documentelor (relevantă și pentru omisiuni recente) se aplică și aici — doar că, peste o perioadă închisă, corecția nu mai poate „intra" direct în luna veche, ci trebuie reflectată în perioada deschisă curentă.

## Ce se greșește în practică

- Se încearcă introducerea chitanței direct cu data ei reală, într-o lună deja raportată — exact ce norma de mai sus interzice pentru sistemele informatice, și ce ridică probleme și când evidența se ține manual.
- Se ignoră complet chitanța găsită târziu, sub argumentul că „luna e oricum închisă" — deși operațiunea economică rămâne reală și trebuie reflectată, doar în perioada curentă, nu retroactiv.
- Se confundă „închiderea lunii" din contabilitatea internă a firmei cu termenele de depunere a declarațiilor fiscale — cele două nu coincid neapărat, iar tratamentul corect depinde de care dintre ele a fost deja definitivată.

## Ce face iConta.eu

Verificat exhaustiv în codul funcției `chitanta_emite`: singurele validări la emiterea unei chitanțe sunt suma mai mare decât zero, existența facturii legate (dacă e cazul) și starea „emisă" a acesteia — **nu există nicio verificare de perioadă sau lună închisă** cuplată la emiterea de chitanțe în acest modul. Practic, iConta.eu permite azi emiterea unei chitanțe noi oricând, fără un mecanism de blocare pe perioade închise specific acestei funcționalități; conceptul de perioadă închisă cerut de normă (pct. 58 lit. h) de mai sus) nu e implementat aici. Dacă găsești o chitanță din luna închisă, tratarea ei corectă — cu notă de contabilitate în perioada curentă — rămâne, la acest moment, un pas manual.

[iConta.eu](/)
