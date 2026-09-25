---
title: "Cum se înregistrează un mijloc fix cumpărat cu plata în rate?"
description: "Ce intră în costul de achiziție al unui mijloc fix cumpărat cu plata în rate, conform reglementărilor contabile OMFP 1802/2014, și cum se tratează plafonul din 2026."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se înregistrează un mijloc fix cumpărat cu plata în rate?

Plata eșalonată nu schimbă momentul sau valoarea la care se recunoaște mijlocul fix în contabilitate — activul se înregistrează la costul lui de achiziție, stabilit potrivit unei definiții precise, independent de modul în care se face plata.

## Temeiul legal

::: ghid-temei
„6. cost de achiziție înseamnă prețul datorat și eventualele cheltuieli conexe minus eventualele reduceri ale costului de achiziție."
— OMFP 1802/2014, pct. 8 subpct. 6, Secțiunea 1.2 (Definiții) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Aplicat la un mijloc fix cumpărat cu plata în rate:

- mijlocul fix se recunoaște la **costul de achiziție total** — prețul datorat (adică valoarea integrală a bunului, nu doar avansul sau prima rată plătită) plus cheltuielile conexe (transport, instalare, punere în funcțiune), minus eventualele reduceri comerciale;
- faptul că plata se eșalonează în timp **nu modifică** valoarea de intrare a activului — costul de achiziție se determină la data recunoașterii (data la care riscurile și beneficiile trec la cumpărător), nu se „construiește" progresiv, pe măsură ce se achită ratele;
- dobânda sau costul de finanțare eventual inclus într-un contract cu plata eșalonată (dacă e distinct de prețul bunului) urmează regimul general al cheltuielilor financiare, nu intră în costul de achiziție al mijlocului fix, cu excepția cazurilor de capitalizare a dobânzii pentru active calificate, reglementate separat;
- pentru amortizare contează costul de achiziție integral, nu suma efectiv plătită până la un moment dat — amortizarea începe de la data punerii în funcțiune, indiferent de stadiul plăților către furnizor.

## Ce se greșește în practică

- Se înregistrează mijlocul fix la valoarea avansului plătit, urmând ca valoarea să „crească" cu fiecare rată achitată — corect e recunoașterea integrală de la început, la costul de achiziție total, cu o datorie corespunzătoare către furnizor pentru ratele neachitate.
- Se amână recunoașterea și amortizarea mijlocului fix până la achitarea integrală a ratelor — momentul relevant e recunoașterea activului (transferul riscurilor și beneficiilor, respectiv punerea în funcțiune), nu finalizarea plății.
- Se include în costul de achiziție și componenta de dobândă a contractului cu plată eșalonată, dacă aceasta e distinctă și identificabilă în contract — dobânda urmează, de regulă, regimul cheltuielilor financiare, separat de costul activului.

## Ce face iConta.eu

iConta.eu importă și înregistrează mijloacele fixe (`core/mijloace_fixe_import_api.py`) pe baza unui registru cu valoare de intrare, valoare reziduală și durată de amortizare, verificând informativ pragul de 5.000 lei (OUG 8/2026) sub care un bun nu se mai califică drept mijloc fix amortizabil pentru intrările noi din 2026. Aplicația nu are însă o logică separată pentru contractele cu plată în rate — costul de achiziție introdus trebuie să fie deja cel corect, stabilit conform definiției de mai sus, calculul revenind contabilului la introducerea datelor.

[iConta.eu](/)
