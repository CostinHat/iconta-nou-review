---
title: "Retenția de garanție la construcții: TVA"
description: "Reținerea contractuală a unei garanții de bună execuție dintr-o factură de construcții nu amână, de regulă, exigibilitatea TVA — cu excepția firmelor la TVA la încasare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Retenția de garanție la construcții: TVA

În contractele de construcții-montaj e o practică frecventă ca beneficiarul să rețină un procent (de regulă 5–10%) din valoarea fiecărei facturi, drept garanție de bună execuție, sumă eliberată abia la recepția finală a lucrării. Întrebarea care revine mereu: se calculează TVA pe toată valoarea facturată, inclusiv partea reținută, sau doar pe suma efectiv încasată?

## Temeiul legal

::: ghid-temei
„Exigibilitatea pentru livrări de bunuri și prestări de servicii [...] (1) Exigibilitatea taxei intervine la data la care are loc faptul generator."
— Legea nr. 227/2015 privind Codul fiscal, art. 282 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Regula generală: TVA devine exigibilă la data faptului generator — adică, pentru o lucrare de construcții, la data recepției/prestării serviciului sau la data facturii, dacă factura e emisă înainte de acest moment. **Reținerea contractuală a unui procent de garanție de către beneficiar nu schimbă acest moment** — antreprenorul datorează TVA pe întreaga valoare facturată, inclusiv pe partea pe care nu o încasează imediat, pentru că e ținută drept garanție.
- Excepția o reprezintă firmele care aplică sistemul TVA la încasare: pentru acestea, art. 282 alin. (3) din același act prevede că „exigibilitatea taxei intervine la data încasării contravalorii integrale sau parțiale a livrării de bunuri ori a prestării de servicii" — deci, pentru partea reținută drept garanție și neîncasată, TVA rămâne neexigibilă până la eliberarea efectivă a garanției de către beneficiar.
- Practic: pentru un antreprenor la regim normal de TVA, garanția reținută nu întârzie plata TVA către buget; pentru unul la TVA la încasare, întârzie — dar numai pe partea reținută, nu pe întreaga factură.

## Ce se greșește în practică

- Se amână, din eroare, declararea și plata TVA aferente sumei reținute drept garanție, considerând (greșit, pentru un plătitor de TVA la regim normal) că taxa devine exigibilă abia la eliberarea garanției.
- Se confundă exigibilitatea TVA cu momentul plății — reținerea de garanție e o problemă de trezorerie/decontare contractuală, nu una de TVA, cu excepția firmelor la TVA la încasare.
- Se emite, pentru comoditate, o factură doar pentru partea încasată, lăsând garanția „în afara" evidenței fiscale, deși întreaga valoare a lucrării trebuie facturată la momentul faptului generator.

## Ce face iConta.eu

Nu s-a găsit, verificat direct în cod (`core/`), niciun modul dedicat retenției de garanție la construcții — nici la nivelul motoarelor contabile, nici la nivelul facturării. Fișierul al cărui nume ar putea sugera o legătură, `core/audit_retentie.py`, tratează un subiect complet diferit: retenția datelor cu caracter personal (GDPR), nu retenția contractuală de garanție din construcții.

Concluzie onestă: iConta.eu **nu automatizează** tratamentul retenției de garanție la construcții. Facturarea integrală a lucrării (inclusiv partea reținută) și, dacă e cazul, urmărirea separată a exigibilității TVA pentru firmele la TVA la încasare rămân în sarcina utilizatorului, prin operațiunile obișnuite de facturare și notele contabile manuale.

[iConta.eu](/)
