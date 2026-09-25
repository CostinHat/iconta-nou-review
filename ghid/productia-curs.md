---
title: "Ce fac dacă producția în curs nu a"
description: "Ce se întâmplă dacă producția în curs de execuție nu a fost înregistrată la închiderea perioadei și cum se corectează situația."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă producția în curs nu a

Titlul acestui ghid tratează cea mai frecventă situație legată de producția în curs de execuție: momentul în care ea **nu a fost înregistrată la închiderea perioadei**. Mai jos, ce spune legea despre obligația de constatare și cum se remediază o astfel de omisiune.

## Temeiul legal

::: ghid-temei
„Contul 331 „Produse în curs de execuție" Cu ajutorul acestui cont se ține evidența stocurilor de produse în curs de execuție (care nu au trecut prin toate fazele de prelucrare prevăzute de procesul tehnologic, respectiv producția neterminată) existente la sfârșitul perioadei. [...] În debitul contului 331 [...] se înregistrează: – valoarea la cost de producție a stocului de produse în curs de execuție la sfârșitul perioadei, stabilită pe bază de inventar (711). [...] În creditul contului 331 [...] se înregistrează: – scăderea din gestiune a valorii produselor în curs de execuție la începutul perioadei următoare (711)."
— OMFP 1802/2014, Reglementările contabile, Cap. 16, funcțiunea contului 331 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Ce rezultă din text, aplicat la situația unei omisiuni:

- Constatarea producției în curs la sfârșitul perioadei **nu este opțională** — legea folosește „se înregistrează", nu „se poate înregistra".
- Dacă suma nu a fost înregistrată în luna în care ar fi trebuit, iar eroarea e descoperită ulterior (chiar și în lunile următoare, înainte de închiderea exercițiului financiar), corectarea se face printr-o notă de constatare tardivă (`331 = 711`), la valoarea stabilită pe bază de inventar pentru perioada respectivă.
- Dacă eroarea e descoperită după depunerea situațiilor financiare aferente perioadei, corectarea urmează regulile generale de corectare a erorilor contabile din exerciții încheiate, nu o simplă notă de producție.

## Ce se greșește în practică

- Se sare peste constatarea producției în curs la lunile „mai puțin importante" din an, considerând-o o formalitate — dar ea afectează direct rezultatul lunii (prin contul 711) și valoarea stocurilor din bilanț.
- Se descoperă omisiunea abia la închiderea exercițiului financiar, când corectarea devine mult mai complicată decât o simplă notă lunară.
- Se înregistrează constatarea, dar se omite reluarea ei în luna următoare — ceea ce dublează eronat valoarea stocului de producție în curs.

## Ce face iConta.eu

Din ecranul **Operațiuni speciale → Imobilizări**, operațiunea „Producție (711/345)" permite introducerea oricând, manual, a unei note de constatare a producției în curs (`331 = 711`), cu data pe care o alege contabilul — inclusiv, tehnic, pentru o dată din trecut, dacă exercițiul financiar e încă deschis. Notă onestă: aplicația **nu detectează automat** o lună în care producția în curs ar fi trebuit înregistrată și nu a fost — nu există în cod o verificare sau o alertă de acest tip; recunoașterea omisiunii rămâne responsabilitatea contabilului, aplicația oferind doar mijlocul de a înregistra corect nota, odată identificată nevoia.

[iConta.eu](/)
