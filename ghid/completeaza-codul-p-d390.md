---
title: "Cum se completează codul P în D390?"
description: Codul P identifică prestarea intracomunitară de servicii — spre deosebire de livrarea de bunuri, nu e tipul implicit al aplicației și trebuie completat manual.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se completează codul P în D390?

Codul **P** desemnează prestarea intracomunitară de servicii către un beneficiar dintr-un alt stat membru. Spre deosebire de codul L (livrare de bunuri), care este tipul implicit pentru orice factură emisă intracomunitar, prestarea de servicii nu este dedusă automat — trebuie declarată manual.

## Temeiul legal

::: ghid-temei
**OPANAF 705/2020, Anexa 2, Instrucțiuni pct. 1 lit. d)**:
> „[...] d) prestări intracomunitare de servicii (P) [...]"

**Coloana „Cod operator intracomunitar" pentru P**:
> „în cazul prestărilor intracomunitare de servicii (P) - codul de identificare în scopuri de TVA al persoanei care primeşte serviciile în alt stat membru decât România [...]"
:::

Codul de operator este obligatoriu pentru P: se trece codul de TVA al beneficiarului serviciului, din statul membru în care are locul prestării.

## Ce se greșește în practică

Greșeala tipică este lăsarea nedeclarată a prestărilor de servicii intracomunitare, pentru că aplicația clasifică implicit toate facturile emise intracomunitar ca L (bunuri) — dacă factura reprezintă de fapt un serviciu, e nevoie de o intervenție explicită pentru ca operațiunea să ajungă declarată corect ca P, altfel rămâne raportată greșit ca livrare de bunuri.

## Ce face iConta.eu

Aplicația nu deduce niciodată automat tipul P din facturi — orice factură emisă intracomunitar e clasificată implicit pe L (bunuri). Pentru a raporta corect o prestare de servicii, ai două căi: fie reclasifici din panoul de clasificare D390 (pasul 2) operațiunea auto-derivată din L în P, fie adaugi o linie pur manuală de tip P (cu țara și codul beneficiarului, obligatorii), dacă operațiunea nu corespunde unei facturi individuale din sistem.

**Limitare curentă de reconfirmat**: pentru facturile create prin ecranul dedicat de livrare/achiziție intracomunitară, axa bunuri/servicii înregistrată la creare pare, conform codului verificat, să blocheze efectul reclasificării ulterioare din panoul D390 — dacă factura a fost creată prin acel ecran cu axa „bunuri", reclasificarea în P riscă să nu se reflecte în declarația generată. Pentru facturi emise prin ecranul obișnuit de facturare, reclasificarea funcționează normal. Recomandăm verificarea comportamentului live al aplicației pentru cazul tău concret înainte de a depune declarația.

[iConta.eu](/)
