---
title: "Stocuri achiziționate pe credit: momentul înregistrării"
description: "Regula contabilă care stabilește când se înregistrează în gestiune stocurile cumpărate pe credit comercial, indiferent de momentul plății furnizorului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Stocuri achiziționate pe credit: momentul înregistrării

Când o firmă cumpără mărfuri sau materii prime „pe credit" — adică plătește furnizorul mai târziu, pe bază de scadență de plată — apare frecvent întrebarea dacă stocul se înregistrează în gestiune la data facturii, la data primirii banilor de la furnizor (adică niciodată, e o confuzie) sau la data plății. Reglementările contabile sunt clare: momentul înregistrării nu are legătură cu momentul plății, ci cu momentul la care riscurile și beneficiile aferente bunurilor trec la cumpărător.

## Temeiul legal

::: ghid-temei
„Înregistrarea în contabilitate a intrării stocurilor se efectuează la data transferului riscurilor și beneficiilor. [...] În general, datele de transfer al controlului, de transfer al proprietății și de livrare coincid. Totuși, pot exista decalaje de timp, de exemplu, pentru: [...] – bunuri recepționate pentru care nu s-a primit încă factura, care trebuie înregistrate în activele cumpărătorului; [...] – bunuri livrate și nefacturate, care trebuie scoase din evidență, transferul de proprietate având loc [...]"
— OMFP 1802/2014, Reglementări contabile, pct. 283 alin. (1)-(2) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Din text rezultă regula centrală, valabilă indiferent de termenul de plată agreat cu furnizorul:

- Stocul intră în gestiune **la data transferului riscurilor și beneficiilor**, care de regulă coincide cu recepția fizică a bunurilor — nu cu momentul plății, nu cu momentul emiterii facturii de către furnizor și nu cu scadența creditului comercial acordat de acesta.
- Dacă bunurile ajung la cumpărător înainte de factură, ele tot trebuie **înregistrate în activele cumpărătorului** la recepție, chiar dacă documentul fiscal nu a sosit încă — practic pe baza avizului de însoțire a mărfii sau a altui document de recepție.
- Simetric, dacă bunurile au fost livrate dar nefacturate, ele se scot din evidența vânzătorului odată ce transferul de proprietate a avut loc, indiferent când se emite factura.
- Punctul 284 din aceleași reglementări întărește regula: deținerea de bunuri materiale fără să fie înregistrate în contabilitate este interzisă, iar decalajele dintre aprovizionare și recepție trebuie tratate explicit (bunurile sosite fără factură se înregistrează ca intrări în gestiune pe baza recepției și a documentelor însoțitoare).

## Ce se greșește în practică

- Se amână înregistrarea stocului până la primirea facturii de la furnizor, deși bunurile au fost deja recepționate fizic — ceea ce denaturează stocul scriptic și poate ascunde diferențe la inventar.
- Se confundă „achiziție pe credit" (plată amânată către furnizor, o formă de finanțare comercială) cu momentul de recunoaștere contabilă a stocului — cele două sunt independente; creditul comercial afectează doar contul de datorii (401), nu momentul intrării în gestiune.
- Nu se înregistrează distinct, în conturi în afara bilanțului, bunurile sosite dar nerecepționate (de exemplu, aflate încă în verificare calitativă) — ele nu trebuie tratate ca stoc propriu până la finalizarea recepției.

## Ce face iConta.eu

Acest subiect ține de contabilitatea generală a stocurilor și a creditului comercial furnizor-client, nu de funcționalitatea F086 (sponsorizări și credit fiscal) cercetată pentru acest ghid — cele două noțiuni de „credit" (creditul comercial dintr-o achiziție de mărfuri și creditul fiscal din sponsorizare) nu au nimic în comun. Cercetarea disponibilă pentru acest ghid a verificat direct în cod doar motorul de sponsorizări și garda de plafon din D101 (`core/sponsorizari.py`, `core/d101.py`); nu avem, în acest dosar, o verificare directă a vreunui modul din iConta.eu dedicat gestiunii de stocuri sau recepțiilor de marfă, așa că nu facem aici nicio afirmație despre ce automatizează sau nu automatizează aplicația pe acest subiect.

[iConta.eu](/)
