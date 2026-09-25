---
title: "Cum se înregistrează un mijloc fix cumpărat prin leasing financiar?"
description: "Ciclul complet la locatar: primirea bunului (2133=167), ratele lunare (167/666/628=404+4426) și închiderea prin valoarea reziduală (167=404), conform OMFP 1802/2014."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează un mijloc fix cumpărat prin leasing financiar?

La leasingul financiar, mijlocul fix intră în contabilitatea firmei utilizatoare (locatarul) chiar de la primire, ca o investiție în imobilizări — nu treptat, pe măsura plății ratelor. Monografia are trei etape: primirea bunului, ratele lunare și, dacă e cazul, valoarea reziduală de la final.

## Temeiul legal

::: ghid-temei
„215. ‐ (1) Reflectarea în contabilitatea locatarilor a activelor aferente operațiunilor de leasing financiar se efectuează cu ajutorul conturilor de imobilizări necorporale şi imobilizări corporale. (2) Dobânzile de plătit corespunzătoare datoriilor din operațiuni de leasing financiar se înregistrează în contabilitatea locatarilor periodic, conform contabilității de angajamente, în contrapartida contului de cheltuieli. Dobânda de plătit, aferentă perioadelor viitoare, se evidențiază în conturi în afara bilanțului (contul 8051 «Dobânzi de plătit»)."
— OMFP 1802/2014, pct. 215 alin. (1)-(2) (sursă: anaf_surse/omfp_1802_2014.txt)
:::

- **Primirea bunului**: se recunoaște la valoarea capitalului din contract (avans + rate de capital + valoare reziduală), pe conturile de imobilizări — 2133=167. Dobânda totală a contractului nu e încă o cheltuială: se ține extracontabil, pe 8051, până se facturează.
- **Fiecare rată**: capitalul închide treptat 167, dobânda facturată devine cheltuială (666), eventualul comision intră pe 628, iar TVA se calculează pe întreaga bază a facturii (capital + dobândă + comision) — nu doar pe capital.
- **Valoarea reziduală**, la final: închide definitiv datoria (167=404), cu TVA aferentă.

## Ce se greșește în practică

- Se înregistrează toată valoarea contractului (capital + dobândă) pe contul de imobilizare (2133) la primire, în loc de doar capitalul.
- Se trece dobânda direct pe cheltuială (666) chiar de la primirea bunului, în loc s-o țină extracontabil până la facturarea ei efectivă.
- Se calculează TVA doar pe partea de capital a ratei, ignorând că se aplică pe întreaga bază facturată — capital, dobândă și comision.

## Ce face iConta.eu

Ecranul „Operațiuni speciale" → intrarea „Leasing" acoperă exact acest ciclu: „Primire bun (financiar)" scrie 2133=167 (plus 8051 extracontabil, dacă există dobândă totală), „Rată lunară" scrie 167/666/628=404, cu TVA pe 4426, iar „Valoare reziduală" închide 167. **Atenție**: la data acestui ghid, formularul din acest ecran nu colectează cota de TVA pentru tipurile „Rată lunară" și „Valoare reziduală" — deși motorul de calcul le acceptă corect, trimiterea lor din acest ecran eșuează azi cu o eroare de validare; funcționează din interfață doar tipul „Primire bun (financiar)". Amortizarea ulterioară a bunului nu face parte din acest ecran — se ține separat, în registrul de Mijloace fixe.

[iConta.eu](/)
